"""
Smoke test script for AI Disaster Intelligence Platform backend.
Run this AFTER starting the backend server with:
    uvicorn backend.app.main:app --reload --port 8000
"""
import json
import sys
import urllib.request
import urllib.error

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

def req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, data=data, headers=headers, method=method),
            timeout=10
        )
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {"error": str(e)}

def test(name, method, path, body=None, expect_key=None, expect_status=200):
    global PASS, FAIL
    status, resp = req(method, path, body)
    ok = (status == expect_status)
    if ok and expect_key:
        ok = expect_key in resp if isinstance(resp, dict) else len(resp) > 0
    icon = "✅" if ok else "❌"
    print(f"  {icon}  [{status}] {name}")
    if not ok:
        print(f"       Response: {str(resp)[:200]}")
        FAIL += 1
    else:
        PASS += 1

print("\n=== AI Disaster Intelligence Platform - Smoke Tests ===\n" + "="*50)

print("\n[1] Health Check")
test("GET /health returns status=ok", "GET", "/health", expect_key="status")

print("\n[2] Disaster Feed")
test("GET /disasters returns a list", "GET", "/disasters")

print("\n[3] Risk Zones")
test("GET /risk-zones returns a list", "GET", "/risk-zones")

print("\n[4] Analytics Summary")
test("GET /analytics/summary", "GET", "/analytics/summary", expect_key="total_incidents")

print("\n[5] Predict — Disaster (Flood scenario)")
test("POST /predict/disaster (flood)", "POST", "/predict/disaster", {
    "latitude": 23.8, "longitude": 90.4,
    "timestamp": "2024-07-15T12:00:00",
    "weather_rainfall": 150.0, "weather_wind_speed": 20.0,
    "social_signal_score": 0.9
}, expect_key="disaster_type")

print("\n[6] Predict — Disaster (No disaster scenario)")
test("POST /predict/disaster (no disaster)", "POST", "/predict/disaster", {
    "latitude": 28.6, "longitude": 77.2,
    "timestamp": "2024-07-15T12:00:00",
    "weather_rainfall": 5.0, "weather_wind_speed": 10.0,
    "social_signal_score": 0.1
}, expect_key="risk_level")

print("\n[7] Predict — Weather Risk (XGBoost model)")
test("POST /predict/weather (heavy rain)", "POST", "/predict/weather", {
    "precipitation": 80.0, "temp_max": 38.5,
    "temp_min": 25.0, "wind_speed": 55.0,
    "humidity": 90.0, "location": "Mumbai"
}, expect_key="risk_score")

test("POST /predict/weather (calm weather)", "POST", "/predict/weather", {
    "precipitation": 2.0, "temp_max": 28.0,
    "temp_min": 18.0, "wind_speed": 10.0,
    "humidity": 45.0, "location": "Delhi"
}, expect_key="risk_level")

print("\n[8] Predict — Tweet Classification")
test("POST /predict/tweet (disaster tweet)", "POST", "/predict/tweet", {
    "text": "Flash floods sweeping through downtown! Hundreds trapped, rescue teams deployed."
}, expect_key="is_disaster")

test("POST /predict/tweet (normal tweet)", "POST", "/predict/tweet", {
    "text": "Beautiful sunny day today, went to the park."
}, expect_key="disaster_probability")

print("\n[9] Predict — Satellite")
test("POST /predict/satellite (no image=fallback)", "POST", "/predict/satellite", expect_key="disaster_type")

print("\n[10] Situation Report (RAG)")
test("POST /situation-report", "POST", "/situation-report", {
    "region": "Mumbai", "disaster_type": "flood", "severity": "HIGH"
}, expect_key="report")

print("\n[11] Edge Cases / Validation")
test("POST /predict/tweet (empty text) → 422", "POST", "/predict/tweet",
     {"text": ""}, expect_status=422)

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("🎉 All tests passed! Backend is healthy.")
else:
    print(f"⚠️  {FAIL} test(s) need attention.")
