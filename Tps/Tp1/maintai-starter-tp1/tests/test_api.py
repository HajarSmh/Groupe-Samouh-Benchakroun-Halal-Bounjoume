from fastapi.testclient import TestClient

from maintai.api.main import app

HEADERS = {}
VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}
HIGH_RISK = {"temperature_c": 85.0, "vibration_mm_s": 9.0, "load_pct": 95.0, "runtime_hours": 19000}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "model_loaded": True}


def test_predict_returns_probability(client):
    r = client.post("/v1/predict", json=VALID, headers=HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["failure_probability"] <= 1
    assert isinstance(body["alert"], bool)


def test_high_risk_reading_raises_alert(client):
    r = client.post("/v1/predict", json=HIGH_RISK, headers=HEADERS)
    assert r.json()["alert"] is True


def test_out_of_range_value_is_rejected(client):
    r = client.post("/v1/predict", json={**VALID, "temperature_c": 500}, headers=HEADERS)
    assert r.status_code == 422


def test_missing_field_is_rejected(client):
    incomplete = {k: v for k, v in VALID.items() if k != "load_pct"}
    r = client.post("/v1/predict", json=incomplete, headers=HEADERS)
    assert r.status_code == 422


def test_503_when_model_missing(settings_env, monkeypatch, tmp_path):
    monkeypatch.setenv("MAINTAI_MODELS_DIR", str(tmp_path / "empty"))
    with TestClient(app) as c:
        r = c.post("/v1/predict", json=VALID, headers=HEADERS)
    assert r.status_code == 503


def test_openapi_documents_predict(client):
    assert "/v1/predict" in client.get("/openapi.json").json()["paths"]
