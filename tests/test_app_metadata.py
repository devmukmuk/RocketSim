# tests/test_app_metadata.py

from rocketsim import __app_name__, __version__


def test_app_metadata() -> None:
    assert __app_name__ == "RocketSim"
    assert __version__ == "2026.6.0"