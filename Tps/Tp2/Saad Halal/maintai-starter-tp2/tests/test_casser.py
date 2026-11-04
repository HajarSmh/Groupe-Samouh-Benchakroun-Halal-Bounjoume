import pytest

HEADERS = {"X-API-Key": "test-key"}

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}

CAS_REFUSES = [
    (
        "vibration manquante",
        "/v1/predict",
        {k: v for k, v in VALID.items() if k != "vibration_mm_s"},
        422,
    ),
    ("vibration trop elevee", "/v1/predict", {**VALID, "vibration_mm_s": 800}, 422),
    (
        "vibration non numerique",
        "/v1/predict",
        {**VALID, "vibration_mm_s": "eleve"},
        422,
    ),
    ("champ en trop", "/v1/predict", {**VALID, "champ_inconnu": 123}, 422),
    ("mauvaise route", "/doc", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    r = client.post(url, json=corps, headers=HEADERS)

    assert r.status_code == attendu, (
        f"{description} : attendu {attendu}, obtenu {r.status_code}"
    )
