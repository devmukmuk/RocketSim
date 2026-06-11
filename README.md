# RocketSim

RocketSim is a Python-based model rocket simulation and launch planning tool.

The goal of RocketSim is to provide a lightweight, configurable, and extensible platform for:

* Simulating model rocket flights
* Evaluating rocket stability
* Estimating altitude, velocity, and acceleration
* Generating launch reports
* Producing launch-day checklists
* Creating flight charts and data exports
* Supporting NAR and Tripoli certification projects

RocketSim is designed as a learning project and engineering tool for hobby rocketry enthusiasts.

---

# Features (Planned)

## Flight Simulation

* Single-stage model rocket simulation
* Real motor thrust curves
* Atmospheric modeling
* Drag calculations
* Recovery system deployment
* Landing estimates

## Stability Analysis

* Center of Gravity (CG)
* Center of Pressure (CP)
* Stability Margin (calibers)

## Reporting

* Flight summary reports
* Launch range cards
* Operations checklists
* Flight data archives

## Visualization

* Altitude vs Time
* Velocity vs Time
* Acceleration vs Time
* Thrust vs Time

## Export Formats

* Markdown
* PDF
* CSV
* JSON
* Excel

---

# Project Status

Current Version:

```text
0.1.0-alpha
```

Current Phase:

```text
Project Scaffold
```

---

# Project Structure

```text
RocketSim/
│
├── src/
│   └── rocketsim/
│
├── tests/
│
├── configs/
│   ├── rockets/
│   ├── motors/
│   └── launches/
│
├── docs/
│   └── rocketsim-docs/
│
├── outputs/
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

---

# Development Environment

## Create Virtual Environment

### Windows Git Bash

```bash
python -m venv .venv

source .venv/Scripts/activate
```

### Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

## Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements-dev.txt
```

---

# Running Tests

```bash
pytest
```

---

# Planned CLI

```bash
rocketsim simulate launch.yaml

rocketsim report launch.yaml

rocketsim checklist launch.yaml
```

---

# Example Future Workflow

```bash
rocketsim simulate configs/launches/loc_iv_h123.yaml
```

Outputs:

```text
outputs/
└── loc_iv_h123/
    ├── simulation-report.md
    ├── launch-checklist.md
    ├── altitude-time.png
    ├── velocity-time.png
    ├── simulation-data.csv
```

---

# Long-Term Goals

* OpenRocket import support
* RockSim import support
* Weather integration
* Wind drift analysis
* Recovery prediction
* Multi-stage rockets
* Flight computer integration
* GPS flight analysis
* GUI dashboard

---

# License

This project is provided for educational and hobby use.

Always follow:

* NAR Safety Code
* Tripoli Safety Code
* Manufacturer recommendations
* Local launch regulations

Simulation results are estimates only and should never replace proper flight testing and range safety procedures.

---

# Author

Mike Mattinson

Rocketry • Software Development • Engineering • STEM Education
