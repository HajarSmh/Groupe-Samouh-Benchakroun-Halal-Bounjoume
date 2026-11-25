import json

import mlflow
import mlflow.sklearn

from maintai.config import FEATURES, get_settings
from maintai.tracking import EXPERIMENT, file_md5
from maintai.train import main


def last_run():
    runs = mlflow.search_runs(experiment_names=[EXPERIMENT], order_by=["start_time DESC"])
    assert len(runs) >= 1, "aucun run MLflow : log_run n'a rien enregistré"
    return runs.iloc[0]


def test_training_creates_a_run(trained_model):
    r = last_run()
    assert r["params.model"] == "logreg"
    assert r["params.C"] == "1.0"


def test_run_records_metrics(trained_model):
    r = last_run()
    assert 0 <= r["metrics.recall"] <= 1
    assert r["metrics.recall"] > r["metrics.baseline_recall"]


def test_run_records_data_version(trained_model):
    assert last_run()["params.data_md5"] == file_md5(get_settings().data_path)


def test_run_stores_the_model(trained_model):
    model = mlflow.sklearn.load_model(f"runs:/{last_run()['run_id']}/model")
    X = [[72, 6, 85, 15000]]
    import pandas as pd
    assert 0 <= model.predict_proba(pd.DataFrame(X, columns=FEATURES))[0, 1] <= 1


def test_options_change_the_run(trained_model, monkeypatch, tmp_path):
    monkeypatch.setenv("MAINTAI_MODELS_DIR", str(tmp_path / "models"))
    main(["--model", "forest", "--threshold", "0.4"])
    r = last_run()
    assert r["params.model"] == "forest"
    assert r["params.threshold"] == "0.4"
    info = json.loads((tmp_path / "models" / "model_info.json").read_text(encoding="utf-8"))
    assert info["threshold"] == 0.4
