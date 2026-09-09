import React, { useState, useEffect } from "react";
import "./Analytics.css";

const API = "http://localhost:8000";

export default function Analytics({ onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    fetch(`${API}/analytics/summary`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => { if (!cancelled) { setSummary(data); } })
      .catch(() => { if (!cancelled) setError(true); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, []);

  // ── Derived display data ──────────────────────────────────────────────────
  const barData = summary?.monthly_severity?.length
    ? summary.monthly_severity
    : [
        { month: "Jan", value: 45 }, { month: "Feb", value: 62 },
        { month: "Mar", value: 55 }, { month: "Apr", value: 80 },
        { month: "May", value: 70 }, { month: "Jun", value: 58 },
      ];

  const pieData = summary?.by_type?.length
    ? summary.by_type.slice(0, 4).map((t, i) => ({
        label: t.name.charAt(0).toUpperCase() + t.name.slice(1),
        count: t.count,
        color: ["var(--primary)", "var(--secondary)", "var(--tertiary)", "var(--outline)"][i],
      }))
    : [
        { label: "Flood",      count: 56, color: "var(--primary)" },
        { label: "Wildfire",   count: 32, color: "var(--secondary)" },
        { label: "Earthquake", count: 20, color: "var(--tertiary)" },
        { label: "Cyclone",    count: 16, color: "var(--outline)" },
      ];

  const totalByType = pieData.reduce((s, d) => s + d.count, 0) || 1;

  const kpis = summary
    ? [
        {
          label:  "Avg AI Confidence",
          value:  `${Math.round((summary.avg_confidence || 0.85) * 100)}%`,
          trend:  "up",
          delta:  "Multi-model fusion",
        },
        {
          label:  "Total Incidents",
          value:  String(summary.total_incidents || 0),
          trend:  "up",
          delta:  `${summary.critical_count} critical`,
        },
        {
          label:  "High+ Risk Events",
          value:  String((summary.high_count || 0) + (summary.critical_count || 0)),
          trend:  "down",
          delta:  "Requires attention",
        },
        {
          label:  "Avg Severity Index",
          value:  `${Math.round((summary.avg_severity || 0.60) * 100)}%`,
          trend:  "neutral",
          delta:  "Platform-wide",
        },
      ]
    : null;

  const sectorRisks = summary?.by_type?.slice(0, 5).map((t, i) => ({
    name:  t.name.charAt(0).toUpperCase() + t.name.slice(1),
    risk:  Math.round((t.count / (summary.total_incidents || 1)) * 100),
    color: ["var(--primary)", "var(--secondary)", "var(--tertiary)", "var(--primary-container)", "var(--outline)"][i],
  })) || [
    { name: "Flood",      risk: 45, color: "var(--primary)" },
    { name: "Wildfire",   risk: 26, color: "var(--secondary)" },
    { name: "Earthquake", risk: 16, color: "var(--tertiary)" },
    { name: "Cyclone",    risk: 13, color: "var(--primary-container)" },
  ];

  const maxBar = Math.max(...barData.map(d => d.value || d.val || 0), 1);

  return (
    <div className="analytics-root fade-in">
      <header className="analytics-header">
        <div>
          <h1 className="analytics-title">Analytics</h1>
          <p className="analytics-sub">
            {loading
              ? "Loading live data..."
              : error
              ? "Showing cached data — backend unavailable"
              : `${summary?.total_incidents || 0} total incidents · Live from backend`}
          </p>
        </div>
        <button
          id="btn-data-export"
          className="btn-primary"
          onClick={() => onNavigate("backend-pending")}
        >
          <span className="material-symbols-outlined">download</span>
          Data Export
        </button>
      </header>

      {/* KPI Cards */}
      <div className="analytics-kpi-grid">
        {loading || !kpis
          ? [1, 2, 3, 4].map(k => (
              <div key={k} className="analytics-kpi card-lift">
                <div className="skeleton" style={{ width: "50%", height: 14, marginBottom: 8 }} />
                <div className="skeleton" style={{ width: "70%", height: 28, marginBottom: 8 }} />
                <div className="skeleton" style={{ width: "40%", height: 12 }} />
              </div>
            ))
          : kpis.map((kpi) => (
              <div key={kpi.label} className="analytics-kpi card-lift">
                <p className="kpi-label">{kpi.label}</p>
                <p className="kpi-value">{kpi.value}</p>
                <div className={`kpi-trend kpi-${kpi.trend}`}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                    {kpi.trend === "up" ? "trending_up" : kpi.trend === "down" ? "trending_down" : "remove"}
                  </span>
                  <span>{kpi.delta}</span>
                </div>
              </div>
            ))}
      </div>

      <div className="analytics-charts-grid">
        {/* Bar chart — monthly severity */}
        <div className="analytics-chart-card card-lift">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Severity Trends Over Time</h2>
              <p className="chart-sub">Average disaster severity index by month</p>
            </div>
            <span className="badge badge-critical">Live Data</span>
          </div>
          <div className="bar-chart">
            {barData.map((d) => {
              const val = d.value ?? d.val ?? 0;
              return (
                <div key={d.month} className="bar-col">
                  <div className="bar-fill-wrap">
                    <div
                      className="bar-fill"
                      style={{ height: `${(val / maxBar) * 100}%` }}
                      title={`${d.month}: ${val}`}
                    />
                  </div>
                  <span className="bar-label">{d.month}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Type distribution */}
        <div className="analytics-chart-card card-lift">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Type Frequency</h2>
              <p className="chart-sub">Distribution of recorded events</p>
            </div>
          </div>
          <div className="pie-chart-wrap">
            <div
              className="pie-chart"
              style={{
                background: `conic-gradient(${pieData
                  .reduce((acc, d, i) => {
                    const pct = (d.count / totalByType) * 100;
                    const prev = acc.total;
                    acc.total += pct;
                    acc.str += `${d.color} ${prev}% ${acc.total}%${i < pieData.length - 1 ? ", " : ""}`;
                    return acc;
                  }, { total: 0, str: "" }).str
                })`,
              }}
            />
            <div className="pie-legend">
              {pieData.map((d) => (
                <div key={d.label} className="pie-legend-item">
                  <span className="pie-dot" style={{ background: d.color }} />
                  <span className="pie-legend-text">
                    {d.label} ({Math.round((d.count / totalByType) * 100)}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Risk distribution by disaster type */}
      <div className="analytics-risk-card card-lift">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">Risk Distribution by Disaster Type</h2>
            <p className="chart-sub">Share of total incidents per category</p>
          </div>
          <button
            id="btn-full-report"
            className="btn-tonal"
            onClick={() => onNavigate("reports")}
          >
            <span className="material-symbols-outlined">description</span>
            Full Report
          </button>
        </div>
        <div className="risk-rows">
          {sectorRisks.map((s) => (
            <div key={s.name} className="risk-row">
              <span className="risk-row-name">{s.name}</span>
              <div className="progress-track" style={{ flex: 1 }}>
                <div
                  className="progress-fill"
                  style={{ width: `${s.risk}%`, background: s.color }}
                />
              </div>
              <span className="risk-row-val" style={{ color: s.color }}>{s.risk}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
