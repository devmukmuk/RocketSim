from pathlib import Path

import pytest

from rocketsim.models.rocket import Rocket


def test_rocket_from_dict_creates_valid_rocket() -> None:
    rocket = Rocket.from_dict(
        {
            "name": "Example Rocket",
            "diameter": 4.0,
            "length": 45.0,
            "dry_weight": 48.0,
            "center_of_gravity": 26.0,
            "center_of_pressure": 32.0,
            "fin_count": 4,
            "fin_root_chord": 6.0,
            "fin_tip_chord": 3.0,
            "fin_span": 4.0,
            "fin_sweep": 2.0,
        }
    )

    assert rocket.name == "Example Rocket"
    assert rocket.fin_count == 4
    assert rocket.diameter == 4.0


def test_rocket_from_dict_requires_missing_fields() -> None:
    with pytest.raises(ValueError, match="Missing required rocket field"):
        Rocket.from_dict(
            {
                "name": "Incomplete Rocket",
                "diameter": 4.0,
            }
        )


def test_rocket_rejects_non_positive_numeric_values() -> None:
    with pytest.raises(ValueError, match="Rocket field must be positive"):
        Rocket.from_dict(
            {
                "name": "Bad Rocket",
                "diameter": 0.0,
                "length": 45.0,
                "dry_weight": 48.0,
                "center_of_gravity": 26.0,
                "center_of_pressure": 32.0,
                "fin_count": 4,
                "fin_root_chord": 6.0,
                "fin_tip_chord": 3.0,
                "fin_span": 4.0,
                "fin_sweep": 2.0,
            }
        )


def test_rocket_from_yaml_loads_config(tmp_path: Path) -> None:
    rocket_file = tmp_path / "rocket.yaml"

    rocket_file.write_text(
        """
name: YAML Rocket
diameter: 4.0
length: 45.0
dry_weight: 48.0
center_of_gravity: 26.0
center_of_pressure: 32.0
fin_count: 4
fin_root_chord: 6.0
fin_tip_chord: 3.0
fin_span: 4.0
fin_sweep: 2.0
""".strip(),
        encoding="utf-8",
    )

    rocket = Rocket.from_yaml(rocket_file)

    assert rocket.name == "YAML Rocket"
    assert rocket.length == 45.0
