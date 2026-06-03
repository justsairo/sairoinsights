# Sairo Insights Pre-Deployment Security Checklist

Stack reviewed: React frontend, FastAPI backend, Pandas in-memory dataset storage, no user accounts, no password reset flow, and no database.

## 1. Authorization

Already in place:
- Dataset APIs require an unguessable per-dataset access token in the `X-Dataset-Token` header.
- `dataset_id` alone is no longer sufficient to access, clean, analyze, chart, or inspect a dataset.

Missing:
- There is still no user account system. For multi-user production, replace dataset tokens with authenticated users and store `owner_user_id` with each dataset.

Production pattern once a database exists:

```sql
select * from datasets
where id = :dataset_id and owner_user_id = :current_user_id;
```

Routes requiring ownership checks:
- `POST /api/clean`
- `POST /api/analyze`
- `POST /api/chart`
- `GET /api/insights/{dataset_id}`

## 2. Input Validation

Already in place:
- Pydantic request models constrain analysis, chart, cleaning, outlier, and aggregation options.
- Uploaded file types are restricted to CSV, Excel, and JSON.
- Uploads are capped at 50MB, 100,000 rows, and 500 columns.
- React renders values as text, not raw HTML.

Missing:
- If this app later adds forms beyond dataset controls, keep validating with Pydantic on the backend and avoid `dangerouslySetInnerHTML` on the frontend.

## 3. CORS Policy

Already in place:
- Backend reads trusted origins from `ALLOWED_ORIGINS`.
- The API no longer uses `*`.

Production example:

```bash
ALLOWED_ORIGINS=https://sairoinsights.com,https://admin.sairoinsights.com
```

## 4. Rate Limiting

Already in place:
- API routes are rate limited by IP and path.
- Default is `60` requests per `60` seconds.
- Exceeded limits return `429` and `Retry-After`.

Production example:

```bash
RATE_LIMIT_MAX_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

For larger production deployments, move rate limiting to Redis or an edge gateway so limits work across multiple server instances.

## 5. Password Reset Security

Not applicable:
- The app has no accounts or passwords.

Required if auth is added:
- Store only a hash of the reset token.
- Generate tokens with a cryptographic random generator.
- Expire in 30 minutes.
- Mark tokens used after successful reset.

Database shape:

```sql
create table password_reset_tokens (
  id uuid primary key,
  user_id uuid not null references users(id),
  token_hash text not null unique,
  expires_at timestamptz not null,
  used_at timestamptz
);
create index idx_password_reset_tokens_user_id on password_reset_tokens(user_id);
create index idx_password_reset_tokens_expires_at on password_reset_tokens(expires_at);
```

## 6. Error Handling

Already in place:
- Backend validation, HTTP, and unhandled exceptions return safe user-facing messages.
- Backend logs server exceptions internally.
- React has a global error boundary with a clean fallback.

## 7. Database Indexes

Not applicable:
- There is no database yet.

Required if persistence is added:

```sql
create index idx_datasets_owner_user_id on datasets(owner_user_id);
create index idx_datasets_created_at on datasets(created_at);
create unique index idx_users_email on users(lower(email));
create index idx_analysis_jobs_dataset_id on analysis_jobs(dataset_id);
```

## 8. Logging

Already in place:
- Backend emits structured JSON logs.
- Request completion, validation errors, rate limit events, uploads, and unhandled errors are logged.
- Dataset tokens and uploaded data contents are not logged.

Recommended production sinks:
- Sentry for application errors.
- Datadog, Better Stack/Logtail, or CloudWatch for structured logs.

## 9. Alerts

Recommended alerts:
- Uptime check: `GET /api/health` fails for 2 consecutive checks.
- Error rate: 5xx responses exceed 2% over 5 minutes.
- Latency: p95 request duration exceeds 2 seconds for 10 minutes.
- Rate limiting: 429 responses spike unexpectedly.
- Disk/memory pressure if deployed on a VM.

Tools:
- UptimeRobot for basic uptime.
- Sentry for exceptions.
- Datadog or Better Stack for logs, metrics, and alert routing.

## 10. Rollback Strategy

Recommended deployment model:
- Use immutable releases with tagged Git commits.
- Build the frontend and backend from the same commit.
- Keep migrations reversible once a database is added.

Git rollback:

```bash
git tag v1.0.0
git revert <bad_commit_sha>
git push origin main
```

Render-style rollback:
- Open service dashboard.
- Select the last healthy deploy.
- Click rollback/redeploy previous version.

Database rule once migrations exist:
- Every migration must include a tested down migration before release.
