# Sairo Insights

Sairo Insights is a local web app for lightweight dataset exploration. It supports the workflow from the project spec: upload, clean, analyze, visualize, generate automatic insights, and monitor financial news with live market snapshots.

## Use

1. Click **Install** in Pinokio.
2. Click **Start**.
3. Open the Web UI.
4. Upload a CSV, Excel, or JSON file, or load the included sample dataset.

The app keeps datasets in memory for the current server session.

## Architecture

- `app/backend`: FastAPI API, Pandas processing, SciPy outlier detection, scikit-learn linear regression, RSS financial news collection, yfinance market snapshots, SMTP digest email, and static frontend hosting.
- `app/frontend`: React, Tailwind CSS, Plotly, and lucide-react icons.
- Launcher scripts live in the project root for Pinokio one-click install, start, update, and reset.

## API

### JavaScript

```js
const form = new FormData()
form.append("file", file)
const upload = await fetch("/api/upload", { method: "POST", body: form }).then(r => r.json())

const stats = await fetch("/api/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ dataset_id: upload.dataset_id, analysis_type: "describe" })
}).then(r => r.json())
```

### Python

```python
import requests

with open("app/backend/sample_sales.csv", "rb") as handle:
    upload = requests.post("http://127.0.0.1:8000/api/upload", files={"file": handle}).json()

stats = requests.post("http://127.0.0.1:8000/api/analyze", json={
    "dataset_id": upload["dataset_id"],
    "analysis_type": "describe"
}).json()
```

### Curl

```bash
curl -F "file=@app/backend/sample_sales.csv" http://127.0.0.1:8000/api/upload
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"DATASET_ID","analysis_type":"describe"}'
```

## Endpoints

- `GET /api/health`
- `GET /api/sample`
- `POST /api/upload`
- `POST /api/clean`
- `POST /api/analyze`
- `POST /api/chart`
- `GET /api/insights/{dataset_id}`
- `POST /api/news/collect`
- `POST /api/news/webhook`
- `GET /api/news/latest`
- `GET /api/news/market`
- `GET /api/news/export-csv`
- `POST /api/news/send-email`

## Financial News Automation

The News screen collects headlines from Reuters, Bloomberg, WSJ, FT, and The Economist RSS feeds, fetches market prices from Yahoo Finance, stores results in `app/backend/data`, exports CSV, and can send an HTML digest email.

## n8n Integration

Sairo Insights includes a pre-configured integration for **n8n** to automate your data and news workflows.

- **Pre-configured Workflow:** Find a ready-to-import workflow in `app/automation/sairo_insights_workflow.json`.
- **Easy Access:** Use the **Automation (n8n)** button in the Pinokio sidebar to open your n8n dashboard.
- **Documentation:** See [AUTOMATION.md](AUTOMATION.md) for detailed setup and import instructions.

Optional environment variables:

```bash
NEWS_AUTOMATION_ENABLED=true
NEWS_AUTOMATION_HOUR_UTC=7
ADMIN_API_KEY=replace-with-a-long-random-token
NEWS_RECIPIENT_EMAIL=recipient@example.com
NEWS_SENDER_EMAIL=sender@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=sender@example.com
SMTP_PASSWORD=app-password
```

When `ADMIN_API_KEY` is set, protected news mutation/export routes require:

```bash
Authorization: Bearer <ADMIN_API_KEY>
```

## Example Flow

Upload the sample data, remove duplicates, fill missing values, run descriptive statistics, create a scatter or bar chart, generate plain-language insights, then open News to collect market headlines and export or email the weekly digest.
