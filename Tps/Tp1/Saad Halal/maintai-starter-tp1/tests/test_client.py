VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}


def test_500_degres_est_refuse(client):
    # client : une fixture de conftest.py
    r = client.post("/v1/predict", json={**VALID, "temperature_c": 500})

    assert r.status_code == 422
