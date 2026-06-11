"""RocketSim package initialization."""

# src/rocketsim/__init__.py

__all__ = [
    "__app_name__",
    "__version__",
]

__app_name__ = "RocketSim"
__version__ = "2026.6.0"


(
    SUCCESS,
    CONFIG_ERROR,
    INPUT_ERROR,
    SIMULATION_ERROR,
    EXPORT_ERROR,
) = range(5)


ERRORS = {
    CONFIG_ERROR: "configuration error",
    INPUT_ERROR: "invalid input",
    SIMULATION_ERROR: "simulation error",
    EXPORT_ERROR: "export error",
}