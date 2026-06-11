from pathlib import Path

import pytest

from rocketsim.models.motor import Motor


def test_motor_from_dict_creates_valid_motor() -> None:
    motor = Motor.from_dict(
        {
            "name": "Example H123",
            "impulse_class": "H",
            "average_thrust": 123.0,
            "burn_time": 1.7,
            "delay": 10.0,
            "propellant_weight": 0.18,
            "thrust_curve": [
                {"time": 0.0, "thrust": 0.0},
                {"time": 0.1, "thrust": 160.0},
                {"time": 1.7, "thrust": 0.0},
            ],
        }
    )

    assert motor.name == "Example H123"
    assert motor.impulse_class == "H"
    assert motor.average_thrust == 123.0
    assert motor.thrust_curve[1] == (0.1, 160.0)


def test_motor_from_dict_requires_missing_fields() -> None:
    with pytest.raises(ValueError, match="Missing required motor field"):
        Motor.from_dict(
            {
                "name": "Incomplete Motor",
                "impulse_class": "H",
            }
        )


def test_motor_rejects_non_positive_numeric_values() -> None:
    with pytest.raises(ValueError, match="Motor field must be positive"):
        Motor.from_dict(
            {
                "name": "Bad Motor",
                "impulse_class": "H",
                "average_thrust": 0.0,
                "burn_time": 1.7,
                "delay": 10.0,
                "propellant_weight": 0.18,
                "thrust_curve": [{"time": 0.0, "thrust": 0.0}],
            }
        )


def test_motor_rejects_negative_delay() -> None:
    with pytest.raises(ValueError, match="Motor delay cannot be negative"):
        Motor.from_dict(
            {
                "name": "Bad Delay Motor",
                "impulse_class": "H",
                "average_thrust": 123.0,
                "burn_time": 1.7,
                "delay": -1.0,
                "propellant_weight": 0.18,
                "thrust_curve": [{"time": 0.0, "thrust": 0.0}],
            }
        )


def test_motor_from_yaml_loads_config(tmp_path: Path) -> None:
    motor_file = tmp_path / "motor.yaml"

    motor_file.write_text(
        """
name: YAML H123
impulse_class: H
average_thrust: 123.0
burn_time: 1.7
delay: 10.0
propellant_weight: 0.18
thrust_curve:
  - time: 0.0
    thrust: 0.0
  - time: 0.1
    thrust: 160.0
  - time: 1.7
    thrust: 0.0
""".strip(),
        encoding="utf-8",
    )

    motor = Motor.from_yaml(motor_file)

    assert motor.name == "YAML H123"
    assert motor.thrust_curve[-1] == (1.7, 0.0)
