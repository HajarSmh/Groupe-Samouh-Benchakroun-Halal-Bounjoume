import json

from maintai.config import FEATURES, get_settings


def test_training_writes_artifacts(trained_model):
    s = get_settings()
    assert s.model_path.exists()
    assert s.info_path.exists()
    assert s.metrics_path.exists()


def test_info_is_the_input_contract(trained_model):
    info = json.loads(get_settings().info_path.read_text(encoding="utf-8"))
    assert info["features"] == FEATURES
    assert 0 < info["threshold"] < 1


def test_model_beats_baseline(trained_model):
    metrics = json.loads(get_settings().metrics_path.read_text(encoding="utf-8"))
    assert metrics["model"]["recall"] > metrics["baseline"]["recall"]
    assert set(metrics["model"]) >= {"accuracy", "recall", "precision", "threshold"}
