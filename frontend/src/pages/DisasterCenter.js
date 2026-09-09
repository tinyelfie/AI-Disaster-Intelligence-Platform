import React, { useState, useEffect, useCallback } from "react";
import "./DisasterCenter.css";
import DisasterMap from "../DisasterMap";

const API = "http://localhost:8000";

const TYPE_ICONS = {
  flood:      "water_drop",
  wildfire:   "local_fire_department",
  earthquake: "landscape",
  cyclone:    "cyclone",
  drought:    "wb_sunny",
  default:    "warning",
};

const RISK_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

// ── Simple markdown renderer (no external lib needed) ─────────────────────────
function SimpleMarkdown({ text }) {
  if (!text) return null;

  const lines = text.split("\n");
  const elements = [];
  let key = 0;

  for (const line of lines) {
    if (line.startsWith("## ")) {
      elements.push(<h2 key={key++} className="md-h2">{line.slice(3)}</h2>);
    } else if (line.startsWith("### ")) {
      elements.push(<h3 key={key++} className="md-h3">{line.slice(4)}</h3>);
    } else if (line.startsWith("**") && line.endsWith("**")) {
      elements.push(<p key={key++} className="md-bold">{line.slice(2, -2)}</p>);
    } else if (line.startsWith("- ")) {
      elements.push(<li key={key++} className="md-li">{line.slice(2)}</li>);
    } else if (line.startsWith("> ")) {
      elements.push(<blockquote key={key++} className="md-quote">{line.slice(2)}</blockquote>);
    } else if (line.startsWith("*") && line.endsWith("*")) {
      elements.push(<p key={key++} className="md-italic">{line.slice(1, -1)}</p>);
    } else if (line.trim() === "") {
      elements.push(<br key={key++} />);
    } else {
      // Inline bold
      const parts = line.split(/\*\*(.*?)\*\*/g);
      elements.push(
        <p key={key++} className="md-p">
          {parts.map((part, i) =>
            i % 2 === 1 ? <strong key={i}>{part}</strong> : part
          )}
        </p>
      );
    }
  }
  return <div className="dc-markdown">{elements}</div>;
}

export default function DisasterCenter({ user, onNavigate }) {
  const [disasters, setDisasters]       = useState([]);
  const [activeAlert, setActiveAlert]   = useState(null);
  const [aiOpen, setAiOpen]             = useState(true);
  const [acknowledged, setAcknowledged] = useState([]);
  const [loading, setLoading]           = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [report, setReport]             = useState(null);
  const [reportError, setReportError]   = useState(false);

  // ── Fetch live disasters ──────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    fetch(`${API}/disasters`)
      .then(r => r.json())
      .then(data => {
        if (cancelled) return;
        const sorted = [...data].sort(
          (a, b) => (RISK_ORDER[a.risk_level] ?? 4) - (RISK_ORDER[b.risk_level] ?? 4)
        );
        setDisasters(sorted);
        if (sorted.length > 0) setActiveAlert(sorted[0]);
      })
      .catch(() => { if (!cancelled) setDisasters([]); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, []);

  // ── Generate RAG situation report when active alert changes ──────────────
  const fetchReport = useCallback(async (alert) => {
    if (!alert) return;
    setReportLoading(true);
    setReport(null);
    setReportError(false);

    try {
      const res = await fetch(`${API}/situation-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          region:        alert.location_name || `${alert.latitude?.toFixed(2)}°N`,
          disaster_type: alert.disaster_type,
          severity:      alert.risk_level,
        }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setReport(data.report);
    } catch {
      setReportError(true);
    } finally {
      setReportLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeAlert) fetchReport(activeAlert);
  }, [activeAlert, fetchReport]);

  const handleAck = (id) => setAcknowledged(prev => [...prev, id]);

  const selectAlert = (d) => {
    setActiveAlert(d);
    setReport(null);
  };

  const visibleAlerts = disasters.slice(0, 6);    // show top 6 in tabs
  const liveLabel = loading
    ? "Loading..."
    : `${disasters.length} incident${disasters.length !== 1 ? "s" : ""} detected`;

  return (
    <div className="dc-root fade-in">
      {/* Top bar */}
      <header className="dc-topbar">
        <div className="dc-topbar-left">
          <div className="dc-live-badge">
            <span className={`pulse-dot${loading ? "" : " pulse-red"}`} />
            <span>{loading ? "Connecting..." : "Live Sync Active"}</span>
          </div>
          <span className="dc-sector-label">
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>location_on</span>
            {activeAlert
              ? `${activeAlert.location_name || "Unknown Region"} — ${activeAlert.disaster_type} detected`
              : liveLabel}
          </span>
        </div>
        <div className="dc-topbar-right">
          <button id="btn-new-incident"  className="btn-primary" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">add_circle</span>
            New Incident
          </button>
          <button id="btn-satellite"    className="btn-tonal"   onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">satellite_alt</span>
            Satellite Overlay
          </button>
          <button id="btn-broadcast"    className="btn-tonal"   onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">warning</span>
            Broadcast Alert
          </button>
          <button className="btn-icon" aria-label="Search" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">search</span>
          </button>
          <button className="btn-icon" aria-label="Notifications" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">notifications</span>
          </button>
        </div>
      </header>

      <div className="dc-body">
        {/* Map panel — Leaflet live map */}
        <div className="dc-map-panel">
          {disasters.length > 0 ? (
            <DisasterMap
              disasters={disasters}
              onSelectDisaster={selectAlert}
            />
          ) : (
            <div className="dc-map-bg">
              {loading && (
                <div className="dc-map-loading">
                  <span className="material-symbols-outlined spin" style={{ fontSize: 36 }}>
                    progress_activity
                  </span>
                  <p>Loading disaster feed...</p>
                </div>
              )}
            </div>
          )}

          {/* Map controls */}
          <div className="dc-map-controls">
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Fullscreen">
              <span className="material-symbols-outlined">fullscreen</span>
            </button>
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Zoom in">
              <span className="material-symbols-outlined">add</span>
            </button>
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Zoom out">
              <span className="material-symbols-outlined">remove</span>
            </button>
          </div>

          <div className="dc-map-label">Disaster Center — Global Monitoring</div>
        </div>

        {/* AI Analysis sidebar */}
        <div className={`dc-ai-panel${aiOpen ? "" : " dc-ai-collapsed"}`}>
          <div className="dc-ai-header" onClick={() => setAiOpen(!aiOpen)}>
            <div className="dc-ai-title-row">
              <span className="material-symbols-outlined dc-ai-icon">psychology</span>
              <span className="dc-ai-title">AI Analysis</span>
              <span className="dc-ai-live-chip">
                <span className={`pulse-dot${reportLoading ? "" : " pulse-red"}`} />
                {reportLoading ? "Generating..." : "Live"}
              </span>
            </div>
            <span className="material-symbols-outlined dc-ai-chevron">
              {aiOpen ? "expand_more" : "chevron_right"}
            </span>
          </div>

          {aiOpen && (
            <div className="dc-ai-body slide-in">
              {/* Alert tabs */}
              {visibleAlerts.length > 0 && (
                <div className="dc-alert-tabs">
                  {visibleAlerts.map(d => {
                    const level = d.risk_level?.toLowerCase() || "medium";
                    return (
                      <button
                        key={d.id}
                        className={`dc-alert-tab${activeAlert?.id === d.id ? " active" : ""} dc-alert-tab-${level}`}
                        onClick={() => selectAlert(d)}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                          {TYPE_ICONS[d.disaster_type] || TYPE_ICONS.default}
                        </span>
                        <span className={`badge badge-${level}`}>{d.risk_level}</span>
                        <span className="dc-alert-tab-time">
                          {d.location_name || d.disaster_type}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Active alert card */}
              {loading && !activeAlert ? (
                <div className="dc-loading-state">
                  <span className="material-symbols-outlined spin">progress_activity</span>
                  <p>Loading incidents...</p>
                </div>
              ) : activeAlert ? (
                <div className="dc-alert-card">
                  <div className="dc-alert-card-header">
                    <span className={`badge badge-${activeAlert.risk_level?.toLowerCase()}`}>
                      <span className="material-symbols-outlined" style={{ fontSize: 11 }}>warning</span>
                      {activeAlert.risk_level} Alert
                    </span>
                    <span className="dc-alert-time">
                      {activeAlert.disaster_type?.charAt(0).toUpperCase() + activeAlert.disaster_type?.slice(1)}
                    </span>
                  </div>
                  <h3 className="dc-alert-title">
                    {activeAlert.disaster_type?.charAt(0).toUpperCase() + activeAlert.disaster_type?.slice(1)} —{" "}
                    {activeAlert.location_name || `${activeAlert.latitude?.toFixed(2)}°N, ${activeAlert.longitude?.toFixed(2)}°E`}
                  </h3>

                  {/* Contextual data */}
                  <div className="dc-context-section">
                    <p className="dc-context-label">Sensor Data</p>
                    <div className="dc-context-item">
                      <div className="dc-context-icon-wrap">
                        <span className="material-symbols-outlined">analytics</span>
                      </div>
                      <div>
                        <p className="dc-context-title">Severity Score</p>
                        <p className="dc-context-desc">
                          {Math.round((activeAlert.severity_score || 0) * 100)}% — Confidence: {Math.round((activeAlert.confidence || 0) * 100)}%
                        </p>
                      </div>
                    </div>
                    <div className="dc-context-item">
                      <div className="dc-context-icon-wrap">
                        <span className="material-symbols-outlined">groups</span>
                      </div>
                      <div>
                        <p className="dc-context-title">Population at Risk</p>
                        <p className="dc-context-desc">
                          {activeAlert.population_at_risk?.toLocaleString() || "Unknown"} people
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Escalation probability */}
                  <div className="dc-prob-section">
                    <div className="dc-prob-header">
                      <span className="dc-prob-label">Severity Index</span>
                      <span
                        className="dc-prob-value"
                        style={{
                          color: (activeAlert.severity_score || 0) > 0.75
                            ? "var(--error)"
                            : "var(--secondary)",
                        }}
                      >
                        {Math.round((activeAlert.severity_score || 0) * 100)}%
                      </span>
                    </div>
                    <div className="progress-track">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${Math.round((activeAlert.severity_score || 0) * 100)}%`,
                          background: (activeAlert.severity_score || 0) > 0.75
                            ? "var(--error)"
                            : "var(--primary)",
                        }}
                      />
                    </div>
                  </div>

                  {/* Action buttons */}
                  <div className="dc-alert-actions">
                    <button
                      id={`btn-view-details-${activeAlert.id}`}
                      className="btn-primary"
                      style={{ flex: 1 }}
                      onClick={() => onNavigate("reports")}
                    >
                      View Reports
                    </button>
                    <button
                      id={`btn-acknowledge-${activeAlert.id}`}
                      className={`btn-outline${acknowledged.includes(activeAlert.id) ? " acknowledged" : ""}`}
                      style={{ flex: 1 }}
                      onClick={() => handleAck(activeAlert.id)}
                      disabled={acknowledged.includes(activeAlert.id)}
                    >
                      {acknowledged.includes(activeAlert.id) ? "✓ Acknowledged" : "Acknowledge"}
                    </button>
                  </div>

                  {/* RAG situation report */}
                  <div className="dc-rag-section">
                    <div className="dc-rag-header">
                      <span className="material-symbols-outlined dc-ai-icon">auto_awesome</span>
                      <span>AI Situation Report</span>
                      {reportLoading && (
                        <span className="material-symbols-outlined spin" style={{ fontSize: 16 }}>
                          progress_activity
                        </span>
                      )}
                    </div>
                    {reportLoading ? (
                      <div className="dc-rag-loading">
                        <div className="skeleton" style={{ height: 14, width: "90%", marginBottom: 8 }} />
                        <div className="skeleton" style={{ height: 14, width: "75%", marginBottom: 8 }} />
                        <div className="skeleton" style={{ height: 14, width: "85%", marginBottom: 8 }} />
                        <div className="skeleton" style={{ height: 14, width: "60%" }} />
                      </div>
                    ) : reportError ? (
                      <p className="dc-rag-error">
                        Could not generate report. Check that the backend is running.
                      </p>
                    ) : report ? (
                      <div className="dc-rag-body">
                        <SimpleMarkdown text={report} />
                      </div>
                    ) : null}
                  </div>
                </div>
              ) : (
                <div className="dc-loading-state">
                  <span className="material-symbols-outlined">check_circle</span>
                  <p>No active incidents</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
