"""Tests for basic RocketSim vertical flight physics."""

import pytest

from rocketsim.models.simulation import FlightState
from rocketsim.physics.flight import (
    GRAVITY_MPS2,
    calculate_acceleration_mps2,
    calculate_burned_mass_kg,
    calculate_drag_newtons,
    step_flight_state,
)


def test_gravity_only_acceleration_is_negative() -> None:
    acceleration = calculate_acceleration_mps2(
        thrust_newtons=0.0,
        drag_newtons=0.0,
        mass_kg=1.0,
        velocity_mps=0.0,
    )

    assert acceleration == pytest.approx(-GRAVITY_MPS2)


def test_thrust_greater_than_weight_produces_upward_acceleration() -> None:
    acceleration = calculate_acceleration_mps2(
        thrust_newtons=20.0,
        drag_newtons=0.0,
        mass_kg=1.0,
        velocity_mps=0.0,
    )

    assert acceleration > 0


def test_drag_opposes_upward_velocity() -> None:
    acceleration_without_drag = calculate_acceleration_mps2(
        thrust_newtons=20.0,
        drag_newtons=0.0,
        mass_kg=1.0,
        velocity_mps=10.0,
    )

    acceleration_with_drag = calculate_acceleration_mps2(
        thrust_newtons=20.0,
        drag_newtons=5.0,
        mass_kg=1.0,
        velocity_mps=10.0,
    )

    assert acceleration_with_drag < acceleration_without_drag


def test_drag_opposes_downward_velocity() -> None:
    acceleration = calculate_acceleration_mps2(
        thrust_newtons=0.0,
        drag_newtons=5.0,
        mass_kg=1.0,
        velocity_mps=-10.0,
    )

    assert acceleration > -GRAVITY_MPS2


def test_drag_calculation_is_positive_for_nonzero_velocity() -> None:
    drag = calculate_drag_newtons(
        velocity_mps=20.0,
        drag_coefficient=0.75,
        reference_area_m2=0.01,
    )

    assert drag > 0


def test_burned_mass_decreases_during_burn() -> None:
    burned_mass = calculate_burned_mass_kg(
        propellant_mass_kg=0.2,
        burn_time_seconds=2.0,
        elapsed_time_seconds=0.0,
        step_seconds=0.5,
    )

    assert burned_mass == pytest.approx(0.05)


def test_burned_mass_is_zero_after_burnout() -> None:
    burned_mass = calculate_burned_mass_kg(
        propellant_mass_kg=0.2,
        burn_time_seconds=2.0,
        elapsed_time_seconds=2.0,
        step_seconds=0.5,
    )

    assert burned_mass == 0.0


def test_step_flight_state_advances_time_velocity_altitude_and_mass() -> None:
    state = FlightState(
        time_seconds=0.0,
        altitude_meters=0.0,
        velocity_mps=0.0,
        acceleration_mps2=0.0,
        mass_kg=1.0,
        thrust_newtons=0.0,
        drag_newtons=0.0,
    )

    next_state = step_flight_state(
        state=state,
        step_seconds=0.1,
        thrust_newtons=20.0,
        drag_coefficient=0.75,
        reference_area_m2=0.01,
        propellant_mass_kg=0.2,
        burn_time_seconds=2.0,
    )

    assert next_state.time_seconds == pytest.approx(0.1)
    assert next_state.velocity_mps > 0
    assert next_state.altitude_meters > 0
    assert next_state.mass_kg < state.mass_kg
