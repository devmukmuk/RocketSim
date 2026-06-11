"""RocketSim CLI."""

from __future__ import annotations

import typer
from rich.console import Console

from rocketsim import __app_name__, __version__
from rocketsim.models.motor import Motor
from rocketsim.models.rocket import Rocket
from rocketsim.models.simulation import SimulationResult
from rocketsim.services.simulation_service import SimulationService

app = typer.Typer(
    help="RocketSim - Model Rocket Flight Simulation and Launch Planning",
    add_completion=False,
)

console = Console()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show application version.",
    ),
) -> None:
    """RocketSim command line interface."""
    if version:
        console.print(
            f"{__app_name__} v{__version__}",
        )
        raise typer.Exit()


@app.command()
def about() -> None:
    """Display application information."""
    console.print()
    console.print(f"[bold]{__app_name__}[/bold]")
    console.print(f"Version: {__version__}")
    console.print()
    console.print("Model Rocket Flight Simulation")
    console.print("Launch Planning")
    console.print("Report Generation")
    console.print()


@app.command()
def simulate(
    rocket_config: str,
    motor_config: str,
    step_seconds: float = 0.05,
    max_time_seconds: float = 60.0,
) -> None:
    """Run a basic rocket flight simulation."""
    rocket = Rocket.from_yaml(rocket_config)
    motor = Motor.from_yaml(motor_config)

    result = SimulationService().simulate(
        rocket=rocket,
        motor=motor,
        step_seconds=step_seconds,
        max_time_seconds=max_time_seconds,
    )

    print_simulation_summary(
        rocket=rocket,
        motor=motor,
        result=result,
    )


def print_simulation_summary(
    rocket: Rocket,
    motor: Motor,
    result: SimulationResult,
) -> None:
    """Print a human-readable simulation summary."""
    console.print()
    console.print("[bold]RocketSim Simulation[/bold]")
    console.print("====================")
    console.print()

    console.print("[bold]Rocket[/bold]")
    console.print("------")
    console.print(f"Name: {rocket.name}")
    console.print(f"Diameter: {rocket.diameter:.4f} m")
    console.print(f"Dry Weight: {rocket.dry_weight:.3f} kg")
    console.print()

    console.print("[bold]Motor[/bold]")
    console.print("-----")
    console.print(f"Name: {motor.name}")
    console.print(f"Impulse Class: {motor.impulse_class}")
    console.print(f"Average Thrust: {motor.average_thrust:.2f} N")
    console.print(f"Burn Time: {motor.burn_time:.2f} s")
    console.print()

    console.print("[bold]Results[/bold]")
    console.print("-------")
    console.print(f"Max Altitude: {result.max_altitude_meters:.2f} m")
    console.print(f"Max Velocity: {result.max_velocity_mps:.2f} m/s")

    if result.states:
        console.print(f"Simulation Time: {result.states[-1].time_seconds:.2f} s")

    console.print()
    console.print("[bold]Events[/bold]")
    console.print("------")

    if not result.events:
        console.print("No events detected.")
        return

    for event in result.events:
        console.print(
            f"{event.name:<12}"
            f"{event.time_seconds:8.2f}s  "
            f"{event.altitude_meters:8.2f}m  "
            f"{event.velocity_mps:8.2f}m/s"
        )


@app.command()
def checklist(
    launch_file: str,
) -> None:
    """Generate launch checklist."""
    console.print(
        "[yellow]Checklist generation not yet implemented.[/yellow]"
    )
    console.print(f"Launch File: {launch_file}")


@app.command()
def report(
    launch_file: str,
) -> None:
    """Generate simulation report."""
    console.print(
        "[yellow]Report generation not yet implemented.[/yellow]"
    )
    console.print(f"Launch File: {launch_file}")
