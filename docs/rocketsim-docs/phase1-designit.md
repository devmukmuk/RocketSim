# ==================================================
# RocketSim Phase 1 - Project Scope and Core Inputs
# ==================================================

Estimated Story Points: 2

# --------------------------------------------------
# Story 1a - Rocket Input Model
# --------------------------------------------------
Define a rocket configuration model with:

- rocket name
- diameter
- length
- dry weight
- center of gravity
- center of pressure
- fin count
- fin root chord
- fin tip chord
- fin span
- fin sweep

Suggested files:

- src/rocketsim/models/rocket.py
- tests/models/test_rocket.py
- configs/rockets/example_rocket.yaml

# --------------------------------------------------
# Story 1b - Motor Input Model
# --------------------------------------------------
Define a motor configuration model with:

- motor name
- impulse class
- average thrust
- burn time
- delay
- propellant weight
- thrust curve placeholder

Suggested files:

- src/rocketsim/models/motor.py
- tests/models/test_motor.py
- configs/motors/example_motor.yaml

# ==================================================
# Acceptance Criteria
# ==================================================

- Rocket YAML can be loaded into a Rocket model
- Motor YAML can be loaded into a Motor model
- Missing required fields raise clear validation errors
- Unit tests cover valid and invalid rocket inputs
- Unit tests cover valid and invalid motor inputs
- No simulation math is required yet

# ==================================================
# Notes
# ==================================================

Phase 1 should only establish clean input structures.
Do not add flight simulation, charts, reports, or CLI behavior yet.
