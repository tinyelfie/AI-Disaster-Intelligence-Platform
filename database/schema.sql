-- ============================================================
--  AI Disaster Intelligence Platform — Database Schema
--  Standard SQL / SQLite Compatible (zero-setup)
-- ============================================================

-- Table: disasters
-- Historical disaster events and real-time inference results
CREATE TABLE IF NOT EXISTS disasters (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_type       VARCHAR(64)     NOT NULL,
    severity_score      FLOAT           NOT NULL,
    risk_level          VARCHAR(16)     NOT NULL,   -- LOW | MEDIUM | HIGH | CRITICAL
    population_at_risk  INTEGER         NOT NULL DEFAULT 0,
    confidence          FLOAT           NOT NULL DEFAULT 0.0,
    latitude            FLOAT           NOT NULL,
    longitude           FLOAT           NOT NULL,
    location_name       VARCHAR(256),
    country             VARCHAR(128),
    description         TEXT,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_disasters_risk_level    ON disasters(risk_level);
CREATE INDEX IF NOT EXISTS idx_disasters_created_at    ON disasters(created_at);
CREATE INDEX IF NOT EXISTS idx_disasters_disaster_type ON disasters(disaster_type);

-- Table: predictions
-- Logs every model inference call for audit + analytics
CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          VARCHAR(32)     NOT NULL,   -- satellite | tweet | weather | fusion
    input_data      TEXT,                       -- JSON encoded string
    output_data     TEXT,                       -- JSON encoded string
    disaster_type   VARCHAR(64),
    risk_level      VARCHAR(16),
    confidence      FLOAT,
    latency_ms      INTEGER,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_source     ON predictions(source);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);

-- Table: risk_zones
-- Geographic risk zones with GeoJSON polygon data for the map overlay
CREATE TABLE IF NOT EXISTS risk_zones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(256)    NOT NULL,
    severity    VARCHAR(16)     NOT NULL,   -- LOW | MEDIUM | HIGH | CRITICAL
    zone_type   VARCHAR(64),               -- flood_plain | fire_risk | seismic | coastal
    geometry    TEXT            NOT NULL,  -- Standard GeoJSON Polygon string
    description TEXT,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_zones_severity ON risk_zones(severity);

-- Default risk zones with GeoJSON polygons
INSERT OR IGNORE INTO risk_zones (id, name, severity, zone_type, geometry, description)
VALUES
    (
        1,
        'Bay of Bengal Coastal Strip',
        'CRITICAL',
        'coastal',
        '{"type":"Polygon","coordinates":[[[85,15],[92,15],[92,22],[85,22],[85,15]]]}',
        'High cyclone and storm surge risk along the Bay of Bengal coastline'
    ),
    (
        2,
        'Indo-Gangetic Flood Plain',
        'HIGH',
        'flood_plain',
        '{"type":"Polygon","coordinates":[[[75,24],[88,24],[88,30],[75,30],[75,24]]]}',
        'Monsoon flood-prone alluvial plain — annual inundation risk'
    ),
    (
        3,
        'Western Ghats Fire Zone',
        'HIGH',
        'fire_risk',
        '{"type":"Polygon","coordinates":[[[74,8],[78,8],[78,21],[74,21],[74,8]]]}',
        'Dense forest cover with high wildfire risk in dry season'
    ),
    (
        4,
        'Himalayan Seismic Belt',
        'MEDIUM',
        'seismic',
        '{"type":"Polygon","coordinates":[[[72,27],[97,27],[97,36],[72,36],[72,27]]]}',
        'Active tectonic zone with moderate to high earthquake probability'
    ),
    (
        5,
        'Rajasthan Drought Zone',
        'MEDIUM',
        'drought',
        '{"type":"Polygon","coordinates":[[[69,24],[78,24],[78,30],[69,30],[69,24]]]}',
        'Arid region with persistent drought and heat wave risk'
    );
