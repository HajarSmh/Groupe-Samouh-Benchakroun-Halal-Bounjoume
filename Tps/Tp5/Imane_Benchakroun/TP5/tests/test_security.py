VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}


def test_missing_key_is_rejected(client):
    assert client.post("/v1/predict", json=VALID).status_code == 401


def test_wrong_key_is_rejected(client):
    r = client.post("/v1/predict", json=VALID, headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_health_stays_public(client):
    assert client.get("/health").status_code == 200


def test_cors_allows_local_web_client(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5500",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-api-key",
    })
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5500"


def test_cors_refuses_unknown_origin(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://evil.example",
        "Access-Control-Request-Method": "POST",
    })
    assert "access-control-allow-origin" not in r.headers
