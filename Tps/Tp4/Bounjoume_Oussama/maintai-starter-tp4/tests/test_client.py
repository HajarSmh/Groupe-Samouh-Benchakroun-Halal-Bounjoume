import pytest

from maintai.client import APIError, MaintaiClient

VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}


def test_client_returns_prediction(client):
    api = MaintaiClient(api_key="test-key", http=client)
    assert 0 <= api.predict(VALID)["failure_probability"] <= 1


def test_client_wrong_key_raises_401(client):
    api = MaintaiClient(api_key="mauvaise", http=client)
    with pytest.raises(APIError) as e:
        api.predict(VALID)
    assert e.value.status_code == 401


def test_client_bad_reading_raises_422(client):
    api = MaintaiClient(api_key="test-key", http=client)
    with pytest.raises(APIError) as e:
        api.predict({**VALID, "temperature_c": 500})
    assert e.value.status_code == 422
