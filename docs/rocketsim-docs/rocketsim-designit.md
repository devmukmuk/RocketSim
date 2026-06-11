# ==================================================
# RocketSim Custom Model Rocket Simulator
# ==================================================

Estimated Story Points: 16
Estimated Phases: 8

# --------------------------------------------------
# Phase 1 - Project Scope and Core Inputs
# --------------------------------------------------
- Define rocket input model: rocket name, diameter, length, weight, CG, CP, fin count, fin dimensions
- Define motor input model: motor name, impulse class, thrust curve placeholder, delay, propellant weight

# --------------------------------------------------
# Phase 2 - Basic Flight Simulation
# --------------------------------------------------
- Add simple vertical flight model: thrust, drag, gravity, mass change
- Output core flight events: liftoff, max velocity, burnout, apogee, deployment, landing

# --------------------------------------------------
# Phase 3 - Chart Outputs
# --------------------------------------------------
- Generate altitude vs time chart
- Generate velocity vs time chart

# --------------------------------------------------
# Phase 4 - Launch Report
# --------------------------------------------------
- Generate plain-text or markdown launch summary report
- Include stability margin, estimated apogee, max velocity, descent rate, and landing estimate

# --------------------------------------------------
# Phase 5 - Checklist System
# --------------------------------------------------
- Add reusable launch operations checklist template
- Add rocket-specific checklist output based on selected motor and recovery setup

# --------------------------------------------------
# Phase 6 - CLI Workflow
# --------------------------------------------------
- Add `rocketsim simulate` command
- Add config-driven input file support using YAML or JSON

# --------------------------------------------------
# Phase 7 - Document Export
# --------------------------------------------------
- Export simulation report to markdown
- Export charts as PNG files

# --------------------------------------------------
# Phase 8 - Validation and Safety Review
# --------------------------------------------------
- Add input validation for missing or unsafe values
- Add tests for simulation math, reports, and checklist generation

# ==================================================
# Architecture Notes
# ==================================================

Recommended project modules:

src/rocketsim/
├── cli.py
├── models/
│   ├── rocket.py
│   ├── motor.py
│   ├── environment.py
│   └── simulation.py
├── services/
│   ├── simulation_service.py
│   ├── chart_service.py
│   ├── report_service.py
│   └── checklist_service.py
├── templates/
│   ├── launch_report.md
│   └── launch_checklist.md
└── tests/

Input files:

configs/
├── rockets/
│   └── loc_iv.yaml
├── motors/
│   └── h123.yaml
└── launches/
    └── loc_iv_h123_launch.yaml

# ==================================================
# Suggested CLI
# ==================================================

rocketsim simulate configs/launches/loc_iv_h123_launch.yaml

rocketsim report configs/launches/loc_iv_h123_launch.yaml

rocketsim checklist configs/launches/loc_iv_h123_launch.yaml

# ==================================================
# Example Outputs
# ==================================================

outputs/
└── loc_iv_h123_2026-06-11/
    ├── simulation-summary.md
    ├── launch-checklist.md
    ├── altitude-time.png
    ├── velocity-time.png
    └── simulation-data.csv

# ==================================================
# Testing Strategy
# ==================================================

- Unit test input parsing
- Unit test thrust/drag/gravity calculations
- Unit test event detection
- Unit test checklist generation
- Snapshot test generated markdown reports
- Integration test full launch simulation from YAML input to output folder

# ==================================================
# Risks / Considerations
# ==================================================

- Early simulation should be clearly labeled “estimate only”
- Thrust curves should eventually use real motor data files
- Wind drift and recovery modeling should be added after basic vertical simulation works
- Safety checklist should avoid replacing official range safety procedures
- Stability calculations should be conservative

# ==================================================
# Future Enhancements
# ==================================================

- OpenRocket/RockSim file import
- Motor database integration
- Weather/wind profile support
- Drift and landing zone estimate
- PDF report export
- Multi-rocket comparison charts
- Launch day range card
- NAR/Tripoli Level 1 certification packet helper
- GUI dashboard
