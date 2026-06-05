import express from 'express';
import multer from 'multer';
import cors from 'cors';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import * as math from 'mathjs';
import * as ss from 'simple-statistics';
import { DatasetRecord, AnalyzeRequest } from './types';

dotenv.config();

const app = express();
const port = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());

const DATASETS: Map<string, DatasetRecord> = new Map();
const USERS: Map<string, string> = new Map();

// Multer for file uploads
const upload = multer({ storage: multer.memoryStorage() });

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', engine: 'TypeScript/Node.js' });
});

// Config
app.get('/api/config', (req, res) => {
  res.json({
    supabase_enabled: false,
    automation_enabled: !!process.env.ADMIN_API_KEY
  });
});

// Auth (Local Fallback)
app.post('/api/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (USERS.has(email)) return res.status(400).json({ detail: 'User already exists' });
  USERS.set(email, password);
  res.json({
    user: { id: 'local', email },
    session: { access_token: `local_token_${email}` },
    message: 'Signup successful (Local Mode/TS).'
  });
});

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  if (USERS.get(email) !== password) return res.status(401).json({ detail: 'Invalid credentials' });
  res.json({
    user: { id: 'local', email },
    session: { access_token: `local_token_${email}`, refresh_token: 'local_refresh_token' }
  });
});

// Helper for cleaning
app.post('/api/clean', (req, res) => {
  const { dataset_id, missing, remove_duplicates, outlier_method } = req.body;
  const record = DATASETS.get(dataset_id);
  if (!record) return res.status(404).json({ detail: 'Dataset not found' });

  let df = [...record.data];
  const before = {
    rows: df.length,
    missing: countMissing(df, record.columns),
    duplicates: countDuplicates(df)
  };

  if (remove_duplicates) {
    const seen = new Set();
    df = df.filter(row => {
      const s = JSON.stringify(row);
      if (seen.has(s)) return false;
      seen.add(s);
      return true;
    });
  }

  const numericCols = record.columns.filter(col => 
    df.every(row => typeof row[col] === 'number' || row[col] === null)
  );

  record.columns.forEach(col => {
    const vals = df.map(r => r[col]).filter(v => v !== null);
    if (vals.length < df.length) {
      if (missing === 'mean' && numericCols.includes(col)) {
        const mean = ss.mean(vals as number[]);
        df.forEach(row => { if (row[col] === null) row[col] = mean; });
      } else if (missing === 'median' && numericCols.includes(col)) {
        const median = ss.median(vals as number[]);
        df.forEach(row => { if (row[col] === null) row[col] = median; });
      } else if (missing === 'mode') {
        const mode = ss.mode(vals);
        df.forEach(row => { if (row[col] === null) row[col] = mode; });
      }
    }
  });

  if (missing === 'drop') {
    df = df.filter(row => record.columns.every(col => row[col] !== null));
  }

  if (outlier_method !== 'none' && numericCols.length > 0) {
    numericCols.forEach(col => {
      const vals = df.map(r => r[col]).filter(v => v !== null) as number[];
      if (vals.length > 0) {
        if (outlier_method === 'iqr') {
          const q1 = ss.quantile(vals, 0.25);
          const q3 = ss.quantile(vals, 0.75);
          const iqr = q3 - q1;
          const low = q1 - 1.5 * iqr;
          const high = q3 + 1.5 * iqr;
          df = df.filter(row => row[col] === null || (row[col] >= low && row[col] <= high));
        } else if (outlier_method === 'zscore') {
          const mean = ss.mean(vals);
          const std = ss.standardDeviation(vals);
          df = df.filter(row => row[col] === null || Math.abs((row[col] - mean) / std) < 3);
        }
      }
    });
  }

  const cleanedId = uuidv4();
  DATASETS.set(cleanedId, { data: df, columns: record.columns, accessToken: record.accessToken });

  res.json({
    dataset_id: cleanedId,
    dataset_token: record.accessToken,
    columns: record.columns,
    rows: df.length,
    preview: df.slice(0, 5),
    before,
    after: {
      rows: df.length,
      missing: countMissing(df, record.columns),
      duplicates: countDuplicates(df)
    }
  });
});

function countMissing(data: any[], cols: string[]) {
  let count = 0;
  data.forEach(row => cols.forEach(col => { if (row[col] === null) count++; }));
  return count;
}

function countDuplicates(data: any[]) {
  const seen = new Set();
  let count = 0;
  data.forEach(row => {
    const s = JSON.stringify(row);
    if (seen.has(s)) count++;
    else seen.add(s);
  });
  return count;
}

// Upload endpoint
import * as xlsx from 'xlsx';
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ detail: 'No file uploaded' });
  
  let data: any[] = [];
  const filename = req.file.originalname.toLowerCase();

  if (filename.endsWith('.csv')) {
    data = parse(req.file.buffer.toString(), { columns: true, cast: true });
  } else if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) {
    const workbook = xlsx.read(req.file.buffer);
    const firstSheet = workbook.SheetNames[0];
    data = xlsx.utils.sheet_to_json(workbook.Sheets[firstSheet]);
  } else if (filename.endsWith('.json')) {
    data = JSON.parse(req.file.buffer.toString());
  } else {
    return res.status(400).json({ detail: 'Unsupported file format' });
  }

  const id = uuidv4();
  const columns = data.length > 0 ? Object.keys(data[0]) : [];
  DATASETS.set(id, { data, columns, accessToken: 'local_token' });

  res.json({
    dataset_id: id,
    dataset_token: 'local_token',
    columns,
    rows: data.length,
    preview: data.slice(0, 5)
  });
});

app.post('/api/analyze', (req, res) => {
  const request: AnalyzeRequest = req.body;
  const dataset = DATASETS.get(request.dataset_id);
  
  if (!dataset) return res.status(404).json({ detail: 'Dataset not found' });

  const numericCols = dataset.columns.filter(col => 
    dataset.data.every(row => typeof row[col] === 'number' || row[col] === null)
  );

  try {
    switch (request.analysis_type) {
      case 'describe': {
        const result = numericCols.map(col => {
          const vals = dataset.data.map(r => r[col]).filter(v => v !== null) as number[];
          if (vals.length === 0) return { index: col };
          return {
            index: col,
            count: vals.length,
            mean: ss.mean(vals),
            std: ss.standardDeviation(vals),
            min: ss.min(vals),
            '25%': ss.quantile(vals, 0.25),
            '50%': ss.median(vals),
            '75%': ss.quantile(vals, 0.75),
            max: ss.max(vals)
          };
        });
        return res.json({ type: 'describe', result });
      }

      case 'correlation': {
        const result: any = {};
        numericCols.forEach(c1 => {
          result[c1] = {};
          numericCols.forEach(c2 => {
            const v1: number[] = [];
            const v2: number[] = [];
            dataset.data.forEach(row => {
              if (typeof row[c1] === 'number' && typeof row[c2] === 'number') {
                v1.push(row[c1]);
                v2.push(row[c2]);
              }
            });
            result[c1][c2] = v1.length > 1 ? ss.sampleCorrelation(v1, v2) : 1;
          });
        });
        return res.json({ type: 'correlation', method: 'pearson', result });
      }

      case 'regression': {
        if (!request.x || !request.y) return res.status(400).json({ detail: 'Select X and Y columns' });
        const pairs = dataset.data
          .filter(r => typeof r[request.x!] === 'number' && typeof r[request.y!] === 'number')
          .map(r => [r[request.x!], r[request.y!]] as [number, number]);
        
        if (pairs.length < 2) return res.status(400).json({ detail: 'Need at least two valid rows' });
        
        const regression = ss.linearRegression(pairs);
        const r2 = ss.linearRegressionLine(regression); // This is the line function, not R2
        // Calculate R2 manually or use another method
        const xVals = pairs.map(p => p[0]);
        const yVals = pairs.map(p => p[1]);
        const yPred = xVals.map(x => regression.m * x + regression.b);
        const rSquared = ss.rSquared(pairs, x => regression.m * x + regression.b);

        return res.json({
          type: 'regression',
          coefficient: regression.m,
          intercept: regression.b,
          r2: rSquared
        });
      }

      case 'moving_average': {
        if (!request.value) return res.status(400).json({ detail: 'Select a column for moving average' });
        const vals = dataset.data.map(r => r[request.value!]).filter(v => typeof v === 'number') as number[];
        const window = request.window || 7;
        const result: number[] = [];
        for (let i = 0; i <= vals.length - window; i++) {
          const slice = vals.slice(i, i + window);
          result.push(ss.mean(slice));
        }
        return res.json({ type: 'moving_average', result });
      }

      default:
        return res.status(400).json({ detail: 'Unsupported analysis type in TS engine' });
    }
  } catch (err: any) {
    res.status(500).json({ detail: err.message });
  }
});

// Helper for initial sample data
import fs from 'fs';
import { parse } from 'csv-parse/sync';

app.get('/api/sample', (req, res) => {
  const csvPath = '../backend/sample_sales.csv';
  if (fs.existsSync(csvPath)) {
    const fileContent = fs.readFileSync(csvPath, 'utf-8');
    const records = parse(fileContent, { columns: true, cast: true });
    const id = uuidv4();
    const columns = Object.keys(records[0]);
    DATASETS.set(id, { data: records, columns, accessToken: 'local_token' });
    
    res.json({
      dataset_id: id,
      dataset_token: 'local_token',
      columns,
      rows: records.length,
      preview: records.slice(0, 5)
    });
  } else {
    res.status(404).json({ detail: 'Sample data not found' });
  }
});

app.listen(port, () => {
  console.log(`TypeScript Backend running at http://localhost:${port}`);
});
