from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Rocket:
    name: str
    diameter: float
    length: float
    dry_weight: float
    center_of_gravity: float
    center_of_pressure: float
    fin_count: int
    fin_root_chord: float
    fin_tip_chord: float
    fin_span: float
    fin_sweep: float
    drag_coefficient: float = 0.75

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rocket":
        required_fields = [
            "name",
            "diameter",
            "length",
            "dry_weight",
            "center_of_gravity",
            "center_of_pressure",
            "fin_count",
            "fin_root_chord",
            "fin_tip_chord",
            "fin_span",
            "fin_sweep",
            "drag_coefficient",
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(
                "Missing required rocket field(s): "
                + ", ".join(missing_fields)
            )

        rocket = cls(
            name=str(data["name"]),
            diameter=float(data["diameter"]),
            length=float(data["length"]),
            dry_weight=float(data["dry_weight"]),
            center_of_gravity=float(data["center_of_gravity"]),
            center_of_pressure=float(data["center_of_pressure"]),
            fin_count=int(data["fin_count"]),
            fin_root_chord=float(data["fin_root_chord"]),
            fin_tip_chord=float(data["fin_tip_chord"]),
            fin_span=float(data["fin_span"]),
            fin_sweep=float(data["fin_sweep"]),
            drag_coefficient=float(data["drag_coefficient"])
        )

        rocket.validate()
        return rocket

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Rocket":
        config_path = Path(path)

        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError("Rocket config must be a YAML mapping.")

        return cls.from_dict(data)

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Rocket name is required.")

        positive_fields = {
            "diameter": self.diameter,
            "length": self.length,
            "dry_weight": self.dry_weight,
            "center_of_gravity": self.center_of_gravity,
            "center_of_pressure": self.center_of_pressure,
            "fin_root_chord": self.fin_root_chord,
            "fin_tip_chord": self.fin_tip_chord,
            "fin_span": self.fin_span,
            "drag_coefficient": self.drag_coefficient,
        }

        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"Rocket field must be positive: {field_name}")

        if self.fin_count <= 0:
            raise ValueError("Rocket fin_count must be positive.")

        if self.fin_sweep < 0:
            raise ValueError("Rocket fin_sweep cannot be negative.")
