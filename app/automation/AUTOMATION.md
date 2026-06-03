Sairo Insights — n8n Integration + Gmail Automation Setup

Overview

This folder contains three pre-built n8n workflows:
- sairo_insights_workflow.json — minimal schedule -> webhook (original)
- sairo_insights_workflow_enhanced.json — enhanced: schedule -> webhook -> export CSV -> email + Google Sheets
- sairo_insights_workflow_enhanced.json (v2) — **NEW**: Full automation with Gmail for news AND cleaned datasets

New Features (Gmail Integration)

1. **Send Cleaned Data via Gmail** — After cleaning a dataset, users can send it directly via Gmail with a custom message.
2. **n8n Automation** — Schedule automated data cleaning + Gmail sending + news digest in one workflow.
3. **Backend Endpoint** — `/api/send-cleaned-via-gmail` supports OAuth2 Gmail credentials.

Quick Setup (local)

### Backend Configuration

1. Ensure backend is running (Pinokio Start): http://localhost:8000
2. Set required env vars in `app/backend/.env`:
   ```
   ADMIN_API_KEY=replace-with-a-long-random-token
   NEWS_AUTOMATION_ENABLED=true
   NEWS_RECIPIENT_EMAIL=recipient@example.com
   NEWS_SENDER_EMAIL=sender@example.com
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=sender@example.com
   SMTP_PASSWORD=app-password
   
   # Gmail OAuth2 (for cleaned data sending)
   GMAIL_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
   # OR path to JSON file:
   GMAIL_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
   ```

### Frontend Usage

After cleaning a dataset in the UI:
1. Fill in recipient email, subject, and message
2. Click "Send via Gmail"
3. Cleaned CSV is sent to the recipient

### n8n Workflow Setup

1. Start n8n locally:
   ```bash
   docker run -it --rm -p 5678:5678 -e N8N_HOST=0.0.0.0 n8nio/n8n
   # OR: npx n8n start
   ```

2. Open n8n at http://localhost:5678

3. Create n8n credentials:
   - **Gmail** (OAuth2): Connect your Google account
   - **Google Sheets**: For optional data logging
   - **SMTP** (if using email instead of Gmail)

4. Import workflow:
   - In n8n UI: Top-right → Import from File → select `sairo_insights_workflow_enhanced.json`

5. Configure imported workflow:
   - Replace `REPLACE_WITH_ADMIN_API_KEY` with your `ADMIN_API_KEY` value
   - Replace `REPLACE_WITH_DATASET_ID` with actual dataset ID (or parameterize)
   - Replace `REPLACE_WITH_DATASET_TOKEN` with valid token
   - Set n8n credentials for Gmail, SMTP, Google Sheets as needed
   - Update email recipients in environment variables

6. Activate the workflow

### Google Cloud Setup (for Gmail via Service Account)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API:
   - Search "Gmail API" → Enable
4. Create Service Account:
   - Left menu → Service Accounts
   - Create new service account
   - Generate JSON key → Download
5. Delegate domain-wide authority (optional):
   - In Service Account → Edit → Enable "Domain-wide delegation"
   - Copy Client ID
6. Set `GMAIL_SERVICE_ACCOUNT_JSON` env var to the JSON content or file path

### Workflow Execution Flow

```
Schedule (8am UTC)
  ↓
Sync News Articles
  ↓
Export News CSV
  ↓
├→ Send News via Gmail
├→ Append to Google Sheets
│
Fetch & Send Cleaned Data (parallel)
  ↓
Send Cleaned Dataset Email
```

Tips & Troubleshooting

- **Gmail not sending?** Ensure service account has delegated authority or is authorized to send email.
- **n8n can't reach backend?** Check backend is running at http://localhost:8000 and firewall allows requests.
- **API key mismatch?** Verify `ADMIN_API_KEY` in `.env` matches value used in n8n headers.
- **Logs:** Check `logs/api/` for backend errors or n8n execution logs for workflow debugging.

Next Steps

- Test Gmail sending manually via frontend UI
- Configure n8n to run on a schedule
- Export cleaned datasets automatically to Google Sheets
- Set up alerts on email failures
