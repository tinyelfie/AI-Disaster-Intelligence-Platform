import React, { useState, useEffect } from "react";
import "./Reports.css";

const API = "http://localhost:8000";

const TYPE_OPTIONS = ["All Types", "flood", "wildfire", "earthquake", "cyclone", "drought"];
const RISK_OPTIONS = ["All Risks", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

const TYPE_ICONS = {
  flood:      "water_drop",
  wildfire:   "local_fire_department",
  earthquake: "landscape",
  cyclone:    "cyclone",
  drought:    "wb_sunny",
  default:    "warning",
};

// ── Simple markdown renderer ────────────────────────────────────────────────────
function SimpleMarkdown({ text }) {
  if (!text) return null;
  const lines = text.split("\n");
  const els = [];
  let k = 0;
  for (const line of lines) {
    if (line.startsWith("## "))      els.push(<h2 key={k++} style={{ fontSize: 15, fontWeight: 800, margin: "10px 0 4px" }}>{line.slice(3)}</h2>);
    else if (line.startsWith("### ")) els.push(<h3 key={k++} style={{ fontSize: 13, fontWeight: 700, color: "var(--primary)", margin: "8px 0 3px" }}>{line.slice(4)}</h3>);
    else if (line.startsWith("- "))   els.push(<li key={k++} style={{ marginLeft: 16, marginBottom: 3 }}>{line.slice(2)}</li>);
    else if (line.trim() === "")      els.push(<br key={k++} />);
    else {
      const parts = line.split(/\*\*(.*?)\*\*/g);
      els.push(<p key={k++} style={{ margin: "3px 0", fontSize: 13, lineHeight: 1.6 }}>{parts.map((p, i) => i % 2 === 1 ? <strong key={i}>{p}</strong> : p)}</p>);
    }
  }
  return <div>{els}</div>;
}

export default function Reports({ onNavigate }) {
  const [disasters, setDisasters] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [riskFilter, setRiskFilter] = useState("All Risks");
  const [search, setSearch]         = useState("");

  // Report generation modal state
  const [generating, setGenerating] = useState(false);
  const [genTarget, setGenTarget]   = useState(null);   // the disaster to report on
  const [report, setReport]         = useState(null);
  const [reportLoading, setReportLoading] = useState(false);

  // ── Fetch live disasters ──────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API}/disasters`)
      .then(r => r.json())
      .then(data => { if (!cancelled) setDisasters(data); })
      .catch(() => { if (!cancelled) setDisasters([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  // ── Filter logic ──────────────────────────────────────────────────────────
  const filtered = disasters.filter(r => {
    const matchType = typeFilter === "All Types" || r.disaster_type === typeFilter;
    const matchRisk = riskFilter === "All Risks" || r.risk_level === riskFilter;
    const matchSearch = !search || r.disaster_type?.toLowerCase().includes(search.toLowerCase()) ||
      r.location_name?.toLowerCase().includes(search.toLowerCase());
    return matchType && matchRisk && matchSearch;
  });

  // ── Generate report ───────────────────────────────────────────────────────
  const handleGenerate = async (disaster) => {
    setGenTarget(disaster);
    setGenerating(true);
    setReport(null);
    setReportLoading(true);

    try {
      const res = await fetch(`${API}/situation-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          region:        disaster.location_name || `${disaster.latitude?.toFixed(2)}°N`,
          disaster_type: disaster.disaster_type,
          severity:      disaster.risk_level,
        }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setReport(data.report);
    } catch {
      setReport("*Could not generate report. Please check that the backend is running.*");
    } finally {
      setReportLoading(false);
    }
  };

  const fmtDate = (ts) => {
    try {
      return new Date(ts).toLocaleString("en-US", {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
      });
    } catch { return ts; }
  };

  return (
    <div className="reports-root fade-in">
      <header className="reports-header">
        <div>
          <h1 className="reports-title">Reports</h1>
          <p className="reports-sub">
            {loading ? "Loading..." : `${filtered.length} incidents · Click any row to generate an AI report`}
          </p>
        </div>
        <button
          id="btn-generate-report"
          className="btn-primary"
          onClick={() => disasters[0] && handleGenerate(disasters[0])}
          disabled={loading || disasters.length === 0}
        >
          <span className="material-symbols-outlined">auto_awesome</span>
          Generate AI Report
        </button>
      </header>

      {/* Filters */}
      <div className="reports-filters">
        <div className="reports-search-wrap">
          <span className="material-symbols-outlined reports-search-icon">search</span>
          <input
            type="search"
            className="tech-input reports-search"
            placeholder="Search by type or location..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <select
          className="tech-input reports-select"
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
        >
          {TYPE_OPTIONS.map(o => (
            <option key={o}>{o === "All Types" ? o : o.charAt(0).toUpperCase() + o.slice(1)}</option>
          ))}
        </select>

        <select
          className="tech-input reports-select"
          value={riskFilter}
          onChange={e => setRiskFilter(e.target.value)}
        >
          {RISK_OPTIONS.map(o => <option key={o}>{o}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="reports-table-wrap card-lift">
        {loading ? (
          <div className="reports-loading">
            <span className="material-symbols-outlined spin">progress_activity</span>
            <p>Loading incidents from backend...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="reports-loading">
            <span className="material-symbols-outlined">search_off</span>
            <p>No incidents match your filters.</p>
          </div>
        ) : (
          <table className="reports-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Risk Level</th>
                <th>Location</th>
                <th>Timestamp</th>
                <th>Severity</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => {
                const level = r.risk_level?.toLowerCase();
                const icon  = TYPE_ICONS[r.disaster_type] || TYPE_ICONS.default;
                return (
                  <tr
                    key={r.id}
                    className="reports-row"
                    onClick={() => handleGenerate(r)}
                    title="Click to generate AI situation report"
                  >
                    <td className="reports-id">#{r.id}</td>
                    <td>
                      <div className="reports-type-cell">
                        <span className="reports-type-icon">
                          <span className="material-symbols-outlined">{icon}</span>
                        </span>
                        {r.disaster_type?.charAt(0).toUpperCase() + r.disaster_type?.slice(1)}
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${level}`}>{r.risk_level}</span>
                    </td>
                    <td className="reports-location">
                      {r.location_name || `${r.latitude?.toFixed(2)}°N, ${r.longitude?.toFixed(2)}°E`}
                    </td>
                    <td className="reports-time">{fmtDate(r.created_at)}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div className="progress-track" style={{ width: 60 }}>
                          <div
                            className="progress-fill"
                            style={{ width: `${Math.round((r.severity_score || 0) * 100)}%` }}
                          />
                        </div>
                        <span style={{ fontSize: 12, color: "var(--on-surface-variant)" }}>
                          {Math.round((r.severity_score || 0) * 100)}%
                        </span>
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn-icon"
                        id={`btn-view-${r.id}`}
                        onClick={e => { e.stopPropagation(); handleGenerate(r); }}
                        aria-label="Generate report"
                      >
                        <span className="material-symbols-outlined">auto_awesome</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {/* Pagination info */}
        {!loading && filtered.length > 0 && (
          <div className="reports-pagination">
            <span className="reports-count">
              Showing {filtered.length} of {disasters.length} incidents
            </span>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="reports-footer">
        <span>© 2024 Terra-Aura Intelligence</span>
        <div className="reports-footer-links">
          {["Terms & Conditions", "Privacy Policy", "Contact", "Support"].map(l => (
            <button key={l} className="reports-footer-link" onClick={() => onNavigate("legal")}>{l}</button>
          ))}
        </div>
      </footer>

      {/* AI Situation Report Modal */}
      {generating && (
        <div className="modal-overlay" onClick={() => setGenerating(false)}>
          <div className="modal-card slide-in reports-modal" onClick={e => e.stopPropagation()}>
            <div className="reports-modal-header">
              <span className="material-symbols-outlined modal-icon icon-fill" style={{ color: "var(--primary)" }}>
                auto_awesome
              </span>
              <div>
                <h3 className="modal-title">
                  AI Situation Report
                </h3>
                <p style={{ fontSize: 12, color: "var(--on-surface-variant)", marginTop: 2 }}>
                  {genTarget?.disaster_type?.charAt(0).toUpperCase() + genTarget?.disaster_type?.slice(1)} —{" "}
                  {genTarget?.risk_level} severity
                </p>
              </div>
            </div>

            {reportLoading ? (
              <div className="reports-modal-loading">
                <div className="spinner" />
                <p>Generating AI report using RAG pipeline...</p>
                <p style={{ fontSize: 11, opacity: 0.6 }}>Retrieving context · Calling Gemini 1.5 Flash</p>
              </div>
            ) : (
              <div className="reports-modal-body">
                <SimpleMarkdown text={report} />
              </div>
            )}

            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              <button
                className="btn-primary"
                style={{ flex: 1 }}
                onClick={() => onNavigate("disaster-center")}
              >
                View on Map
              </button>
              <button className="btn-outline" onClick={() => setGenerating(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
