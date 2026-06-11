"""RocketSim CLI."""

from __future__ import annotations

import typer
from rich.console import Console

from rocketsim import __app_name__, __version__

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
    launch_file: str,
) -> None:
    """Run a rocket flight simulation."""
    console.print(
        f"[yellow]Simulation not yet implemented.[/yellow]"
    )
    console.print(f"Launch File: {launch_file}")


@app.command()
def checklist(
    launch_file: str,
) -> None:
    """Generate launch checklist."""
    console.print(
        f"[yellow]Checklist generation not yet implemented.[/yellow]"
    )
    console.print(f"Launch File: {launch_file}")


@app.command()
def report(
    launch_file: str,
) -> None:
    """Generate simulation report."""
    console.print(
        f"[yellow]Report generation not yet implemented.[/yellow]"
    )
    console.print(f"Launch File: {launch_file}")