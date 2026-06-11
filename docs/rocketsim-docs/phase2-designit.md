# ==================================================
# RocketSim Phase 2 - Basic Flight Simulation
# ==================================================

Estimated Story Points: 4  
Estimated Phases: 2

# --------------------------------------------------
# Phase 2a - Flight State and Physics Step
# --------------------------------------------------
- Add `FlightState` model: time, altitude, velocity, acceleration, mass, thrust, drag
- Add basic vertical physics step: thrust, gravity, drag, mass burn-down

# --------------------------------------------------
# Phase 2b - Simulation Service and Events
# --------------------------------------------------
- Add `SimulationService` to run time-step simulation from rocket + motor inputs
- Detect core events: liftoff, burnout, max velocity, apogee, deployment placeholder, landing placeholder

# ==================================================
# Architecture Notes
# ==================================================

Phase 2 builds on the Phase 1 rocket and motor input models.

Recommended files:

src/rocketsim/
├── models/
│   ├── simulation.py
│   ├── rocket.py
│   └── motor.py
├── physics/
│   └── flight.py
├── services/
│   └── simulation_service.py
└── tests/
    ├── physics/
    │   └── test_flight.py
    └── services/
        └── test_simulation_service.py

Core assumptions:

- 1D vertical flight only
- No wind
- No rail angle
- Constant drag coefficient for now
- Simple air density constant
- Motor thrust may use placeholder average thrust if no full curve exists
- Recovery/deployment can be event placeholders until later phases

# ==================================================
# Testing Strategy
# ==================================================

- Test gravity-only acceleration is negative
- Test thrust greater than weight produces upward acceleration
- Test drag opposes velocity
- Test mass decreases during motor burn
- Test burnout event occurs after burn time
- Test apogee event occurs when velocity changes from positive to negative
- Test simulation output contains ordered flight states

# ==================================================
# Risks / Considerations
# ==================================================

- Keep formulas simple and readable before improving realism
- Avoid overbuilding thrust-curve support too early
- Clearly label output as estimated
- Do not mix chart/report work into Phase 2
- Keep generated runtime outputs out of commits unless intentionally testing fixtures

# ==================================================
# Suggested Phase 2a Branch
# ==================================================

p2a-flight-physics

# ==================================================
# Suggested Phase 2b Branch
# ==================================================

p2b-simulation-events
