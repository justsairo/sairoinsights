from __future__ import annotations

import asyncio
import csv
import hashlib
import html
import io
import json
import logging
import math
import os
import re
import secrets
import smtplib
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Annotated, Literal

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile, Depends
from supabase import create_client, Client

load_dotenv()
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

try:
    import feedparser
except ImportError:  # pragma: no cover - handled at runtime for clearer deploy errors
    feedparser = None

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - handled at runtime for clearer deploy errors
    yf = None

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()

supabase: Client | None = None
if STORAGE_BACKEND == "supabase" and SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_ROWS = 100_000
MAX_COLUMNS = 500
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
SAFE_ERROR_MESSAGE = "Something went wrong. Try refreshing the page."


@dataclass
class DatasetRecord:
    frame: pd.DataFrame
    access_token: str


DATASETS: dict[str, DatasetRecord] = {}
USERS: dict[str, str] = {} # Local fallback: email -> password
RATE_LIMITS: dict[str, deque[float]] = defaultdict(deque)
NEWS_AUTOMATION_TASK: asyncio.Task | None = None

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
SAMPLE_DATA = BASE_DIR / "sample_sales.csv"
MAX_ARTICLES_STORED = 2000
ARTICLE_TTL_DAYS = 90
NEWS_AUTOMATION_ENABLED = os.getenv("NEWS_AUTOMATION_ENABLED", "false").lower() == "true"
NEWS_AUTOMATION_HOUR_UTC = int(os.getenv("NEWS_AUTOMATION_HOUR_UTC", "7"))
NEWS_RECIPIENT_EMAIL = os.getenv("NEWS_RECIPIENT_EMAIL", "")
NEWS_SENDER_EMAIL = os.getenv("NEWS_SENDER_EMAIL") or os.getenv("SMTP_USERNAME", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]

RSS_SOURCES = [
    {"url": "https://feeds.reuters.com/reuters/businessNews", "name": "Reuters Business", "category": "markets"},
    {"url": "https://feeds.reuters.com/reuters/topNews", "name": "Reuters Top News", "category": "general"},
    {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg Markets", "category": "markets"},
    {"url": "https://feeds.bloomberg.com/economics/news.rss", "name": "Bloomberg Economics", "category": "macro"},
    {"url": "https://feeds.a.wsj.com/rss/RSSMarketsMain.xml", "name": "WSJ Markets", "category": "markets"},
    {"url": "https://feeds.a.wsj.com/rss/WSJcomUSBusiness.xml", "name": "WSJ Business", "category": "business"},
    {"url": "https://www.ft.com/rss/home", "name": "Financial Times", "category": "macro"},
    {"url": "https://www.economist.com/finance-and-economics/rss.xml", "name": "The Economist Finance", "category": "macro"},
    {"url": "https://www.economist.com/the-world-this-week/rss.xml", "name": "The Economist World", "category": "general"},
]

MARKET_SYMBOLS = {
    "sp500": "^GSPC",
    "nasdaq": "^IXIC",
    "ftse100": "^FTSE",
    "dax": "^GDAXI",
    "eur_usd": "EURUSD=X",
    "gbp_usd": "GBPUSD=X",
    "usd_jpy": "USDJPY=X",
    "us_10y_yield": "^TNX",
    "us_2y_yield": "^IRX",
    "gold_usd": "GC=F",
    "wti_oil": "CL=F",
    "brent_oil": "BZ=F",
}

NEWS_CSV_COLUMNS = [
    "timestamp",
    "pub_date",
    "source",
    "category",
    "headline",
    "summary",
    "url",
    *MARKET_SYMBOLS.keys(),
]


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        for key in ("method", "path", "status_code", "duration_ms", "client_ip", "event"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
logger = logging.getLogger("sairoinsights")

app = FastAPI(title="Sairo Insights API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CleanRequest(BaseModel):
    dataset_id: str
    missing: Literal["none", "mean", "median", "mode", "drop"] = "none"
    remove_duplicates: bool = False
    outlier_method: Literal["none", "iqr", "zscore"] = "none"


class AnalyzeRequest(BaseModel):
    dataset_id: str
    analysis_type: Literal[
        "describe", 
        "correlation", 
        "groupby", 
        "regression", 
        "ttest", 
        "anova", 
        "normality", 
        "moving_average"
    ]
    x: str | None = None
    y: str | None = None
    group_by: str | None = None
    value: str | None = None
    aggregation: Literal["mean", "sum", "count", "median", "min", "max", "pearson", "spearman"] = "mean"
    window: int = Field(default=7, ge=2, le=365)  # For moving averages


class ChartRequest(BaseModel):
    dataset_id: str
    chart_type: Literal["auto", "bar", "line", "scatter", "histogram", "box"]
    x: str | None = None
    y: str | None = None


class NewsCollectRequest(BaseModel):
    days_for_csv: int = Field(default=7, ge=1, le=90)
    send_email: bool = False


class NewsCollectResponse(BaseModel):
    status: str
    articles_collected: int
    articles_stored: int
    sources_succeeded: int
    sources_failed: int
    market_snapshot: dict[str, Any]
    email_sent: bool


@app.middleware("http")
async def rate_limit_and_log(request: Request, call_next):
    start = time.perf_counter()
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{request.url.path}"
    now = time.monotonic()
    hits = RATE_LIMITS[key]
    while hits and now - hits[0] > RATE_LIMIT_WINDOW_SECONDS:
        hits.popleft()
    if request.url.path.startswith("/api/") and len(hits) >= RATE_LIMIT_MAX_REQUESTS:
        logger.warning(
            "rate_limit_exceeded",
            extra={"event": "rate_limit_exceeded", "method": request.method, "path": request.url.path, "client_ip": client_ip},
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please wait and try again."},
            headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
        )
    hits.append(now)

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    level = logging.ERROR if response.status_code >= 500 else logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        level,
        "request_completed",
        extra={
            "event": "request_completed",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        },
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_error", extra={"event": "validation_error", "method": request.method, "path": request.url.path})
    return JSONResponse(status_code=422, content={"detail": "Invalid request. Check your inputs and try again."})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    public_messages = {
        400: exc.detail,
        401: "Unauthorized.",
        403: "You do not have access to this dataset.",
        404: "Not found.",
        413: exc.detail,
        429: "Too many requests. Please wait and try again.",
    }
    return JSONResponse(status_code=exc.status_code, content={"detail": public_messages.get(exc.status_code, SAFE_ERROR_MESSAGE)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"UNHANDLED EXCEPTION: {exc}")
    traceback.print_exc()
    logger.exception("unhandled_exception", extra={"event": "unhandled_exception", "method": request.method, "path": request.url.path})
    return JSONResponse(status_code=500, content={"detail": SAFE_ERROR_MESSAGE})


def json_safe(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return json_safe(value.item())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def summarize_frame(df: pd.DataFrame, dataset_id: str, dataset_token: str | None = None) -> dict[str, Any]:
    summary = {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isna().sum().to_dict(),
        "preview": df.head(10).to_dict(orient="records"),
        "numeric_columns": list(df.select_dtypes(include=np.number).columns),
        "categorical_columns": list(df.select_dtypes(exclude=np.number).columns),
    }
    if dataset_token:
        summary["dataset_token"] = dataset_token
    return json_safe(summary)


def new_dataset_token() -> str:
    return secrets.token_urlsafe(32)


def store_dataset(df: pd.DataFrame, user_id: str, access_token: str | None = None) -> tuple[str, str]:
    dataset_id = str(uuid.uuid4())
    dataset_token = access_token or new_dataset_token()

    if STORAGE_BACKEND == "supabase" and supabase:
        try:
            csv_data = df.to_csv(index=False).encode("utf-8")
            # 1. Upload to Storage (bucket: datasets)
            supabase.storage.from_("datasets").upload(f"{user_id}/{dataset_id}.csv", csv_data, {"content-type": "text/csv"})
            # 2. Store metadata in DB (table: datasets)
            supabase.table("datasets").insert({
                "id": dataset_id,
                "user_id": user_id,
                "token": dataset_token
            }).execute()
            return dataset_id, dataset_token
        except Exception as e:
            logger.error(f"supabase_storage_error: {e}")
            # Fallback to local in-memory if supabase fails

    DATASETS[dataset_id] = DatasetRecord(frame=df, access_token=dataset_token)
    return dataset_id, dataset_token


def get_dataset(dataset_id: str, user_id: str, dataset_token: str | None) -> pd.DataFrame:
    if STORAGE_BACKEND == "supabase" and supabase:
        try:
            # 1. Verify token and user_id in DB
            res = supabase.table("datasets").select("token").eq("id", dataset_id).eq("user_id", user_id).single().execute()
            if not res or not res.data or not secrets.compare_digest(dataset_token or "", res.data.get("token", "")):
                 raise HTTPException(status_code=403, detail="You do not have access to this dataset")
            
            # 2. Download from Storage
            file_data = supabase.storage.from_("datasets").download(f"{user_id}/{dataset_id}.csv")
            return pd.read_csv(io.BytesIO(file_data))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"supabase_retrieval_error: {e}")
            # Try fallback to in-memory

    record = DATASETS.get(dataset_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not dataset_token or not secrets.compare_digest(dataset_token, record.access_token):
        raise HTTPException(status_code=403, detail="You do not have access to this dataset")
    return record.frame.copy()


def get_dataset_record(dataset_id: str) -> DatasetRecord:
    record = DATASETS.get(dataset_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return record


def validate_dataset_size(df: pd.DataFrame) -> None:
    if df.empty or len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    if len(df) > MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"Dataset has too many rows. Maximum is {MAX_ROWS}.")
    if len(df.columns) > MAX_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Dataset has too many columns. Maximum is {MAX_COLUMNS}.")


def require_columns(df: pd.DataFrame, *columns: str | None) -> None:
    missing = [col for col in columns if col and col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail="Select valid dataset columns")


def scalarize_nested(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(json_safe(value), ensure_ascii=False, sort_keys=True)
    return value


def scalarize_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df.map(scalarize_nested)


def numeric_series_or_400(series: pd.Series, column: str) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        raise HTTPException(status_code=400, detail=f"{column} must contain numeric values")
    return numeric


def frame_from_json_document(document: Any) -> pd.DataFrame:
    if isinstance(document, list):
        if not document:
            return pd.DataFrame()
        if all(isinstance(item, dict) for item in document):
            return pd.json_normalize(document, sep=".")
        if all(isinstance(item, list) for item in document):
            return pd.DataFrame(document)
        return pd.DataFrame({"value": document})

    if isinstance(document, dict):
        array_items = {key: value for key, value in document.items() if isinstance(value, list)}
        if len(array_items) == 1:
            key, value = next(iter(array_items.items()))
            scalar_items = {item_key: item_value for item_key, item_value in document.items() if item_key != key}
            is_dataset_wrapper = not scalar_items or key.lower() in {"data", "records", "rows", "items", "results"}
            if not is_dataset_wrapper:
                return pd.json_normalize(document, sep=".")
            if all(isinstance(item, dict) for item in value):
                rows = []
                for item in value:
                    row = dict(item)
                    row.update(scalar_items)
                    rows.append(row)
                return pd.json_normalize(rows, sep=".")
            if all(isinstance(item, list) for item in value):
                df = pd.DataFrame(value)
            else:
                df = pd.DataFrame({key: value})
            for scalar_key, scalar_value in scalar_items.items():
                df[scalar_key] = scalar_value
            return df

        if array_items and all(len(value) == len(next(iter(array_items.values()))) for value in array_items.values()):
            rows = []
            scalar_items = {key: value for key, value in document.items() if not isinstance(value, list)}
            for index in range(len(next(iter(array_items.values())))):
                row = {key: value[index] for key, value in array_items.items()}
                row.update(scalar_items)
                rows.append(row)
            return pd.json_normalize(rows, sep=".")

        return pd.json_normalize(document, sep=".")

    return pd.DataFrame({"value": [document]})


def parse_json_upload(data: bytes) -> pd.DataFrame:
    text = data.decode("utf-8-sig")
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        document = rows
    return scalarize_frame(frame_from_json_document(document))


def parse_upload(upload: UploadFile, data: bytes) -> pd.DataFrame:
    filename = upload.filename or "unknown_file"
    suffix = Path(filename).suffix.lower()
    
    # 1. Targeted parsing based on extension hint
    try:
        if suffix == ".csv":
            return pd.read_csv(io.BytesIO(data))
        if suffix == ".tsv":
            return pd.read_csv(io.BytesIO(data), sep="\t")
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(io.BytesIO(data))
        if suffix == ".json":
            return parse_json_upload(data)
    except Exception:
        pass # Fallback to sniffing if extension-based attempt fails

    # 2. Polymorphic Sniffing (order: JSON -> CSV/Delimited -> Excel)
    # Try JSON sniffing
    try:
        return parse_json_upload(data)
    except Exception:
        pass

    # Try CSV/Delimited auto-detection
    try:
        # sep=None with engine='python' triggers delimiter sniffing
        df = pd.read_csv(io.BytesIO(data), sep=None, engine='python', on_bad_lines='skip')
        # If it found more than one column, it's likely a valid tabular structure
        if not df.empty and len(df.columns) > 1:
            return df
    except Exception:
        pass

    # Try Excel (signature based)
    try:
        return pd.read_excel(io.BytesIO(data))
    except Exception:
        pass

    # 3. Last Resort: Plain Text Line Extraction
    try:
        text = data.decode("utf-8", errors="replace")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            return pd.DataFrame({"content": lines})
    except Exception:
        pass

    raise HTTPException(
        status_code=400, 
        detail=f"The file '{filename}' could not be interpreted as data. Please ensure it contains text or tabular information."
    )


def coerce_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col) for col in out.columns]
    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].map(scalarize_nested)
            try:
                out[col] = pd.to_numeric(out[col])
            except (TypeError, ValueError):
                pass
    return out


def require_news_admin(authorization: str | None) -> None:
    if not ADMIN_API_KEY:
        return
    expected = f"Bearer {ADMIN_API_KEY}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def clean_html_text(text: str) -> str:
    stripped = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(stripped)).strip()[:800]


def csv_safe(value: Any) -> str:
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(("=", "+", "-", "@")) else text


def parse_single_feed(source: dict[str, str]) -> list[dict[str, Any]]:
    if feedparser is None:
        raise RuntimeError("feedparser is not installed")
    feed = feedparser.parse(source["url"])
    articles: list[dict[str, Any]] = []
    now_ts = datetime.now(timezone.utc).isoformat()

    for entry in feed.entries[:15]:
        url = entry.get("link", "")
        if not url:
            continue
        pub_date = now_ts
        if getattr(entry, "published_parsed", None):
            try:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass
        title = clean_html_text(entry.get("title", ""))
        if not title:
            continue
        articles.append(
            {
                "id": url_hash(url),
                "timestamp": now_ts,
                "pub_date": pub_date,
                "source": source["name"],
                "category": source["category"],
                "headline": title,
                "summary": clean_html_text(entry.get("summary", entry.get("description", ""))),
                "url": url,
            }
        )
    return articles


async def fetch_all_rss() -> tuple[list[dict[str, Any]], int, int]:
    tasks = [asyncio.to_thread(parse_single_feed, src) for src in RSS_SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    articles: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning("rss_feed_failed", extra={"event": "rss_feed_failed"})
            failed += 1
            continue
        articles.extend(result)
        succeeded += 1
        logger.info("rss_feed_fetched", extra={"event": "rss_feed_fetched"})
    return articles, succeeded, failed


def fetch_market_value(symbol: str) -> float | None:
    if yf is None:
        raise RuntimeError("yfinance is not installed")
    try:
        history = yf.Ticker(symbol).history(period="2d", interval="1d", auto_adjust=False)
        if history.empty:
            return None
        value = history["Close"].dropna().iloc[-1]
        return None if pd.isna(value) else float(value)
    except Exception:
        return None


async def fetch_market_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat()}
    tasks = {field: asyncio.to_thread(fetch_market_value, symbol) for field, symbol in MARKET_SYMBOLS.items()}
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for field, result in zip(tasks.keys(), results):
        snapshot[field] = None if isinstance(result, Exception) else result
    found = sum(1 for key, value in snapshot.items() if key != "timestamp" and value is not None)
    logger.info("market_snapshot_fetched", extra={"event": "market_snapshot_fetched", "status_code": found})
    return snapshot


async def read_articles_sync() -> list[dict[str, Any]]:
    if not supabase:
        logger.warning("supabase_not_configured", extra={"event": "read_articles_sync_skipped"})
        return []
    try:
        res = supabase.table("news_articles").select("*").order("timestamp", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"supabase_read_articles_error: {e}")
        return []


async def write_articles_sync(articles: list[dict[str, Any]]) -> None:
    if not supabase:
        logger.warning("supabase_not_configured", extra={"event": "write_articles_sync_skipped"})
        return
    try:
        # Supabase upsert (insert or update on conflict)
        # Note: The 'id' field is used for conflict resolution
        res = supabase.table("news_articles").upsert(articles, on_conflict="id").execute()
        if res.data:
            logger.info(f"supabase_upsert_articles_success: {len(res.data)} articles upserted.")
        else:
            logger.warning("supabase_upsert_articles_no_data: No data returned from upsert.")
    except Exception as e:
        logger.error(f"supabase_write_articles_error: {e}")


async def store_news_articles(articles: list[dict[str, Any]], market: dict[str, Any]) -> int:
    if not supabase:
        logger.warning("supabase_not_configured", extra={"event": "store_news_articles_skipped"})
        return 0

    existing_res = await supabase.table("news_articles").select("id").execute()
    existing_ids = {item["id"] for item in existing_res.data} if existing_res.data else set()

    stored_articles = []
    market_fields = {key: value for key, value in market.items() if key != "timestamp"}
    for article in articles:
        if article["id"] not in existing_ids:
            stored_articles.append({**article, **market_fields})

    if stored_articles:
        await write_articles_sync(stored_articles)

    # Store market snapshot
    try:
        await supabase.table("market_snapshots").insert(market).execute()
        logger.info("supabase_market_snapshot_stored", extra={"event": "market_snapshot_stored", "timestamp": market.get("timestamp")})
    except Exception as e:
        logger.error(f"supabase_store_market_snapshot_error: {e}")

    return len(stored_articles)


async def load_news_articles(days: int = 7) -> list[dict[str, Any]]:
    if days < 1 or days > 90:
        raise HTTPException(status_code=400, detail="days must be between 1 and 90")
    if not supabase:
        logger.warning("supabase_not_configured", extra={"event": "load_news_articles_skipped"})
        return []
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    try:
        res = supabase.table("news_articles").select("*").gte("pub_date", cutoff).order("timestamp", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"supabase_load_news_articles_error: {e}")
        return []


async def load_market_snapshot_sync() -> dict[str, Any]:
    if not supabase:
        logger.warning("supabase_not_configured", extra={"event": "load_market_snapshot_sync_skipped"})
        return {}
    try:
        res = supabase.table("market_snapshots").select("*").order("timestamp", desc=True).limit(1).single().execute()
        return res.data if res.data else {}
    except Exception as e:
        logger.error(f"supabase_load_market_snapshot_error: {e}")
        return {}


def generate_news_csv(articles: list[dict[str, Any]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=NEWS_CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for article in articles:
        writer.writerow({column: csv_safe(article.get(column, "")) for column in NEWS_CSV_COLUMNS})
    return buffer.getvalue().encode("utf-8")


def build_digest_email(articles: list[dict[str, Any]], market: dict[str, Any], days: int) -> str:
    today = date.today().strftime("%B %d, %Y")
    date_from = (date.today() - timedelta(days=days)).strftime("%b %d")

    def fmt_num(value: Any) -> str:
        if value is None:
            return ""
        try:
            return f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return html.escape(str(value), quote=True)

    market_rows = "".join(
        f"<tr><td>{html.escape(field.replace('_', ' ').title())}</td><td style='text-align:right'>{fmt_num(market.get(field))}</td></tr>"
        for field in MARKET_SYMBOLS
    )

    by_source: dict[str, list[dict[str, Any]]] = {}
    for article in articles[:120]:
        by_source.setdefault(str(article.get("source", "Unknown")), []).append(article)

    sections = ""
    for source, source_articles in by_source.items():
        items = ""
        for article in source_articles[:5]:
            headline = html.escape(str(article.get("headline", "")), quote=True)
            url = html.escape(str(article.get("url", "#")), quote=True)
            summary = html.escape(str(article.get("summary", ""))[:220], quote=True)
            pub_date = html.escape(str(article.get("pub_date", ""))[:10], quote=True)
            items += (
                "<div style='padding:10px 0;border-bottom:1px solid #e5e7eb'>"
                f"<a href='{url}' style='color:#1d4ed8;font-weight:600;text-decoration:none'>{headline}</a>"
                f"<p style='color:#4b5563;font-size:12px'>{summary}</p>"
                f"<p style='color:#9ca3af;font-size:11px'>{pub_date}</p>"
                "</div>"
            )
        safe_source = html.escape(source, quote=True)
        sections += f"<h3 style='color:#374151'>{safe_source} - {len(source_articles)} articles</h3>{items}"

    return f"""<!doctype html>
<html><body style="margin:0;background:#f3f4f6;font-family:Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px">
<table width="680" cellpadding="0" cellspacing="0" style="background:white;border-radius:10px;overflow:hidden">
<tr><td style="background:#1e40af;color:white;padding:24px">
<h1 style="margin:0;font-size:22px">Financial News & Market Digest</h1>
<p style="margin:8px 0 0;color:#dbeafe">{html.escape(date_from)} - {html.escape(today)} | {len(articles)} articles</p>
</td></tr>
<tr><td style="padding:24px">
<h2 style="font-size:14px;text-transform:uppercase;color:#374151">Live Market Snapshot</h2>
<table width="100%" cellpadding="6" cellspacing="0" style="border:1px solid #e5e7eb">{market_rows}</table>
<h2 style="font-size:14px;text-transform:uppercase;color:#374151;margin-top:24px">Headlines</h2>
{sections or "<p>No articles collected yet.</p>"}
</td></tr>
</table>
</td></tr></table>
</body></html>"""


def smtp_configured() -> bool:
    return all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, NEWS_RECIPIENT_EMAIL, NEWS_SENDER_EMAIL])


def send_email_sync(subject: str, html_body: str, csv_bytes: bytes | None = None, filename: str = "financial_news.csv") -> bool:
    if not smtp_configured():
        logger.warning("smtp_not_configured", extra={"event": "smtp_not_configured"})
        return False
    message = MIMEMultipart()
    message["From"] = NEWS_SENDER_EMAIL
    message["To"] = NEWS_RECIPIENT_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html", "utf-8"))
    if csv_bytes:
        attachment = MIMEApplication(csv_bytes, _subtype="csv")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(attachment)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)
    return True


async def send_digest_email(articles: list[dict[str, Any]], market: dict[str, Any], days: int) -> bool:
    subject = f"Financial News & Market Digest - {date.today().strftime('%b %d, %Y')}"
    html_body = build_digest_email(articles, market, days)
    csv_bytes = await asyncio.to_thread(generate_news_csv, articles)
    try:
        return await asyncio.to_thread(send_email_sync, subject, html_body, csv_bytes, f"financial_news_{days}d.csv")
    except Exception:
        logger.exception("digest_email_failed", extra={"event": "digest_email_failed"})
        return False


async def run_news_collection(days_for_csv: int = 7, send_email: bool = False) -> NewsCollectResponse:
    if days_for_csv < 1 or days_for_csv > 90:
        raise HTTPException(status_code=400, detail="days_for_csv must be between 1 and 90")
    logger.info("news_collection_started", extra={"event": "news_collection_started"})
    rss_articles, succeeded, failed = await fetch_all_rss()
    market = await fetch_market_snapshot()
    stored = await store_news_articles(rss_articles, market)
    email_sent = False
    if send_email:
        recent = await load_news_articles(days_for_csv)
        email_sent = await send_digest_email(recent, market, days_for_csv)
    logger.info("news_collection_completed", extra={"event": "news_collection_completed", "status_code": stored})
    return NewsCollectResponse(
        status="ok",
        articles_collected=len(rss_articles),
        articles_stored=stored,
        sources_succeeded=succeeded,
        sources_failed=failed,
        market_snapshot={key: value for key, value in market.items() if key != "timestamp"},
        email_sent=email_sent,
    )


async def news_automation_loop() -> None:
    last_run: date | None = None
    while True:
        now = datetime.now(timezone.utc)
        if now.hour >= NEWS_AUTOMATION_HOUR_UTC and last_run != now.date():
            try:
                await run_news_collection(days_for_csv=7, send_email=False)
                last_run = now.date()
            except Exception:
                logger.exception("news_automation_failed", extra={"event": "news_automation_failed"})
        await asyncio.sleep(1800)


@app.on_event("startup")
async def start_news_automation() -> None:
    global NEWS_AUTOMATION_TASK
    if NEWS_AUTOMATION_ENABLED and NEWS_AUTOMATION_TASK is None:
        NEWS_AUTOMATION_TASK = asyncio.create_task(news_automation_loop())


@app.on_event("shutdown")
async def stop_news_automation() -> None:
    if NEWS_AUTOMATION_TASK:
        NEWS_AUTOMATION_TASK.cancel()


@app.get("/api/config")
def get_config() -> dict[str, Any]:
    return {
        "n8n_url": os.getenv("N8N_URL", "http://localhost:5678"),
        "automation_enabled": bool(ADMIN_API_KEY),
        "supabase_enabled": bool(supabase),
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", ""),
    }


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
async def signup(request: SignupRequest) -> dict[str, Any]:
    """Sign up with Supabase auth (or local fallback)."""
    print(f"DEBUG: signup called for {request.email}")
    if not supabase:
        print("DEBUG: Using local auth for signup")
        if request.email in USERS:
            raise HTTPException(status_code=400, detail="User already exists")
        USERS[request.email] = request.password
        return {
            "user": {"id": "local", "email": request.email},
            "session": {"access_token": f"local_token_{request.email}"},
            "message": "Signup successful (Local Mode)."
        }
    try:
        print("DEBUG: Using Supabase auth for signup")
        response = supabase.auth.sign_up({"email": request.email, "password": request.password})
        return {
            "user": {"id": response.user.id, "email": response.user.email} if response.user else None,
            "session": {"access_token": response.session.access_token} if response.session else None,
            "message": "Signup successful. Please check your email for confirmation."
        }
    except Exception as error:
        logger.error(f"signup_error: {error}")
        raise HTTPException(status_code=400, detail="Signup failed. Email may already exist.")


@app.post("/api/auth/login")
async def login(request: LoginRequest) -> dict[str, Any]:
    """Login with Supabase auth (or local fallback)."""
    print(f"DEBUG: login called for {request.email}")
    if not supabase:
        print("DEBUG: Using local auth for login")
        if request.email not in USERS or USERS[request.email] != request.password:
            print(f"DEBUG: Login failed for {request.email}. User in USERS: {request.email in USERS}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "user": {"id": "local", "email": request.email},
            "session": {"access_token": f"local_token_{request.email}", "refresh_token": "local_refresh_token"},
        }
    try:
        print("DEBUG: Using Supabase auth for login")
        response = supabase.auth.sign_in_with_password({"email": request.email, "password": request.password})
        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "user": {"id": response.user.id, "email": response.user.email},
            "session": {"access_token": response.session.access_token, "refresh_token": response.session.refresh_token},
        }
    except Exception as error:
        logger.error(f"login_error: {error}")
        raise HTTPException(status_code=401, detail="Login failed. Check your email and password.")


@app.post("/api/auth/logout")
async def logout() -> dict[str, str]:
    """Logout (frontend handles token removal)."""
    return {"status": "logged out"}

async def get_current_user_id(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.replace("Bearer ", "")
    if not supabase:
        if token.startswith("local_token_"): # Local fallback for development
            return "local_user_id"
        raise HTTPException(status_code=401, detail="Supabase not configured, cannot verify token")
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            return user.user.id
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/api/auth/verify")
async def verify_token(user_id: Annotated[str, Depends(get_current_user_id)]) -> dict[str, Any]:
    """Verify JWT token and return user info."""
    return {"user": {"id": user_id, "email": "verified_email@example.com"}} # Email is placeholder for now


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sample")
def load_sample(user_id: Annotated[str, Depends(get_current_user_id)]) -> dict[str, Any]:
    df = pd.read_csv(SAMPLE_DATA)
    stored_df = coerce_columns(df)
    dataset_id, dataset_token = store_dataset(stored_df, user_id)
    return summarize_frame(stored_df, dataset_id, dataset_token)


@app.post("/api/upload")
async def upload_dataset(
    user_id: Annotated[str, Depends(get_current_user_id)],
    file: UploadFile = File(...)
) -> dict[str, Any]:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 50MB limit")
    df = coerce_columns(parse_upload(file, data))
    validate_dataset_size(df)
    dataset_id, dataset_token = store_dataset(df, user_id)
    logger.info("dataset_uploaded", extra={"event": "dataset_uploaded"})
    return summarize_frame(df, dataset_id, dataset_token)


@app.post("/api/clean")
def clean_dataset(
    request: CleanRequest, 
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    record = get_dataset_record(request.dataset_id)
    df = get_dataset(request.dataset_id, user_id, x_dataset_token)
    before = {"rows": len(df), "missing": int(df.isna().sum().sum()), "duplicates": int(df.duplicated().sum())}

    if request.remove_duplicates:
        df = df.drop_duplicates()

    numeric_cols = list(df.select_dtypes(include=np.number).columns)
    for col in df.columns:
        if request.missing == "drop":
            continue
        if df[col].isna().any():
            if request.missing == "mean" and col in numeric_cols:
                df[col] = df[col].fillna(df[col].mean())
            elif request.missing == "median" and col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())
            elif request.missing == "mode":
                mode = df[col].mode(dropna=True)
                if not mode.empty:
                    df[col] = df[col].fillna(mode.iloc[0])
    if request.missing == "drop":
        df = df.dropna()

    if request.outlier_method in {"iqr", "zscore"} and numeric_cols:
        mask = pd.Series(True, index=df.index)
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            if request.outlier_method == "iqr":
                q1, q3 = series.quantile([0.25, 0.75])
                iqr = q3 - q1
                mask &= df[col].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr) | df[col].isna()
            else:
                z = np.abs(stats.zscore(df[col], nan_policy="omit"))
                mask &= pd.Series(z < 3, index=df.index).fillna(True)
        df = df[mask]

    cleaned_id, _ = store_dataset(df, user_id, access_token=record.access_token)
    after = {"rows": len(df), "missing": int(df.isna().sum().sum()), "duplicates": int(df.duplicated().sum())}
    result = summarize_frame(df, cleaned_id, record.access_token)
    result["before"] = before
    result["after"] = after
    return result


@app.post("/api/analyze")
def analyze(
    request: AnalyzeRequest, 
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    df = get_dataset(request.dataset_id, user_id, x_dataset_token)
    numeric = list(df.select_dtypes(include=np.number).columns)

    if request.analysis_type == "describe":
        return json_safe({"type": "describe", "result": df[numeric].describe().T.reset_index().to_dict(orient="records")})
    if request.analysis_type == "correlation":
        method = "spearman" if request.aggregation == "spearman" else "pearson"
        return json_safe({"type": "correlation", "method": method, "result": df[numeric].corr(method=method).to_dict()})
    if request.analysis_type == "groupby":
        if not request.group_by or not request.value:
            raise HTTPException(status_code=400, detail="Select group and value columns")
        require_columns(df, request.group_by, request.value)
        if request.aggregation in {"pearson", "spearman"}:
            raise HTTPException(status_code=400, detail="Select a valid group-by aggregation")
        grouped_df = df[[request.group_by, request.value]].copy()
        grouped_df[request.group_by] = grouped_df[request.group_by].map(scalarize_nested)
        if request.aggregation == "count":
            grouped = grouped_df.groupby(request.group_by, dropna=False)[request.value].count().reset_index()
        else:
            grouped_df[request.value] = numeric_series_or_400(grouped_df[request.value], request.value)
            grouped = getattr(grouped_df.groupby(request.group_by, dropna=False)[request.value], request.aggregation)().reset_index()
        return json_safe({"type": "groupby", "result": grouped.to_dict(orient="records")})
    if request.analysis_type == "regression":
        if not request.x or not request.y:
            raise HTTPException(status_code=400, detail="Select X and Y columns")
        require_columns(df, request.x, request.y)
        if request.x not in numeric or request.y not in numeric:
            raise HTTPException(status_code=400, detail="Regression requires numeric X and Y columns")
        model_df = df[[request.x, request.y]].dropna()
        if len(model_df) < 2:
            raise HTTPException(status_code=400, detail="Need at least two valid rows")
        x_values = model_df[[request.x]].to_numpy()
        y_values = model_df[request.y].to_numpy()
        model = LinearRegression().fit(x_values, y_values)
        predictions = model.predict(x_values)
        return json_safe(
            {
                "type": "regression",
                "coefficient": float(model.coef_[0]),
                "intercept": float(model.intercept_),
                "r2": float(r2_score(y_values, predictions)),
            }
        )
    if request.analysis_type == "ttest":
        if not request.x or not request.y:
            raise HTTPException(status_code=400, detail="Select two numeric columns for T-Test")
        require_columns(df, request.x, request.y)
        s1, s2 = df[request.x].dropna(), df[request.y].dropna()
        res = stats.ttest_ind(s1, s2)
        return json_safe({"type": "ttest", "t_statistic": float(res.statistic), "p_value": float(res.pvalue), "significant": bool(res.pvalue < 0.05)})
    
    if request.analysis_type == "anova":
        if not request.group_by or not request.value:
            raise HTTPException(status_code=400, detail="Select group and value columns for ANOVA")
        require_columns(df, request.group_by, request.value)
        groups = [group[request.value].dropna() for _, group in df.groupby(request.group_by)]
        if len(groups) < 2:
            raise HTTPException(status_code=400, detail="ANOVA requires at least two groups")
        res = stats.f_oneway(*groups)
        return json_safe({"type": "anova", "f_statistic": float(res.statistic), "p_value": float(res.pvalue), "significant": bool(res.pvalue < 0.05)})

    if request.analysis_type == "normality":
        if not request.value:
            raise HTTPException(status_code=400, detail="Select a column for normality test")
        require_columns(df, request.value)
        series = df[request.value].dropna()
        if len(series) < 3:
             raise HTTPException(status_code=400, detail="Need at least 3 samples for normality test")
        res = stats.shapiro(series)
        return json_safe({"type": "normality", "statistic": float(res.statistic), "p_value": float(res.pvalue), "is_normal": bool(res.pvalue > 0.05)})

    if request.analysis_type == "moving_average":
        if not request.value:
            raise HTTPException(status_code=400, detail="Select a column for moving average")
        require_columns(df, request.value)
        ma = df[request.value].rolling(window=request.window).mean()
        return json_safe({"type": "moving_average", "result": ma.dropna().tolist()})

    raise HTTPException(status_code=400, detail="Unsupported analysis type")


@app.post("/api/chart")
def chart(
    request: ChartRequest, 
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    df = get_dataset(request.dataset_id, user_id, x_dataset_token)
    cols = [col for col in [request.x, request.y] if col]
    if not cols:
        raise HTTPException(status_code=400, detail="Select at least one chart column")
    require_columns(df, *cols)
    data = df[cols].dropna().head(5000).to_dict(orient="records")
    suggestion = "histogram"
    if request.x and request.y:
        x_numeric = pd.api.types.is_numeric_dtype(df[request.x])
        y_numeric = pd.api.types.is_numeric_dtype(df[request.y])
        suggestion = "scatter" if x_numeric and y_numeric else "bar"
    return json_safe({"chart_type": request.chart_type or suggestion, "suggestion": suggestion, "data": data})


@app.get("/api/insights/{dataset_id}")
def insights(
    dataset_id: str, 
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    df = get_dataset(dataset_id, user_id, x_dataset_token)
    numeric = list(df.select_dtypes(include=np.number).columns)
    items: list[str] = []
    if df.isna().sum().sum():
        worst = df.isna().sum().sort_values(ascending=False).index[0]
        items.append(f"{worst} has the most missing values.")
    if df.duplicated().sum():
        items.append(f"{int(df.duplicated().sum())} duplicate rows were detected.")
    if len(numeric) >= 2:
        corr = df[numeric].corr().abs()
        pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
        strong = pairs[pairs > 0.7].sort_values(ascending=False)
        if len(strong) > 0:
            first = strong.index[0]
            items.append(f"{first[0]} and {first[1]} have a strong correlation ({strong.iloc[0]:.2f}).")
    for col in numeric[:4]:
        series = df[col].dropna()
        if len(series) > 3:
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)]
            if len(outliers):
                items.append(f"{col} contains {len(outliers)} potential outliers by IQR.")
    if not items:
        items.append("No major data quality or correlation issues stood out in this dataset.")
    return {"insights": items[:6]}


class ExportCompleteReportRequest(BaseModel):
    dataset_id: str
    recipient_email: str
    include_cleaned_csv: bool = True
    include_analysis: bool = True
    include_insights: bool = True
    include_news: bool = True
    subject: str = "Sairo Insights - Complete Analysis Report"


async def generate_complete_report(
    dataset_id: str, 
    analysis: dict[str, Any] | None,
    insights: list[str] | None,
    news_articles: list[dict] | None,
    cleaned_csv_bytes: bytes | None
) -> bytes:
    """Generate a comprehensive HTML report with all analysis outputs."""
    from datetime import datetime
    
    html_parts = [
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
                .section {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .section h2 {{ color: #667eea; margin-top: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f0f0f0; font-weight: 600; }}
                .insight {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 10px 0; border-radius: 4px; }}
                .news-item {{ background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 12px; margin: 8px 0; border-radius: 4px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Sairo Insights Analysis Report</h1>
                <p>Dataset: <strong>{dataset_id[:12]}...</strong></p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        """
    ]
    
    if analysis:
        html_parts.append("""
            <div class="section">
                <h2>📈 Analysis Results</h2>
        """)
        if isinstance(analysis, dict):
            for key, value in analysis.items():
                if key not in ["dataset_id", "dataset_token"]:
                    if isinstance(value, dict):
                        html_parts.append(f"<p><strong>{key}:</strong></p><pre>{json.dumps(value, indent=2)[:500]}</pre>")
                    else:
                        html_parts.append(f"<p><strong>{key}:</strong> {value}</p>")
        html_parts.append("</div>")
    
    if insights:
        html_parts.append("""
            <div class="section">
                <h2>💡 Generated Insights</h2>
        """)
        for insight in insights:
            html_parts.append(f'<div class="insight">{html.escape(insight)}</div>')
        html_parts.append("</div>")
    
    if news_articles:
        html_parts.append(f"""
            <div class="section">
                <h2>📰 Latest News ({len(news_articles)} articles)</h2>
        """)
        for article in news_articles[:10]:
            title = html.escape(article.get("title", "Untitled"))
            source = html.escape(article.get("source", "Unknown"))
            html_parts.append(f'<div class="news-item"><strong>{title}</strong><br/><small>{source}</small></div>')
        html_parts.append("</div>")
    
    html_parts.append("""
            <div class="footer">
                <p>Sairo Insights — Local Data Analysis & Automation</p>
            </div>
        </body>
        </html>
    """)
    
    return "".join(html_parts).encode("utf-8")


@app.post("/api/export-report-gmail")
async def export_and_send_report(
    request: ExportCompleteReportRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """Export cleaned data, analysis, insights, and news — send comprehensive report via Gmail."""
    df = get_dataset(request.dataset_id, user_id, x_dataset_token)
    
    # Get cleaned CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    cleaned_csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    # Prepare analysis/insights/news (would be passed from frontend in real scenario)
    analysis = None
    insights = []
    news_articles = []
    
    # Generate comprehensive HTML report
    html_report = await generate_complete_report(
        request.dataset_id,
        analysis,
        insights,
        news_articles,
        cleaned_csv_bytes
    )
    
    # Send via Gmail with attachments
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from email.mime.base import MIMEBase
        from email import encoders
        import base64
        import zipfile
        
        gmail_service_account = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON")
        if not gmail_service_account:
            raise HTTPException(status_code=500, detail="Gmail not configured")
        
        try:
            sa_info = json.loads(gmail_service_account)
        except json.JSONDecodeError:
            sa_info = json.loads(Path(gmail_service_account).read_text())
        
        creds = Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/gmail.send"])
        service = build("gmail", "v1", credentials=creds)
        
        # Create ZIP with all files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            if request.include_cleaned_csv:
                zf.writestr(f"cleaned_data_{request.dataset_id[:8]}.csv", cleaned_csv_bytes)
            zf.writestr(f"analysis_report_{request.dataset_id[:8]}.html", html_report)
        
        zip_bytes = zip_buffer.getvalue()
        
        msg = MIMEMultipart()
        msg["to"] = request.recipient_email
        msg["subject"] = request.subject
        msg.attach(MIMEText("Your complete analysis report is attached.\n\nThe ZIP file contains cleaned data and comprehensive analysis report.", "plain"))
        
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(zip_bytes)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f"attachment; filename=sairo_analysis_{request.dataset_id[:8]}.zip")
        msg.attach(attachment)
        
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        send_message = {"raw": raw_message}
        
        send_result = service.users().messages().send(userId="me", body=send_message).execute()
        logger.info("report_email_sent", extra={"event": "report_email_sent", "recipient": request.recipient_email})
        
        return {
            "status": "sent",
            "message_id": send_result["id"],
            "recipient": request.recipient_email,
            "files_included": ["cleaned_data.csv", "analysis_report.html"],
            "archive_size_kb": len(zip_bytes) / 1024
        }
    
    except Exception as error:
        logger.error(f"export_report_error: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to send report: {str(error)}")


async def send_via_gmail(recipient: str, subject: str, message: str, csv_bytes: bytes, filename: str) -> dict[str, Any]:
    """Send cleaned dataset via Gmail using OAuth2."""
    try:
       from google.auth.transport.requests import Request
       from google.oauth2.service_account import Credentials
       from googleapiclient.discovery import build
       from googleapiclient.errors import HttpError
       from email.mime.base import MIMEBase
       from email import encoders
       import base64

       gmail_service_account = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON")
       if not gmail_service_account:
           raise HTTPException(status_code=500, detail="Gmail not configured (set GMAIL_SERVICE_ACCOUNT_JSON)")

       try:
           sa_info = json.loads(gmail_service_account)
       except json.JSONDecodeError:
           sa_info = json.loads(Path(gmail_service_account).read_text())

       creds = Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/gmail.send"])
       service = build("gmail", "v1", credentials=creds)

       msg = MIMEMultipart()
       msg["to"] = recipient
       msg["subject"] = subject
       msg.attach(MIMEText(message, "plain"))

       attachment = MIMEBase("application", "octet-stream")
       attachment.set_payload(csv_bytes)
       encoders.encode_base64(attachment)
       attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
       msg.attach(attachment)

       raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
       send_message = {"raw": raw_message}

       send_result = service.users().messages().send(userId="me", body=send_message).execute()
       logger.info("gmail_sent", extra={"event": "gmail_sent", "recipient": recipient, "message_id": send_result["id"]})
       return {"status": "sent", "message_id": send_result["id"], "recipient": recipient}

    except HttpError as error:
       logger.error(f"gmail_send_failed: {error}")
       raise HTTPException(status_code=500, detail=f"Failed to send via Gmail: {str(error)}")
    except Exception as error:
       logger.error(f"gmail_error: {error}")
       raise HTTPException(status_code=500, detail="Gmail integration error")


@app.post("/api/send-cleaned-via-gmail")
async def send_cleaned_via_gmail(
    request: SendViaGmailRequest, 
    user_id: Annotated[str, Depends(get_current_user_id)],
    x_dataset_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """Send cleaned dataset via Gmail after cleaning."""
    df = get_dataset(request.dataset_id, user_id, x_dataset_token)
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    filename = f"cleaned_dataset_{request.dataset_id[:8]}.csv"
    result = await send_via_gmail(
       recipient=request.recipient_email,
       subject=request.subject,
       message=request.message,
       csv_bytes=csv_bytes,
       filename=filename
    )
    return result


@app.post("/api/news/collect", response_model=NewsCollectResponse)
async def collect_news(request: NewsCollectRequest, authorization: str | None = Header(default=None)) -> NewsCollectResponse:
    require_news_admin(authorization)
    return await run_news_collection(request.days_for_csv, request.send_email)


@app.post("/api/news/webhook", response_model=NewsCollectResponse)
async def news_schedule_webhook(authorization: str | None = Header(default=None)) -> NewsCollectResponse:
    require_news_admin(authorization)
    return await run_news_collection(days_for_csv=7, send_email=False)


@app.get("/api/news/export-csv")
async def export_news_csv(days: int = 7, authorization: str | None = Header(default=None)) -> Response:
    require_news_admin(authorization)
    articles = await load_news_articles(days)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the requested period")
    csv_bytes = await asyncio.to_thread(generate_news_csv, articles)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="financial_news_{days}d.csv"'},
    )


@app.get("/api/news/latest")
async def latest_news(limit: int = 20, days: int = 3, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_news_admin(authorization)
    safe_limit = max(1, min(limit, 100))
    articles = await load_news_articles(days)
    return {"total": len(articles), "articles": articles[:safe_limit]}


@app.get("/api/news/market")
async def latest_market(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_news_admin(authorization)
    market = await load_market_snapshot_sync()
    if not market:
        market = await fetch_market_snapshot()
        # If still no market, raise HTTP exception
        if not market:
            raise HTTPException(status_code=404, detail="No market data available")
        # Store initial market snapshot if none existed
        try:
            await supabase.table("market_snapshots").insert(market).execute()
        except Exception as e:
            logger.error(f"supabase_initial_market_snapshot_store_error: {e}")
    return market


@app.post("/api/news/send-email")
async def trigger_news_email(days: int = 7, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_news_admin(authorization)
    articles = await load_news_articles(days)
    market = await load_market_snapshot_sync()
    sent = await send_digest_email(articles, market, days)
    return {"sent": sent, "articles_in_digest": len(articles)}


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/{path_name:path}", include_in_schema=False)
def frontend(path_name: str = ""):
    target = FRONTEND_DIST / path_name
    if target.is_file():
        return FileResponse(target)
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend has not been built. Run npm install && npm run build in app/frontend."}
