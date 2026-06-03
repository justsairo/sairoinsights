import React, { useMemo, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import Plot from "react-plotly.js";
import {
  Activity,
  BarChart3,
  Database,
  FileCode,
  FileUp,
  LineChart,
  Loader2,
  Network,
  Newspaper,
  RefreshCw,
  Send,
  Sparkles,
  Wand2,
  Lock,
  Mail,
  ArrowRight,
  CheckCircle2
} from "lucide-react";
import "./styles.css";

const API = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL) || "";
const steps = ["Upload", "Clean", "Analyze", "Visualize", "Insights", "News", "Automation"];

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    console.error("frontend_error", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="grid min-h-screen place-items-center bg-zinc-50 p-6 text-zinc-950">
          <div className="max-w-md rounded-md border border-zinc-200 bg-white p-6 text-center">
            <h1 className="text-xl font-semibold">Something went wrong.</h1>
            <p className="mt-2 text-sm text-zinc-600">Try refreshing the page.</p>
            <button className="btn-primary mt-4" onClick={() => window.location.reload()}>Refresh</button>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}

function AuthPage({ setUser, config }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showHome, setShowHome] = useState(true);

  async function handleAuth(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!isLogin && password !== confirmPassword) {
      setError("Passwords don't match");
      setLoading(false);
      return;
    }

    try {
      const endpoint = isLogin ? "/api/auth/login" : "/api/auth/signup";
      const response = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      localStorage.setItem("auth_token", data.session.access_token);
      localStorage.setItem("user_email", email);
      setUser({ email });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (showHome && !config.supabase_enabled) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="min-h-screen flex flex-col">
          <div className="flex-1 flex items-center justify-center px-6 py-20">
            <div className="max-w-2xl w-full space-y-12">
              <div className="text-center space-y-6">
                <div className="flex h-16 w-16 mx-auto items-center justify-center rounded-xl bg-gradient-to-br from-blue-400 to-purple-600 text-white font-bold text-2xl">
                  SI
                </div>
                <div>
                  <h1 className="text-5xl font-bold text-white mb-2">Sairo Insights</h1>
                  <p className="text-xl text-slate-300">Advanced Data Analysis & Automation Platform</p>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                {[
                  { icon: Database, title: "Upload Data", desc: "CSV, Excel, JSON support" },
                  { icon: Wand2, title: "Smart Cleaning", desc: "Auto data preparation" },
                  { icon: Sparkles, title: "AI Insights", desc: "Correlations & patterns" },
                  { icon: BarChart3, title: "Visualize", desc: "Interactive charts" },
                  { icon: Newspaper, title: "News Feed", desc: "Market updates" },
                  { icon: Network, title: "Automate", desc: "n8n workflows" },
                ].map((f, i) => (
                  <div key={i} className="rounded-lg border border-purple-500/20 bg-purple-500/10 p-4 text-center">
                    <div className="flex justify-center mb-3">
                      <f.icon className="w-8 h-8 text-purple-400" />
                    </div>
                    <h3 className="font-semibold text-white text-sm">{f.title}</h3>
                    <p className="text-xs text-slate-400 mt-1">{f.desc}</p>
                  </div>
                ))}
              </div>

              <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-1">
                <button
                  onClick={() => setShowHome(false)}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-3 px-6 rounded-md transition flex items-center justify-center gap-2"
                >
                  Get Started <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              <div className="text-center text-sm text-slate-400">
                <p>Powered by FastAPI, React, and Supabase</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-slate-700 bg-slate-800/50 backdrop-blur p-8 space-y-6">
          <div className="text-center">
            <div className="flex h-12 w-12 mx-auto items-center justify-center rounded-lg bg-gradient-to-br from-blue-400 to-purple-600 text-white font-bold mb-4">
              SI
            </div>
            <h1 className="text-2xl font-bold text-white">{isLogin ? "Welcome Back" : "Create Account"}</h1>
            <p className="text-sm text-slate-400 mt-1">
              {isLogin ? "Sign in to access your insights" : "Join to start analyzing your data"}
            </p>
          </div>

          {error && (
            <div className="rounded-md border border-red-500/50 bg-red-500/10 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <form onSubmit={handleAuth} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-200">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full mt-1 px-4 py-2 rounded-md border border-slate-600 bg-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-200">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full mt-1 px-4 py-2 rounded-md border border-slate-600 bg-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="••••••••"
              />
            </div>

            {!isLogin && (
              <div>
                <label className="text-sm font-medium text-slate-200">Confirm Password</label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full mt-1 px-4 py-2 rounded-md border border-slate-600 bg-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="••••••••"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-md transition flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              {isLogin ? "Sign In" : "Create Account"}
            </button>
          </form>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-purple-400 hover:text-purple-300 transition"
            >
              {isLogin ? "Need an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>

          {showHome && (
            <button
              onClick={() => setShowHome(true)}
              className="w-full text-sm text-slate-400 hover:text-slate-300 transition py-2"
            >
              ← Back to Home
            </button>
          )}
        </div>
      </div>
    </main>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [step, setStep] = useState("Upload");
  const [dataset, setDataset] = useState(null);
  const [cleaned, setCleaned] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [chart, setChart] = useState(null);
  const [insights, setInsights] = useState([]);
  const [news, setNews] = useState({ articles: [], market: null, total: 0, collection: null });
  const [config, setConfig] = useState({ n8n_url: "http://localhost:5678", automation_enabled: false, supabase_enabled: false });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const active = cleaned || dataset;

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    const userEmail = localStorage.getItem("user_email");
    if (token && userEmail) {
      setUser({ email: userEmail });
    }
    request("/api/config").then(setConfig).catch(() => {});
  }, []);

  async function request(path, options = {}) {
    setBusy(true);
    setError("");
    const { datasetToken, headers, ...fetchOptions } = options;
    const requestHeaders = new Headers(headers || {});
    if (datasetToken) {
      requestHeaders.set("X-Dataset-Token", datasetToken);
    }
    const token = localStorage.getItem("auth_token");
    if (token) {
      requestHeaders.set("Authorization", `Bearer ${token}`);
    }
    try {
      const response = await fetch(`${API}${path}`, { ...fetchOptions, headers: requestHeaders });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Request failed");
      return payload;
    } catch (err) {
      setError(err.message || "Something went wrong. Try refreshing the page.");
      throw err;
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    setUser(null);
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_email");
    setStep("Upload");
    setDataset(null);
    setCleaned(null);
  }

  if (!user) {
    return <AuthPage setUser={setUser} config={config} />;
  }

  return (
    <ErrorBoundary>
      <main className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100">
        <div className="sticky top-0 z-50 border-b border-zinc-200 bg-white/95 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 text-white font-bold text-sm">
                SI
              </div>
              <h1 className="text-lg font-bold">Sairo Insights</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-zinc-600">{user.email}</span>
              <button onClick={logout} className="text-sm px-3 py-2 rounded-md bg-red-50 text-red-700 hover:bg-red-100">
                Logout
              </button>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl px-6 py-8">
          {error && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid gap-6 md:grid-cols-5">
            <nav className="space-y-1">
              {steps.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setStep(s);
                    setError("");
                  }}
                  className={`block w-full rounded-md px-3 py-2 text-left text-sm font-medium transition ${
                    step === s
                      ? "bg-blue-600 text-white"
                      : "text-zinc-700 hover:bg-zinc-200"
                  }`}
                >
                  {s}
                </button>
              ))}
            </nav>

            <div className="md:col-span-4 space-y-5">
              {step === "Upload" && <UploadStep onUpload={uploadFile} onSample={loadSample} dataset={dataset} />}
              {step === "Clean" && <CleanStep dataset={active} request={request} setCleaned={setCleaned} setStep={setStep} />}
              {step === "Analyze" && <AnalyzeStep dataset={active} request={request} analysis={analysis} setAnalysis={setAnalysis} />}
              {step === "Visualize" && <VisualizeStep dataset={active} request={request} chart={chart} setChart={setChart} />}
              {step === "Insights" && <InsightsStep dataset={active} request={request} insights={insights} setInsights={setInsights} />}
              {step === "News" && <NewsStep request={request} news={news} setNews={setNews} />}
              {step === "Automation" && <AutomationStep dataset={active} request={request} insights={insights} news={news} />}
            </div>
          </div>
        </div>
      </main>
    </ErrorBoundary>
  );

  async function uploadFile(file) {
    const form = new FormData();
    form.append("file", file);
    const payload = await request("/api/upload", { method: "POST", body: form });
    setDataset(payload);
    setCleaned(null);
    setAnalysis(null);
    setChart(null);
    setInsights([]);
    setStep("Clean");
  }

  async function loadSample() {
    const payload = await request("/api/sample");
    setDataset(payload);
    setCleaned(null);
    setAnalysis(null);
    setChart(null);
    setInsights([]);
    setStep("Clean");
  }
}
function UploadStep({ onUpload, onSample }) {
  return (
    <div>
      <h2 className="mb-4 text-2xl font-semibold">Upload Dataset</h2>
      <label className="flex min-h-72 cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-zinc-300 bg-white p-8 text-center hover:border-emerald-500">
        <FileUp className="mb-3 text-emerald-700" size={34} />
        <span className="text-lg font-medium">Drop or select a CSV, Excel, or JSON file</span>
        <span className="mt-1 text-sm text-zinc-500">Maximum file size: 50MB</span>
        <input className="hidden" type="file" accept=".csv,.xlsx,.xls,.json" onChange={(e) => e.target.files[0] && onUpload(e.target.files[0])} />
      </label>
      <button onClick={onSample} className="mt-4 inline-flex items-center gap-2 rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white">
        <RefreshCw size={16} /> Load sample dataset
      </button>
    </div>
  );
}

function CleanStep({ dataset, request, setCleaned, setStep }) {
  const [missing, setMissing] = useState("none");
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [outlierMethod, setOutlierMethod] = useState("none");
  const [gmailRecipient, setGmailRecipient] = useState("");
  const [gmailSubject, setGmailSubject] = useState("Cleaned Dataset");
  const [gmailMessage, setGmailMessage] = useState("Here is your cleaned dataset.");
  const [cleanedLocal, setCleanedLocal] = useState(null);
  if (!dataset) return <EmptyState />;

  async function clean() {
    const payload = await request("/api/clean", {
      method: "POST",
      datasetToken: dataset.dataset_token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: dataset.dataset_id,
        missing,
        remove_duplicates: removeDuplicates,
        outlier_method: outlierMethod
      })
    });
    setCleanedLocal(payload);
    setCleaned(payload);
  }

  async function sendViaGmail() {
    if (!gmailRecipient) {
      alert("Please enter a recipient email");
      return;
    }
    const result = await request("/api/send-cleaned-via-gmail", {
      method: "POST",
      datasetToken: cleanedLocal.dataset_token || dataset.dataset_token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: cleanedLocal.dataset_id || dataset.dataset_id,
        recipient_email: gmailRecipient,
        subject: gmailSubject,
        message: gmailMessage
      })
    });
    alert("Email sent successfully!");
  }

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Clean Dataset</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <Control label="Missing values">
          <select value={missing} onChange={(e) => setMissing(e.target.value)} className="input">
            <option value="none">Leave unchanged</option>
            <option value="mean">Fill numeric mean</option>
            <option value="median">Fill numeric median</option>
            <option value="mode">Fill mode</option>
            <option value="drop">Drop rows</option>
          </select>
        </Control>
        <Control label="Duplicate rows">
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={removeDuplicates} onChange={(e) => setRemoveDuplicates(e.target.checked)} /> Remove duplicates</label>
        </Control>
        <Control label="Outliers">
          <select value={outlierMethod} onChange={(e) => setOutlierMethod(e.target.value)} className="input">
            <option value="none">Leave unchanged</option>
            <option value="iqr">Remove by IQR</option>
            <option value="zscore">Remove by Z-score</option>
          </select>
        </Control>
      </div>
      <button onClick={clean} className="btn-primary">Apply cleaning</button>
      
      {cleanedLocal && (
        <div className="rounded-md border border-blue-200 bg-blue-50 p-4 space-y-3">
          <h3 className="font-semibold text-blue-900 flex items-center gap-2">
            <Send size={18} /> Send Cleaned Data via Gmail
          </h3>
          <Control label="Recipient Email">
            <input 
              type="email" 
              value={gmailRecipient} 
              onChange={(e) => setGmailRecipient(e.target.value)} 
              placeholder="recipient@example.com"
              className="input"
            />
          </Control>
          <Control label="Subject">
            <input 
              type="text" 
              value={gmailSubject} 
              onChange={(e) => setGmailSubject(e.target.value)} 
              className="input"
            />
          </Control>
          <Control label="Message">
            <textarea 
              value={gmailMessage} 
              onChange={(e) => setGmailMessage(e.target.value)} 
              className="input h-24"
              placeholder="Your message here..."
            />
          </Control>
          <button onClick={sendViaGmail} className="btn-primary">Send via Gmail</button>
        </div>
      )}
      
      <Preview dataset={cleanedLocal || dataset} />
    </div>
  );
}

function AnalyzeStep({ dataset, request, analysis, setAnalysis }) {
  const [analysisType, setAnalysisType] = useState("describe");
  const [x, setX] = useState("");
  const [y, setY] = useState("");
  const [groupBy, setGroupBy] = useState("");
  const [value, setValue] = useState("");
  const [window, setWindow] = useState(7);
  if (!dataset) return <EmptyState />;

  async function run() {
    const payload = await request("/api/analyze", {
      method: "POST",
      datasetToken: dataset.dataset_token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: dataset.dataset_id, analysis_type: analysisType, x, y, group_by: groupBy, value, window })
    });
    setAnalysis(payload);
  }

  const showX = ["correlation", "regression", "ttest"].includes(analysisType);
  const showY = ["correlation", "regression", "ttest"].includes(analysisType);
  const showGroupBy = ["groupby", "anova"].includes(analysisType);
  const showValue = ["groupby", "anova", "normality", "moving_average"].includes(analysisType);
  const showWindow = analysisType === "moving_average";

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Analyze</h2>
      <div className="grid gap-4 md:grid-cols-4">
        <Control label="Analysis">
          <select className="input" value={analysisType} onChange={(e) => setAnalysisType(e.target.value)}>
            <option value="describe">Descriptive stats</option>
            <option value="correlation">Correlation</option>
            <option value="groupby">Group by</option>
            <option value="regression">Linear regression</option>
            <option value="ttest">T-Test (Independent)</option>
            <option value="anova">ANOVA</option>
            <option value="normality">Normality Test</option>
            <option value="moving_average">Moving Average</option>
          </select>
        </Control>
        {showX && <ColumnSelect label="X Axis" dataset={dataset} value={x} onChange={setX} />}
        {showY && <ColumnSelect label="Y Axis / Target" dataset={dataset} value={y} onChange={setY} />}
        {showGroupBy && <ColumnSelect label="Group by" dataset={dataset} value={groupBy} onChange={setGroupBy} />}
        {showValue && <ColumnSelect label="Value" dataset={dataset} value={value} onChange={setValue} />}
        {showWindow && (
          <Control label="Window size">
            <input type="number" className="input" value={window} onChange={(e) => setWindow(parseInt(e.target.value))} min={2} max={365} />
          </Control>
        )}
      </div>
      <button onClick={run} className="btn-primary">Run analysis</button>
      {analysis && <ResultBlock result={analysis} />}
    </div>
  );
}

function VisualizeStep({ dataset, request, chart, setChart }) {
  const [chartType, setChartType] = useState("auto");
  const [x, setX] = useState("");
  const [y, setY] = useState("");
  const plotData = useMemo(() => buildPlot(chart, x, y), [chart, x, y]);
  if (!dataset) return <EmptyState />;

  async function run() {
    const payload = await request("/api/chart", {
      method: "POST",
      datasetToken: dataset.dataset_token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: dataset.dataset_id, chart_type: chartType, x, y })
    });
    setChart(payload);
  }

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Visualize</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <Control label="Chart">
          <select className="input" value={chartType} onChange={(e) => setChartType(e.target.value)}>
            <option value="auto">Auto suggest</option>
            <option value="bar">Bar</option>
            <option value="line">Line</option>
            <option value="scatter">Scatter</option>
            <option value="histogram">Histogram</option>
            <option value="box">Box</option>
          </select>
        </Control>
        <ColumnSelect label="X" dataset={dataset} value={x} onChange={setX} />
        <ColumnSelect label="Y" dataset={dataset} value={y} onChange={setY} />
      </div>
      <button onClick={run} className="btn-primary">Build chart</button>
      {plotData && (
        <div className="rounded-md border border-zinc-200 bg-white p-2">
          <Plot data={plotData} layout={{ autosize: true, height: 430, margin: { t: 30, r: 20, b: 50, l: 55 } }} useResizeHandler className="w-full" />
        </div>
      )}
    </div>
  );
}

function InsightsStep({ dataset, request, insights, setInsights }) {
  if (!dataset) return <EmptyState />;
  async function load() {
    const payload = await request(`/api/insights/${dataset.dataset_id}`, { datasetToken: dataset.dataset_token });
    setInsights(payload.insights);
  }
  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-semibold">Insights</h2>
      <button onClick={load} className="btn-primary">Generate insights</button>
      <div className="grid gap-3 md:grid-cols-2">
        {insights.map((item) => (
          <div key={item} className="rounded-md border border-zinc-200 bg-white p-4 text-sm">{item}</div>
        ))}
      </div>
      <Preview dataset={dataset} />
    </div>
  );
}

function NewsStep({ request, news, setNews }) {
  async function loadLatest() {
    const [latest, market] = await Promise.all([
      request("/api/news/latest?limit=30&days=7"),
      request("/api/news/market")
    ]);
    setNews((current) => ({ ...current, articles: latest.articles, total: latest.total, market }));
  }

  async function collect() {
    const collection = await request("/api/news/collect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days_for_csv: 7, send_email: false })
    });
    const latest = await request("/api/news/latest?limit=30&days=7");
    setNews((current) => ({ ...current, collection, articles: latest.articles, total: latest.total, market: { ...collection.market_snapshot, timestamp: new Date().toISOString() } }));
  }

  async function sendEmail() {
    const result = await request("/api/news/send-email?days=7", { method: "POST" });
    setNews((current) => ({ ...current, email: result }));
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">Financial News & Markets</h2>
          <p className="mt-1 text-sm text-zinc-500">Collect RSS headlines, refresh market prices, export CSV, and send a digest email.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={loadLatest} className="btn-secondary"><RefreshCw size={16} /> Refresh</button>
          <button onClick={collect} className="btn-primary"><Newspaper size={16} /> Collect feeds</button>
          <button onClick={sendEmail} className="btn-secondary"><Send size={16} /> Send email</button>
          <a href="/api/news/export-csv?days=7" className="btn-secondary">Export CSV</a>
        </div>
      </div>

      {news.collection && (
        <div className="grid gap-3 md:grid-cols-4">
          <Metric label="Collected" value={news.collection.articles_collected} />
          <Metric label="Stored" value={news.collection.articles_stored} />
          <Metric label="Sources OK" value={news.collection.sources_succeeded} />
          <Metric label="Sources Failed" value={news.collection.sources_failed} />
        </div>
      )}
      {news.email && <div className="rounded-md border border-zinc-200 bg-white p-3 text-sm">Email sent: <strong>{String(news.email.sent)}</strong> ({news.email.articles_in_digest} articles)</div>}
      {news.market && <MarketGrid market={news.market} />}
      <NewsList articles={news.articles} total={news.total} />
    </div>
  );
}

function AutomationStep({ dataset, request, insights, news }) {
  const [exportEmail, setExportEmail] = useState("");
  const [exportStatus, setExportStatus] = useState("");
  const [config, setConfig] = useState({ n8n_url: "http://localhost:5678", automation_enabled: false });

  useEffect(() => {
    request("/api/config").then(setConfig).catch(() => {});
  }, []);

  async function exportAndSendReport() {
    if (!dataset || !exportEmail) {
      setExportStatus("error: Please enter an email and ensure dataset is loaded");
      return;
    }
    try {
      setExportStatus("sending...");
      const result = await request("/api/export-report-gmail", {
        method: "POST",
        datasetToken: dataset.dataset_token,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: dataset.dataset_id,
          recipient_email: exportEmail,
          include_cleaned_csv: true,
          include_analysis: true,
          include_insights: true,
          include_news: !!news.articles?.length,
          subject: "Sairo Insights - Complete Analysis Report"
        })
      });
      setExportStatus("✓ Report sent! Check email: " + result.recipient);
    } catch (err) {
      setExportStatus("✗ " + err.message);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Workflow Automation & Export</h2>
        <p className="mt-1 text-sm text-zinc-500">Send your complete analysis (cleaned data, insights, news) via Gmail or integrate with n8n.</p>
      </div>

      {dataset && (
        <div className="rounded-md border border-blue-200 bg-blue-50 p-5 space-y-3">
          <h3 className="font-semibold text-blue-900 flex items-center gap-2">
            <Send size={20} /> Export & Send Complete Report via Gmail
          </h3>
          <p className="text-sm text-blue-800">Send all generated outputs (cleaned data, analysis, insights, news) as a ZIP archive.</p>
          <div className="flex gap-2">
            <input 
              type="email" 
              value={exportEmail} 
              onChange={(e) => setExportEmail(e.target.value)}
              placeholder="recipient@example.com"
              className="input flex-1"
            />
            <button onClick={exportAndSendReport} className="btn-primary">Send Report</button>
          </div>
          {exportStatus && (
            <div className={`text-sm p-2 rounded ${exportStatus.startsWith("✓") ? "bg-green-100 text-green-800" : exportStatus.startsWith("✗") ? "bg-red-100 text-red-800" : "bg-blue-100 text-blue-800"}`}>
              {exportStatus}
            </div>
          )}
        </div>
      )}

      <div className="grid gap-5 md:grid-cols-2">
        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <div className="flex items-center gap-3 font-semibold text-emerald-800">
            <Network size={20} /> Connect to n8n
          </div>
          <p className="mt-2 text-sm text-zinc-600">
            Use n8n to build complex automations. You can trigger Sairo Insights tasks like news collection or data exports directly from your workflows.
          </p>
          <div className="mt-4">
            <a href={config.n8n_url} target="_blank" rel="noreferrer" className="btn-primary inline-flex">
              Open n8n Dashboard
            </a>
          </div>
        </div>

        <div className="rounded-md border border-zinc-200 bg-white p-5">
          <div className="flex items-center gap-3 font-semibold text-zinc-800">
            <FileCode size={20} /> Pre-configured Workflow
          </div>
          <p className="mt-2 text-sm text-zinc-600">
            We've included a ready-to-import workflow file to get you started with daily news and market syncs.
          </p>
          <div className="mt-4">
            <a href="/app/automation/sairo_insights_workflow_enhanced.json" target="_blank" className="btn-secondary inline-flex">
              View Enhanced Workflow
            </a>
          </div>
        </div>
      </div>

      <div className="rounded-md border border-emerald-200 bg-emerald-50 p-5">
        <h3 className="font-semibold text-emerald-900">How to setup n8n automation:</h3>
        <ol className="mt-3 list-inside list-decimal space-y-2 text-sm text-emerald-800">
          <li>Ensure <strong>ADMIN_API_KEY</strong> and <strong>GMAIL_SERVICE_ACCOUNT_JSON</strong> are set in <code>.env</code>.</li>
          <li>Open your <strong>n8n</strong> dashboard and create a new workflow.</li>
          <li>Import the <code>sairo_insights_workflow_enhanced.json</code> file.</li>
          <li>Configure the <strong>HTTP Request</strong> nodes with your API Key and dataset details.</li>
          <li>Set up Gmail credentials in n8n.</li>
          <li>Activate the workflow to start automated daily syncs and email reports.</li>
        </ol>
      </div>

      <div className="rounded-md border border-zinc-200 bg-white p-5">
        <h3 className="font-semibold">Automation Status</h3>
        <div className="mt-3 flex items-center gap-2 text-sm">
          <div className={`h-2.5 w-2.5 rounded-full ${config.automation_enabled ? "bg-emerald-500" : "bg-amber-500"}`} />
          {config.automation_enabled ? (
            <span className="text-emerald-700 font-medium">Ready: ADMIN_API_KEY is configured.</span>
          ) : (
            <span className="text-amber-700 font-medium">Warning: ADMIN_API_KEY is not set. Automation endpoints will be disabled.</span>
          )}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-md border border-zinc-200 bg-white p-4">
      <div className="text-xs uppercase text-zinc-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function MarketGrid({ market }) {
  const entries = Object.entries(market).filter(([key]) => key !== "timestamp");
  return (
    <div className="rounded-md border border-zinc-200 bg-white">
      <div className="border-b border-zinc-200 px-4 py-3 font-medium">Live Market Snapshot</div>
      <div className="grid gap-px bg-zinc-200 sm:grid-cols-2 lg:grid-cols-4">
        {entries.map(([key, value]) => (
          <div key={key} className="bg-white p-3">
            <div className="text-xs uppercase text-zinc-500">{key.replaceAll("_", " ")}</div>
            <div className="mt-1 font-mono text-lg font-semibold">{value == null ? "N/A" : Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function NewsList({ articles, total }) {
  return (
    <div className="rounded-md border border-zinc-200 bg-white">
      <div className="border-b border-zinc-200 px-4 py-3 font-medium">Latest Headlines ({total || 0})</div>
      <div className="divide-y divide-zinc-100">
        {(articles || []).length === 0 && <div className="p-4 text-sm text-zinc-500">No articles collected yet. Use Collect feeds to fetch the latest headlines.</div>}
        {(articles || []).map((article) => (
          <a key={article.id} href={article.url} target="_blank" rel="noreferrer" className="block p-4 hover:bg-zinc-50">
            <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
              <span>{article.source}</span>
              <span>-</span>
              <span>{article.category}</span>
              <span>-</span>
              <span>{String(article.pub_date || "").slice(0, 10)}</span>
            </div>
            <div className="mt-1 font-medium text-zinc-950">{article.headline}</div>
            {article.summary && <p className="mt-1 line-clamp-2 text-sm text-zinc-600">{article.summary}</p>}
          </a>
        ))}
      </div>
    </div>
  );
}

function Control({ label, children }) {
  return <label className="block rounded-md border border-zinc-200 bg-white p-3 text-sm font-medium">{label}<div className="mt-2 font-normal">{children}</div></label>;
}

function ColumnSelect({ label, dataset, value, onChange }) {
  return (
    <Control label={label}>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Select column</option>
        {dataset.columns.map((col) => <option key={col} value={col}>{col}</option>)}
      </select>
    </Control>
  );
}

function Preview({ dataset }) {
  return (
    <div className="overflow-hidden rounded-md border border-zinc-200 bg-white">
      <div className="border-b border-zinc-200 px-4 py-3 font-medium">Preview</div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-100">
            <tr>{dataset.columns.map((col) => <th key={col} className="whitespace-nowrap px-3 py-2 font-medium">{col}</th>)}</tr>
          </thead>
          <tbody>
            {dataset.preview.map((row, index) => (
              <tr key={index} className="border-t border-zinc-100">
                {dataset.columns.map((col) => <td key={col} className="whitespace-nowrap px-3 py-2 text-zinc-700">{String(row[col] ?? "")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ResultBlock({ result }) {
  if (result.type === "describe") {
    return (
      <div className="overflow-hidden rounded-md border border-zinc-200 bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-100">
              <tr>
                <th className="px-3 py-2 font-medium">Metric</th>
                {result.result.map((row) => (
                  <th key={row.index} className="px-3 py-2 font-medium">{row.index}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100">
              {["count", "mean", "std", "min", "25%", "50%", "75%", "max"].map((metric) => (
                <tr key={metric}>
                  <td className="bg-zinc-50 px-3 py-2 font-medium capitalize">{metric}</td>
                  {result.result.map((row) => (
                    <td key={row.index} className="px-3 py-2 text-zinc-700">
                      {typeof row[metric] === "number" ? row[metric].toLocaleString(undefined, { maximumFractionDigits: 2 }) : row[metric]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (result.type === "regression") {
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Coefficient" value={result.coefficient.toFixed(4)} />
        <MetricCard label="Intercept" value={result.intercept.toFixed(2)} />
        <MetricCard label="R² Accuracy" value={(result.r2 * 100).toFixed(1) + "%"} />
      </div>
    );
  }

  if (result.type === "ttest" || result.type === "anova") {
    const isT = result.type === "ttest";
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label={isT ? "T-Statistic" : "F-Statistic"} value={(isT ? result.t_statistic : result.f_statistic).toFixed(4)} />
        <MetricCard label="P-Value" value={result.p_value < 0.001 ? "< 0.001" : result.p_value.toFixed(4)} />
        <div className={`rounded-md border p-4 ${result.significant ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-zinc-200 bg-white text-zinc-500"}`}>
          <div className="text-xs uppercase opacity-70">Significance</div>
          <div className="mt-1 text-xl font-semibold">{result.significant ? "Significant" : "Not Significant"}</div>
        </div>
      </div>
    );
  }

  if (result.type === "normality") {
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="W-Statistic" value={result.statistic.toFixed(4)} />
        <MetricCard label="P-Value" value={result.p_value.toFixed(4)} />
        <div className={`rounded-md border p-4 ${result.is_normal ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}>
          <div className="text-xs uppercase opacity-70">Distribution</div>
          <div className="mt-1 text-xl font-semibold">{result.is_normal ? "Likely Normal" : "Likely Non-Normal"}</div>
        </div>
      </div>
    );
  }

  if (result.type === "moving_average") {
    return (
      <div className="rounded-md border border-zinc-200 bg-white p-4">
        <div className="mb-2 text-sm font-medium text-zinc-500">Calculated Series (Last 10 values)</div>
        <div className="flex flex-wrap gap-2 font-mono text-sm">
          {result.result.slice(-10).map((v, i) => (
            <span key={i} className="rounded bg-zinc-100 px-2 py-1">{v.toFixed(2)}</span>
          ))}
        </div>
        <p className="mt-3 text-xs text-zinc-400">Showing last 10 points out of {result.result.length}. Visualize for full trend.</p>
      </div>
    );
  }

  return (
    <pre className="max-h-96 overflow-auto rounded-md border border-zinc-200 bg-zinc-950 p-4 text-xs text-zinc-50">
      {JSON.stringify(result, null, 2)}
    </pre>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-md border border-zinc-200 bg-white p-4">
      <div className="text-xs uppercase text-zinc-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function EmptyState() {
  return <div className="rounded-md border border-zinc-200 bg-white p-8 text-center text-zinc-500">Upload or load a sample dataset first.</div>;
}

function buildPlot(chart, x, y) {
  if (!chart) return null;
  const rows = chart.data || [];
  const type = chart.chart_type === "auto" ? chart.suggestion : chart.chart_type;
  if (type === "histogram") return [{ type: "histogram", x: rows.map((r) => r[x || y]) }];
  if (type === "box") return [{ type: "box", y: rows.map((r) => r[y || x]), name: y || x }];
  return [{ type: type === "line" ? "scatter" : type, mode: type === "line" ? "lines+markers" : "markers", x: rows.map((r) => r[x]), y: rows.map((r) => r[y]) }];
}

createRoot(document.getElementById("root")).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);
