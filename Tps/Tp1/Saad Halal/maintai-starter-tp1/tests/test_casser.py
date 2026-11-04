import pytest

HEADERS = {"X-API-Key": "test-key"}

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}

CAS_REFUSES = [
    # (description, url, corps, code attendu)
    # 1. Champ manquant
    (
        "champ manquant",
        "/v1/predict",
        {k: v for k, v in VALID.items() if k != "temperature_c"},
        422,
    ),
    # 2. Valeur absurde
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 600}, 422),
    # 3. Texte au lieu d'un nombre
    (
        "texte au lieu d'un nombre",
        "/v1/predict",
        {**VALID, "temperature_c": "chaud"},
        422,
    ),
    # 4. Champ en trop
    ("champ en trop", "/v1/predict", {**VALID, "champ_en_trop": 123}, 422),
    # 5. Mauvaise route
    ("mauvaise route", "/v1/doc", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    response = client.post(url, json=corps, headers=HEADERS)

    assert response.status_code == attendu, (
        f"{description} : attendu {attendu}, "
        f"obtenu {response.status_code}. "
        f"Réponse : {response.text}"
    )
