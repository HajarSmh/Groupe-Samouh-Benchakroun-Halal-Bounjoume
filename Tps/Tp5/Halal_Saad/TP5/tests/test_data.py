import pytest

from maintai.config import FEATURES, TARGET
from maintai.data import load_data, split
from maintai.dataset import make_dataset


def test_dataset_has_expected_columns():
    df = make_dataset(n=500)
    assert list(df.columns) == FEATURES + [TARGET]
    assert set(df[TARGET].unique()) <= {0, 1}


def test_load_data_rejects_missing_column(tmp_path):
    path = tmp_path / "bad.csv"
    make_dataset(n=100).drop(columns="load_pct").to_csv(path, index=False)
    with pytest.raises(ValueError, match="load_pct"):
        load_data(path)


def test_split_keeps_failure_rate():
    _, _, y_train, y_test = split(make_dataset(n=2000))
    assert abs(y_train.mean() - y_test.mean()) < 0.02
