"""Rocket flight simulation service."""

from math import pi

from rocketsim.models.motor import Motor
from rocketsim.models.rocket import Rocket
from rocketsim.models.simulation import FlightEvent, FlightState, SimulationResult
from rocketsim.physics.flight import step_flight_state


class SimulationService:
    """Runs a simple vertical rocket flight simulation."""

    def simulate(
        self,
        rocket: Rocket,
        motor: Motor,
        step_seconds: float = 0.05,
        max_time_seconds: float = 60.0,
    ) -> SimulationResult:
        """Run a complete vertical flight simulation."""
        if step_seconds <= 0:
            raise ValueError("step_seconds must be greater than zero.")

        if max_time_seconds <= 0:
            raise ValueError("max_time_seconds must be greater than zero.")

        result = SimulationResult()

        reference_area_m2 = pi * (rocket.diameter / 2.0) ** 2
        initial_mass_kg = rocket.dry_weight + motor.propellant_weight

        current_state = FlightState(
            time_seconds=0.0,
            altitude_meters=0.0,
            velocity_mps=0.0,
            acceleration_mps2=0.0,
            mass_kg=initial_mass_kg,
            thrust_newtons=0.0,
            drag_newtons=0.0,
        )

        result.states.append(current_state)

        liftoff_recorded = False
        burnout_recorded = False
        max_velocity_recorded = False
        apogee_recorded = False
        landing_recorded = False

        peak_velocity_state = current_state
        previous_state = current_state

        while current_state.time_seconds < max_time_seconds:
            thrust_newtons = self._thrust_at_time(
                motor=motor,
                time_seconds=current_state.time_seconds,
            )

            current_state = step_flight_state(
                state=current_state,
                step_seconds=step_seconds,
                thrust_newtons=thrust_newtons,
                drag_coefficient=rocket.drag_coefficient,
                reference_area_m2=reference_area_m2,
                propellant_mass_kg=motor.propellant_weight,
                burn_time_seconds=motor.burn_time,
            )

            result.states.append(current_state)

            if current_state.velocity_mps > peak_velocity_state.velocity_mps:
                peak_velocity_state = current_state

            if not liftoff_recorded and current_state.altitude_meters > 0.01:
                self._add_event(result, "liftoff", current_state)
                liftoff_recorded = True

            if (
                not burnout_recorded
                and previous_state.time_seconds < motor.burn_time
                and current_state.time_seconds >= motor.burn_time
            ):
                self._add_event(result, "burnout", current_state)
                burnout_recorded = True

            if (
                not max_velocity_recorded
                and peak_velocity_state.time_seconds > 0
                and current_state.velocity_mps < peak_velocity_state.velocity_mps
            ):
                self._add_event(result, "max_velocity", peak_velocity_state)
                max_velocity_recorded = True

            if (
                not apogee_recorded
                and previous_state.velocity_mps > 0
                and current_state.velocity_mps <= 0
            ):
                self._add_event(result, "apogee", current_state)
                self._add_event(result, "deployment", current_state)
                apogee_recorded = True

            if (
                apogee_recorded
                and not landing_recorded
                and current_state.altitude_meters <= 0
            ):
                self._add_event(result, "landing", current_state)
                landing_recorded = True
                break

            previous_state = current_state

        return result

    def _thrust_at_time(self, motor: Motor, time_seconds: float) -> float:
        """Return motor thrust at the requested simulation time."""
        if time_seconds >= motor.burn_time:
            return 0.0

        if not motor.thrust_curve:
            return motor.average_thrust

        sorted_curve = sorted(motor.thrust_curve)

        previous_time, previous_thrust = sorted_curve[0]

        if time_seconds <= previous_time:
            return previous_thrust

        for next_time, next_thrust in sorted_curve[1:]:
            if time_seconds <= next_time:
                time_span = next_time - previous_time

                if time_span <= 0:
                    return next_thrust

                time_fraction = (time_seconds - previous_time) / time_span
                return previous_thrust + (
                    (next_thrust - previous_thrust) * time_fraction
                )

            previous_time = next_time
            previous_thrust = next_thrust

        return motor.average_thrust

    def _add_event(
        self,
        result: SimulationResult,
        name: str,
        state: FlightState,
    ) -> None:
        """Add a flight event from a flight state."""
        result.events.append(
            FlightEvent(
                name=name,
                time_seconds=state.time_seconds,
                altitude_meters=state.altitude_meters,
                velocity_mps=state.velocity_mps,
            )
        )
