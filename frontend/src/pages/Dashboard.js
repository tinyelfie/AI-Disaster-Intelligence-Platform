import React, { useState, useEffect } from "react";
import "./Dashboard.css";

const API = "http://localhost:8000";

// ── Risk level → icon mapping ──────────────────────────────────────────────────
const TYPE_ICONS = {
  flood:      "water_drop",
  wildfire:   "local_fire_department",
  earthquake: "landscape",
  cyclone:    "cyclone",
  drought:    "wb_sunny",
  default:    "warning",
};

const RISK_TO_LEVEL = {
  CRITICAL: "critical",
  HIGH:     "high",
  MEDIUM:   "medium",
  LOW:      "low",
};

// ── Skeleton loaders ───────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="dash-stat-card card-lift" style={{ animation: "none", cursor: "default" }}>
      <div className="skeleton" style={{ width: 40, height: 40, borderRadius: 10, marginBottom: 12 }} />
      <div className="skeleton" style={{ width: "60%", height: 24, marginBottom: 8 }} />
      <div className="skeleton" style={{ width: "40%", height: 14 }} />
    </div>
  );
}

function SkeletonRow() {
  return (
    <div className="dash-incident-row" style={{ cursor: "default" }}>
      <div className="skeleton" style={{ width: 40, height: 40, borderRadius: 10 }} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
        <div className="skeleton" style={{ width: "55%", height: 14 }} />
        <div className="skeleton" style={{ width: "35%", height: 12 }} />
      </div>
    </div>
  );
}

export default function Dashboard({ user, onNavigate }) {
  const [disasters, setDisasters]   = useState([]);
  const [summary, setSummary]       = useState(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(false);

  // ── Fetch data on mount ──────────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      setLoading(true);
      setError(false);
      try {
        const [disRes, sumRes] = await Promise.all([
          fetch(`${API}/disasters`),
          fetch(`${API}/analytics/summary`),
        ]);
        if (!disRes.ok || !sumRes.ok) throw new Error("API error");
        const dis = await disRes.json();
        const sum = await sumRes.json();
        if (!cancelled) {
          setDisasters(dis);
          setSummary(sum);
        }
      } catch {
        if (!cancelled) setError(true);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();
    return () => { cancelled = true; };
  }, []);

  // ── Derived stats from live data ───────────────────────────────────────────
  const quickStats = summary
    ? [
        {
          label: "Active Incidents",
          value: String(summary.total_incidents),
          icon:  "warning",
          color: "var(--primary)",
          delta: `${summary.critical_count} critical`,
        },
        {
          label: "AI Confidence",
          value: `${Math.round((summary.avg_confidence || 0.85) * 100)}%`,
          icon:  "psychology",
          color: "var(--secondary)",
          delta: "Multi-model fusion",
        },
        {
          label: "Sectors Monitored",
          value: "47",
          icon:  "radar",
          color: "var(--tertiary)",
          delta: "Global coverage",
        },
        {
          label: "Avg Severity",
          value: `${Math.round((summary.avg_severity || 0.60) * 100)}%`,
          icon:  "speed",
          color: "#16a34a",
          delta: `${summary.high_count + summary.critical_count} high-risk`,
        },
      ]
    : null;

  const incidents = disasters.slice(0, 5);   // show top 5 on dashboard

  const systemStatuses = [
    { label: "AI Prediction Engine", status: "online" },
    { label: "Satellite Feed",        status: "online" },
    { label: "Alert Broadcast",       status: "online" },
    { label: "Backend API",           status: error ? "offline" : "online" },
    { label: "Database",              status: error ? "pending" : "online" },
  ];

  return (
    <div className="dash-root fade-in">
      {/* Welcome banner */}
      <div className="dash-welcome">
        <div className="dash-welcome-text">
          <p className="dash-welcome-greeting">
            Good day, {user?.name?.split(" ")[0] || "Analyst"}
          </p>
          <h1 className="dash-welcome-title">Operations Dashboard</h1>
          <p className="dash-welcome-sub">
            Global monitoring active ·{" "}
            {new Date().toLocaleDateString("en-US", {
              weekday: "long", year: "numeric", month: "long", day: "numeric",
            })}
          </p>
        </div>
        <div className="dash-welcome-live">
          <div className="dash-live-indicator">
            <span className={`pulse-dot${error ? " pulse-red" : ""}`} />
            <span>{error ? "Connection Error" : "Live Sync Active"}</span>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="dash-stats-grid">
        {loading || !quickStats
          ? [1, 2, 3, 4].map((k) => <SkeletonCard key={k} />)
          : quickStats.map((stat) => (
              <button
                key={stat.label}
                className="dash-stat-card card-lift"
                onClick={() => onNavigate("analytics")}
                id={`btn-stat-${stat.label.replace(/ /g, "-").toLowerCase()}`}
              >
                <div
                  className="dash-stat-icon-wrap"
                  style={{ background: `${stat.color}18` }}
                >
                  <span
                    className="material-symbols-outlined"
                    style={{ color: stat.color }}
                  >
                    {stat.icon}
                  </span>
                </div>
                <div className="dash-stat-info">
                  <p className="dash-stat-value" style={{ color: stat.color }}>
                    {stat.value}
                  </p>
                  <p className="dash-stat-label">{stat.label}</p>
                  <p className="dash-stat-delta">{stat.delta}</p>
                </div>
              </button>
            ))}
      </div>

      {/* Main content */}
      <div className="dash-main-grid">
        {/* Active incidents */}
        <div className="dash-incidents card-lift">
          <div className="dash-section-header">
            <h2 className="dash-section-title">Active Incidents</h2>
            <button
              className="btn-tonal"
              id="btn-view-all-incidents"
              onClick={() => onNavigate("reports")}
            >
              <span className="material-symbols-outlined">description</span>
              View All
            </button>
          </div>
          <div className="dash-incident-list">
            {loading
              ? [1, 2, 3, 4].map((k) => <SkeletonRow key={k} />)
              : error
              ? (
                  <div className="dash-empty-state">
                    <span className="material-symbols-outlined">cloud_off</span>
                    <p>Could not connect to backend. Start the API server.</p>
                  </div>
                )
              : incidents.length === 0
              ? (
                  <div className="dash-empty-state">
                    <span className="material-symbols-outlined">check_circle</span>
                    <p>No active incidents at this time.</p>
                  </div>
                )
              : incidents.map((inc) => {
                  const level = RISK_TO_LEVEL[inc.risk_level] || "medium";
                  const icon  = TYPE_ICONS[inc.disaster_type] || TYPE_ICONS.default;
                  const sev   = Math.round((inc.severity_score || 0) * 100);
                  return (
                    <div
                      key={inc.id}
                      className="dash-incident-row"
                      onClick={() => onNavigate("disaster-center")}
                      role="button"
                      tabIndex={0}
                    >
                      <div className={`dash-incident-icon dash-incident-icon-${level}`}>
                        <span className="material-symbols-outlined">{icon}</span>
                      </div>
                      <div className="dash-incident-info">
                        <p className="dash-incident-type">
                          {inc.disaster_type.charAt(0).toUpperCase() + inc.disaster_type.slice(1)}
                        </p>
                        <p className="dash-incident-sector">
                          {inc.location_name ||
                            `${inc.latitude?.toFixed(2)}°N, ${inc.longitude?.toFixed(2)}°E`}
                        </p>
                      </div>
                      <div className="dash-incident-right">
                        <span className={`badge badge-${level}`}>
                          {inc.risk_level}
                        </span>
                        <div className="dash-severity-bar">
                          <div
                            className="dash-severity-fill"
                            style={{
                              width: `${sev}%`,
                              background:
                                level === "critical" ? "var(--error)" :
                                level === "high"     ? "var(--primary)" :
                                "var(--secondary)",
                            }}
                          />
                        </div>
                        <span className="dash-severity-val">{sev}%</span>
                      </div>
                      <span className="material-symbols-outlined dash-incident-chevron">
                        chevron_right
                      </span>
                    </div>
                  );
                })}
          </div>
        </div>

        {/* Quick actions + system status */}
        <div className="dash-actions-col">
          <div className="dash-quick-actions card-lift">
            <h2 className="dash-section-title">Quick Actions</h2>
            <div className="dash-action-grid">
              {[
                { label: "Disaster Center", icon: "map",         page: "disaster-center", accent: "primary" },
                { label: "Run Analytics",   icon: "bar_chart",   page: "analytics",       accent: "secondary" },
                { label: "Generate Report", icon: "description", page: "reports",         accent: "tertiary" },
                { label: "New Incident",    icon: "add_circle",  page: "backend-pending", accent: "primary" },
                { label: "Broadcast Alert", icon: "warning",     page: "backend-pending", accent: "error" },
                { label: "Satellite View",  icon: "satellite_alt",page: "backend-pending",accent: "tertiary" },
              ].map((action) => (
                <button
                  key={action.label}
                  id={`btn-quick-${action.label.replace(/ /g, "-").toLowerCase()}`}
                  className="dash-action-btn"
                  onClick={() => onNavigate(action.page)}
                  style={{ "--accent": `var(--${action.accent})` }}
                >
                  <span className="material-symbols-outlined dash-action-icon">
                    {action.icon}
                  </span>
                  <span className="dash-action-label">{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* System status */}
          <div className="dash-system-card card-lift">
            <h2 className="dash-section-title">System Status</h2>
            <div className="dash-system-list">
              {systemStatuses.map((sys) => (
                <div key={sys.label} className="dash-system-row">
                  <span className="dash-system-label">{sys.label}</span>
                  <span className={`dash-system-dot dash-dot-${sys.status}`} />
                </div>
              ))}
            </div>
            <button
              className="btn-tonal"
              style={{ width: "100%", marginTop: 8 }}
              id="btn-system-status"
              onClick={() => onNavigate("system-status")}
            >
              <span className="material-symbols-outlined">security</span>
              Full Status Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
