from maintai.cli import main


def test_cli_prints_the_prediction(trained_model, capsys):
    assert main(["72", "6", "85", "15000"]) == 0
    assert "Probabilité de panne" in capsys.readouterr().out


def test_cli_without_model_says_where_it_looked(settings_env, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("MAINTAI_MODELS_DIR", str(tmp_path / "vide"))
    assert main(["72", "6", "85", "15000"]) == 1
    assert "Modèle introuvable" in capsys.readouterr().err
