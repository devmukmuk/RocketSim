"""Basic vertical flight physics for RocketSim."""

from rocketsim.models.simulation import FlightState

# Standard gravitational acceleration at Earth's surface.
#
# Units:
#   meters / second²
#
# Source:
#   International standard gravity
#
# Notes:
#   For Phase 2 we assume:
#   - constant gravity
#   - sea-level launch conditions
#   - altitude effects are ignored
#
# Future enhancements:
#   - gravity variation with altitude
#   - planetary body support (Moon, Mars, etc.)
GRAVITY_MPS2 = 9.80665


# Standard sea-level air density.
#
# Units:
#   kilograms / cubic meter
#
# Source:
#   International Standard Atmosphere (ISA)
#
# Notes:
#   For Phase 2 we assume:
#   - sea-level conditions
#   - 15°C temperature
#   - standard pressure
#   - dry air
#
# This constant is used by the drag model:
#
#   Drag = 0.5 * rho * V² * Cd * A
#
# where:
#   rho = air density
#   V   = velocity
#   Cd  = drag coefficient
#   A   = reference area
#
# Future enhancements:
#   - air density as a function of altitude
#   - temperature corrections
#   - pressure corrections
#   - humidity corrections
#   - weather profile integration
#   - full atmosphere/environment model
#
# Eventually this constant will likely move into an
# Environment model/service and be computed dynamically.
AIR_DENSITY_KG_M3 = 1.225


def calculate_drag_newtons(
    velocity_mps: float,
    drag_coefficient: float,
    reference_area_m2: float,
    air_density_kg_m3: float = AIR_DENSITY_KG_M3,
) -> float:
    """Calculate drag force magnitude in newtons."""
    return (
        0.5
        * air_density_kg_m3
        * velocity_mps
        * velocity_mps
        * drag_coefficient
        * reference_area_m2
    )


def calculate_acceleration_mps2(
    thrust_newtons: float,
    drag_newtons: float,
    mass_kg: float,
    velocity_mps: float,
) -> float:
    """Calculate net vertical acceleration."""
    if mass_kg <= 0:
        raise ValueError("mass_kg must be greater than zero")

    drag_direction = -1 if velocity_mps >= 0 else 1
    drag_force = drag_direction * drag_newtons

    net_force = thrust_newtons + drag_force - (mass_kg * GRAVITY_MPS2)
    return net_force / mass_kg


def calculate_burned_mass_kg(
    propellant_mass_kg: float,
    burn_time_seconds: float,
    elapsed_time_seconds: float,
    step_seconds: float,
) -> float:
    """Calculate propellant mass burned during one simulation step."""
    if propellant_mass_kg <= 0 or burn_time_seconds <= 0:
        return 0.0

    if elapsed_time_seconds >= burn_time_seconds:
        return 0.0

    remaining_burn_time = burn_time_seconds - elapsed_time_seconds
    active_step_seconds = min(step_seconds, remaining_burn_time)
    burn_rate_kg_s = propellant_mass_kg / burn_time_seconds

    return burn_rate_kg_s * active_step_seconds


def step_flight_state(
    state: FlightState,
    step_seconds: float,
    thrust_newtons: float,
    drag_coefficient: float,
    reference_area_m2: float,
    propellant_mass_kg: float,
    burn_time_seconds: float,
) -> FlightState:
    """Advance a vertical flight state by one time step."""
    if step_seconds <= 0:
        raise ValueError("step_seconds must be greater than zero")

    drag_newtons = calculate_drag_newtons(
        velocity_mps=state.velocity_mps,
        drag_coefficient=drag_coefficient,
        reference_area_m2=reference_area_m2,
    )

    acceleration_mps2 = calculate_acceleration_mps2(
        thrust_newtons=thrust_newtons,
        drag_newtons=drag_newtons,
        mass_kg=state.mass_kg,
        velocity_mps=state.velocity_mps,
    )

    next_velocity_mps = state.velocity_mps + acceleration_mps2 * step_seconds
    next_altitude_meters = state.altitude_meters + next_velocity_mps * step_seconds

    burned_mass_kg = calculate_burned_mass_kg(
        propellant_mass_kg=propellant_mass_kg,
        burn_time_seconds=burn_time_seconds,
        elapsed_time_seconds=state.time_seconds,
        step_seconds=step_seconds,
    )

    next_mass_kg = max(state.mass_kg - burned_mass_kg, 0.001)

    return FlightState(
        time_seconds=state.time_seconds + step_seconds,
        altitude_meters=max(next_altitude_meters, 0.0),
        velocity_mps=next_velocity_mps,
        acceleration_mps2=acceleration_mps2,
        mass_kg=next_mass_kg,
        thrust_newtons=thrust_newtons,
        drag_newtons=drag_newtons,
    )
