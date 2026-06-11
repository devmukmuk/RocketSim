"""Tests for SimulationService."""

from rocketsim.models.motor import Motor
from rocketsim.models.rocket import Rocket
from rocketsim.services.simulation_service import SimulationService


def make_test_rocket() -> Rocket:
    """Create a reusable test rocket."""
    return Rocket(
        name="Test Rocket",
        diameter=0.1016,
        length=1.0,
        dry_weight=1.5,
        center_of_gravity=0.4,
        center_of_pressure=0.7,
        fin_count=3,
        fin_root_chord=0.15,
        fin_tip_chord=0.08,
        fin_span=0.10,
        fin_sweep=0.05,
        drag_coefficient=0.75,
    )


def make_test_motor() -> Motor:
    """Create a reusable test motor."""
    return Motor(
        name="Test Motor",
        impulse_class="H",
        average_thrust=120.0,
        burn_time=2.0,
        delay=8.0,
        propellant_weight=0.15,
        thrust_curve=[
            (0.0, 120.0),
            (2.0, 0.0),
        ],
    )


def test_simulation_generates_states() -> None:
    result = SimulationService().simulate(
        rocket=make_test_rocket(),
        motor=make_test_motor(),
    )

    assert len(result.states) > 10


def test_simulation_detects_core_events() -> None:
    result = SimulationService().simulate(
        rocket=make_test_rocket(),
        motor=make_test_motor(),
    )

    event_names = [event.name for event in result.events]

    assert "liftoff" in event_names
    assert "burnout" in event_names
    assert "max_velocity" in event_names
    assert "apogee" in event_names
    assert "deployment" in event_names


def test_simulation_reports_positive_apogee_and_velocity() -> None:
    result = SimulationService().simulate(
        rocket=make_test_rocket(),
        motor=make_test_motor(),
    )

    assert result.max_altitude_meters > 0
    assert result.max_velocity_mps > 0


def test_simulation_starts_with_full_mass() -> None:
    rocket = make_test_rocket()
    motor = make_test_motor()

    result = SimulationService().simulate(
        rocket=rocket,
        motor=motor,
    )

    assert result.states[0].mass_kg == rocket.dry_weight + motor.propellant_weight


def test_simulation_burns_propellant_mass() -> None:
    rocket = make_test_rocket()
    motor = make_test_motor()

    result = SimulationService().simulate(
        rocket=rocket,
        motor=motor,
    )

    assert result.states[-1].mass_kg < result.states[0].mass_kg
    assert result.states[-1].mass_kg >= rocket.dry_weight
