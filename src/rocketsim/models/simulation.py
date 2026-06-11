"""Simulation data models for RocketSim."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FlightState:
    """Represents one point in a vertical rocket flight simulation."""

    time_seconds: float
    altitude_meters: float
    velocity_mps: float
    acceleration_mps2: float
    mass_kg: float
    thrust_newtons: float
    drag_newtons: float


@dataclass(frozen=True)
class FlightEvent:
    """Represents a significant event during flight."""

    name: str
    time_seconds: float
    altitude_meters: float
    velocity_mps: float
    acceleration_mps2: float
    mass_kg: float


@dataclass
class SimulationResult:
    """Results from a completed flight simulation."""

    states: list[FlightState] = field(default_factory=list)
    events: list[FlightEvent] = field(default_factory=list)

    @property
    def max_altitude_meters(self) -> float:
        """Return maximum altitude achieved."""
        if not self.states:
            return 0.0

        return max(state.altitude_meters for state in self.states)

    @property
    def max_velocity_mps(self) -> float:
        """Return maximum velocity achieved."""
        if not self.states:
            return 0.0

        return max(state.velocity_mps for state in self.states)
