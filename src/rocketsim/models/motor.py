from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Motor:
    name: str
    impulse_class: str
    average_thrust: float
    burn_time: float
    delay: float
    propellant_weight: float
    thrust_curve: list[tuple[float, float]]
    loaded_weight: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Motor":
        required_fields = [
            "name",
            "impulse_class",
            "average_thrust",
            "burn_time",
            "delay",
            "propellant_weight",
            "thrust_curve",
            "loaded_weight",
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(
                "Missing required motor field(s): " + ", ".join(missing_fields)
            )

        motor = cls(
            name=str(data["name"]),
            impulse_class=str(data["impulse_class"]),
            average_thrust=float(data["average_thrust"]),
            burn_time=float(data["burn_time"]),
            delay=float(data["delay"]),
            propellant_weight=float(data["propellant_weight"]),
            thrust_curve=[
                (float(point["time"]), float(point["thrust"]))
                for point in data["thrust_curve"]
            ],
            loaded_weight=float(data["loaded_weight"]),
        )

        motor.validate()
        return motor

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Motor":
        config_path = Path(path)

        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError("Motor config must be a YAML mapping.")

        return cls.from_dict(data)

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Motor name is required.")

        if not self.impulse_class.strip():
            raise ValueError("Motor impulse_class is required.")

        positive_fields = {
            "average_thrust": self.average_thrust,
            "burn_time": self.burn_time,
            "propellant_weight": self.propellant_weight,
        }

        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"Motor field must be positive: {field_name}")

        if self.delay < 0:
            raise ValueError("Motor delay cannot be negative.")

        if not self.thrust_curve:
            raise ValueError("Motor thrust_curve is required.")

        for time, thrust in self.thrust_curve:
            if time < 0:
                raise ValueError("Motor thrust_curve time cannot be negative.")
            if thrust < 0:
                raise ValueError("Motor thrust_curve thrust cannot be negative.")
