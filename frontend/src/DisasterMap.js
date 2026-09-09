/**
 * DisasterMap.js
 * ================
 * Leaflet map with:
 *  - Color-coded custom SVG markers per risk level (CRITICAL → red, HIGH → orange, etc.)
 *  - Rich popups with disaster type, severity, coordinates
 *  - Risk zone rectangle overlays (fetched from /risk-zones on mount)
 *  - Click-to-select passes the disaster object up to the parent
 */
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Rectangle, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const API = "http://localhost:8000";

// ── Custom SVG marker factory ──────────────────────────────────────────────────
const RISK_COLORS = {
  CRITICAL: "#ba1a1a",
  HIGH:     "#b02614",
  MEDIUM:   "#765a05",
  LOW:      "#41606e",
};

const TYPE_LABELS = {
  flood:      "💧",
  wildfire:   "🔥",
  earthquake: "🏔️",
  cyclone:    "🌀",
  drought:    "☀️",
};

function makeIcon(riskLevel, disasterType) {
  const color = RISK_COLORS[riskLevel] || RISK_COLORS.MEDIUM;
  const emoji = TYPE_LABELS[disasterType] || "⚠️";

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="44" viewBox="0 0 36 44">
      <filter id="shadow">
        <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
      </filter>
      <path d="M18 0 C8.06 0 0 8.06 0 18 C0 31.5 18 44 18 44 C18 44 36 31.5 36 18 C36 8.06 27.94 0 18 0Z"
            fill="${color}" filter="url(#shadow)"/>
      <circle cx="18" cy="18" r="12" fill="white" opacity="0.2"/>
      <text x="18" y="23" text-anchor="middle" font-size="13">${emoji}</text>
    </svg>
  `;

  return L.divIcon({
    className: "",
    html: `<div style="width:36px;height:44px;">${svg}</div>`,
    iconSize: [36, 44],
    iconAnchor: [18, 44],
    popupAnchor: [0, -44],
  });
}

// ── Severity → zone rectangle color ───────────────────────────────────────────
const ZONE_COLORS = {
  CRITICAL: { color: "#ba1a1a", fillColor: "#ba1a1a", fillOpacity: 0.08, weight: 2 },
  HIGH:     { color: "#b02614", fillColor: "#b02614", fillOpacity: 0.06, weight: 1.5 },
  MEDIUM:   { color: "#765a05", fillColor: "#765a05", fillOpacity: 0.05, weight: 1 },
  LOW:      { color: "#41606e", fillColor: "#41606e", fillOpacity: 0.04, weight: 1 },
};

export default function DisasterMap({ disasters = [], onSelectDisaster }) {
  const [riskZones, setRiskZones] = useState([]);

  // Fetch risk zones once
  useEffect(() => {
    fetch(`${API}/risk-zones`)
      .then(r => r.ok ? r.json() : [])
      .then(data => setRiskZones(data))
      .catch(() => {});
  }, []);

  const center = disasters.length > 0
    ? [disasters[0].latitude, disasters[0].longitude]
    : [20.5937, 78.9629];   // default: India centre

  return (
    <MapContainer
      center={center}
      zoom={5}
      className="disaster-map"
      zoomControl={false}
    >
      {/* Dark satellite-style tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Risk zone rectangles */}
      {riskZones.map(zone => {
        if (!zone.bounds) return null;
        const { north, south, east, west } = zone.bounds;
        const style = ZONE_COLORS[zone.severity] || ZONE_COLORS.LOW;
        return (
          <Rectangle
            key={`zone-${zone.id}`}
            bounds={[[south, west], [north, east]]}
            pathOptions={style}
          >
            <Tooltip sticky>
              <strong>{zone.name}</strong><br />
              Severity: {zone.severity}<br />
              {zone.description}
            </Tooltip>
          </Rectangle>
        );
      })}

      {/* Disaster markers */}
      {disasters.map(d => (
        <Marker
          key={d.id}
          position={[d.latitude, d.longitude]}
          icon={makeIcon(d.risk_level, d.disaster_type)}
          eventHandlers={{
            click: () => onSelectDisaster?.(d),
          }}
        >
          <Popup>
            <div style={{ minWidth: 160, fontFamily: "Manrope, sans-serif" }}>
              <div style={{
                fontWeight: 700, fontSize: 13, marginBottom: 6,
                color: RISK_COLORS[d.risk_level] || "#333",
                textTransform: "uppercase", letterSpacing: "0.05em",
              }}>
                {d.risk_level} — {d.disaster_type}
              </div>
              <div style={{ fontSize: 12, color: "#555", lineHeight: 1.6 }}>
                <div>📍 {d.location_name || `${d.latitude?.toFixed(2)}°N, ${d.longitude?.toFixed(2)}°E`}</div>
                <div>📊 Severity: <strong>{Math.round((d.severity_score || 0) * 100)}%</strong></div>
                <div>🤖 Confidence: <strong>{Math.round((d.confidence || 0) * 100)}%</strong></div>
                {d.population_at_risk && (
                  <div>👥 {d.population_at_risk.toLocaleString()} at risk</div>
                )}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
