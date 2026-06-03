Act as a senior data scientist and full-stack engineer. Design and build a complete MVP for a custom web-based data analysis application. The goal is to create a simple, scalable tool that allows  users  to upload, clean, analyze, and visualize datasets while generating automatic insights.

-----------------------------------
CORE OBJECTIVE:
Build a functional MVP that follows a clear workflow:
Upload → Clean → Analyze → Visualize → Insights

Focus on simplicity, usability, and performance. Avoid over-engineering.

-----------------------------------
TECH STACK:
Frontend:
- React.js with Tailwind CSS

Backend:
- Python with FastAPI (preferred) or Flask

Data Processing:
- Pandas, NumPy, SciPy

Machine Learning:
- Scikit-learn (basic linear regression only)

Visualization:
- Plotly or Chart.js

Storage:
- Temporary local/session-based storage (optional AWS S3)

-----------------------------------
PHASED BUILD EXECUTION PLAN:

PHASE 1: SETUP
- Initialize frontend and backend projects
- Setup Python virtual environment
- Configure FastAPI server
- Create React app with Tailwind
- Setup Git repository
- Ensure both frontend and backend run locally

DELIVERABLE: Basic app structure running

-----------------------------------
PHASE 2: DATA UPLOAD SYSTEM
Backend:
- Create /upload endpoint
- Accept CSV, Excel (.xlsx), JSON
- Max file size: 50MB
- Use pandas to parse files
- Auto-detect schema and data types
- Return:
  - First 10 rows
  - Column names
  - Data types

Frontend:
- Drag-and-drop upload interface
- Display preview table
- Show dataset metadata (rows, columns)

DELIVERABLE: Upload and preview working

-----------------------------------
PHASE 3: DATA CLEANING MODULE
Backend:
- Handle missing values:
  - Mean, median, mode, or drop
- Remove duplicates
- Detect outliers:
  - IQR method
  - Z-score method
- Fix incorrect data types

Frontend:
- Controls:
  - Buttons/toggles for cleaning actions
- Show before vs after comparison

DELIVERABLE: Cleaned dataset returned and visible

-----------------------------------
PHASE 4: DATA ANALYSIS ENGINE
Backend:
- Descriptive statistics (mean, median, std, variance)
- Correlation matrix (Pearson, Spearman)
- Group-by aggregations (sum, mean, count)
- Basic predictive modeling:
  - Linear regression using sklearn

Frontend:
- User selects columns and analysis type
- Display results in tables and summaries

DELIVERABLE: Functional analysis system

-----------------------------------
PHASE 5: VISUALIZATION DASHBOARD
Frontend:
- Implement charts:
  - Bar, line, scatter, histogram, box plot
- Use Plotly or Chart.js
- Add interactivity (hover, zoom)

Smart logic:
- Auto-suggest chart types:
  - Numeric vs numeric → scatter
  - Category vs numeric → bar

Backend (optional):
- Prepare structured chart data

DELIVERABLE: Interactive visualizations

-----------------------------------
PHASE 6: INSIGHTS GENERATOR
Backend:
- Generate automatic plain-language insights:
  - Trends (increase/decrease)
  - Strong correlations (>0.7)
  - Outliers/anomalies

Frontend:
- Display insights as cards or bullet points

DELIVERABLE: Human-readable insights

-----------------------------------
PHASE 7: UX/UI FLOW & POLISH
- Create step-by-step navigation:
  1. Upload
  2. Clean
  3. Analyze
  4. Visualize
- Add:
  - Loading indicators
  - Error handling
  - Clean minimal UI

DELIVERABLE: Smooth user experience

-----------------------------------
PHASE 8: PERFORMANCE & TESTING
- Ensure support for datasets up to ~100k rows
- Optimize processing time (<3 seconds typical operations)
- Avoid redundant data reloads
- Implement basic in-memory caching
- Test edge cases (empty files, bad formats)

DELIVERABLE: Stable MVP

-----------------------------------
PHASE 9: DEPLOYMENT
- Backend:
  - Deploy on Render or Railway
- Frontend:
  - Deploy on Vercel or Netlify
- Ensure environment variables configured
- Provide public access link

DELIVERABLE: Live working app

-----------------------------------
SECURITY:
- Validate file uploads
- Prevent code injection
- Use temporary file storage with auto-deletion

-----------------------------------
OUTPUT REQUIREMENTS:
- Working MVP application
- Clean, modular, well-documented code
- Sample dataset for testing
- Deployment instructions
- Architecture overview
- Key code snippets (API, data processing, charts)
- Example user flow
- Basic UI wireframe (text-based acceptable)

-----------------------------------
CONSTRAINTS:
- Keep it simple and beginner-friendly
- Avoid unnecessary features
- Focus on core functionality only
- Build for clarity, not complexity

-----------------------------------
OPTIONAL (IF TIME ALLOWS):
- JWT-based authentication
- Save/load analysis sessions
- Export cleaned datasets
