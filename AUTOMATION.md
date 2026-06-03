# Automation with Sairo Insights & n8n

Sairo Insights can be integrated with **n8n** to automate data workflows, such as daily financial news collection and market analysis.

## Configuration

1.  Open the `app/backend/.env` file.
2.  Set the following variables:
    -   `N8N_URL`: The URL where your n8n instance is running (e.g., `http://localhost:5678`).
    -   `ADMIN_API_KEY`: A secret token used to authenticate n8n requests to Sairo Insights.
    -   `SAIRO_URL`: The URL where Sairo Insights is running (e.g., `http://localhost:8000`).

## Importing the Automation Workflow

We have provided a pre-configured workflow file: `app/automation/sairo_insights_workflow.json`.

1.  Open your **n8n** dashboard.
2.  Click on **Workflows** -> **Add Workflow** (or use an existing one).
3.  Click the three dots (menu) in the top right corner and select **Import from File**.
4.  Upload the `sairo_insights_workflow.json` file.
5.  Update the **HTTP Request** node if your `ADMIN_API_KEY` or `SAIRO_URL` differs from the defaults.
6.  Click **Save** and **Activate** the workflow.

## Available Automation Endpoints

### 1. Trigger News Collection
-   **Endpoint:** `POST /api/news/webhook`
-   **Authentication:** `Authorization: Bearer <ADMIN_API_KEY>`
-   **Description:** Triggers the RSS news collection and market snapshot process.

### 2. Export News CSV
-   **Endpoint:** `GET /api/news/export-csv?days=7`
-   **Authentication:** `Authorization: Bearer <ADMIN_API_KEY>`
-   **Description:** Returns a CSV file of the collected news.

### 3. Send Digest Email
-   **Endpoint:** `POST /api/news/send-email?days=7`
-   **Authentication:** `Authorization: Bearer <ADMIN_API_KEY>`
-   **Description:** Sends a summary email of the news (requires SMTP configuration in `.env`).
