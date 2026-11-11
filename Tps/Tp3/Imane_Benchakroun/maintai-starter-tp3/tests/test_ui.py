from pathlib import Path

from streamlit.testing.v1 import AppTest

from maintai.client import MaintaiClient

APP = str(Path(__file__).resolve().parent.parent / "ui" / "app.py")


def test_ui_shows_the_data(settings_env):
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.metric[0].value == "2000"


def test_ui_shows_the_prediction(settings_env, monkeypatch):
    # Pas de serveur ici : on remplace l'appel à l'API par une réponse connue
    fake = {"failure_probability": 0.9475, "alert": True, "threshold": 0.3, "model_version": "test"}
    monkeypatch.setattr(MaintaiClient, "predict", lambda self, releve: fake)
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()
    assert at.metric[-1].value == "95 %"
    assert "ALERTE" in at.error[0].value
