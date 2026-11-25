from importlib.metadata import entry_points, version

import maintai


def test_installed_version_matches_the_code():
    # Échoue tant que le package n'est pas installé (pip install -e .)
    assert version("maintai") == maintai.__version__


def test_command_is_declared():
    noms = [e.name for e in entry_points(group="console_scripts")]
    assert "maintai-predict" in noms
