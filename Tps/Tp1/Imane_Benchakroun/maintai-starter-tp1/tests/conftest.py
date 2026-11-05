"""Fixtures partagées : données et modèle dans un dossier temporaire."""
import pytest

from maintai.dataset import make_dataset


@pytest.fixture(scope="session")
def work_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("maintai")
    make_dataset(n=2000, seed=0).to_csv(d / "sensors.csv", index=False)
    return d


@pytest.fixture
def settings_env(work_dir, monkeypatch):
    """Redirige les chemins du projet vers le dossier temporaire."""
    monkeypatch.setenv("MAINTAI_DATA_PATH", str(work_dir / "sensors.csv"))
    monkeypatch.setenv("MAINTAI_MODELS_DIR", str(work_dir / "models"))
    return work_dir


@pytest.fixture
def trained_model(settings_env):
    """Entraîne le modèle une fois, s'il n'existe pas encore."""
    from maintai.train import main

    if not (settings_env / "models" / "model.joblib").exists():
        main()
    return settings_env


@pytest.fixture
def client(trained_model):
    from fastapi.testclient import TestClient

    from maintai.api.main import app

    with TestClient(app) as c:
        yield c
