"""RocketSim application entry point."""

from rocketsim import __app_name__
from rocketsim.commands import cli


def main() -> None:
    """Launch the RocketSim CLI."""
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()