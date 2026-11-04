# MaintAI — Predictive Maintenance System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/Pytest-8.0+-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Code Style](https://img.shields.io/badge/Linter-Ruff-261230?style=flat)](https://github.com/astral-sh/ruff)

An industrial machine failure prediction API developed as part of the *Développement et déploiement d'applications intelligentes* course.

---

## Compte Rendu (Reports)

* **Student Report (TP1 / TP2):** [Bounjoume_Oussama_COMPTE_RENDU.md](./Compte_Rendus/Bounjoume_Oussama_COMPTE_RENDU.md)
* **Architecture Decision Records:** [ADRs Directory](./docs/adr/)

---

## Architecture Overview

The system captures sensor metrics from industrial equipment (temperature, vibration, load percentage, and accumulated operating hours), validates input payload schemas using Pydantic, and serves machine learning predictions via FastAPI.

```
            +-------------------+
            |  Industrial Client|
            | (curl / Web Page) |
            +---------+---------+
                      |
                      | HTTP POST /v1/predict (X-API-Key)
                      v
            +-------------------+
            |   FastAPI App     |
            | (Pydantic Schema) |
            +---------+---------+
                      |
                      v
            +-------------------+
            |  ML Predictor     |
            | (Logistic Reg.)   |
            +-------------------+
```

---

## Quick Start

### 1. Virtual Environment & Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset & Train Model

```bash
# Generate synthetic sensor data in data/sensors.csv
python -m maintai.dataset

# Train model and produce artifacts in models/
python -m maintai.train
```

### 3. Run Pytest Suite & Ruff Linter

```bash
# Run unit and integration tests (18+ tests)
python -m pytest -v

# Run ruff code quality checks
ruff check .
```

### 4. Launch FastAPI Server

```bash
uvicorn maintai.api.main:app --reload
```

* **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## Repository Structure

```
├── Compte_Rendus/        # Student lab reports (Bounjoume_Oussama_COMPTE_RENDU.md)
├── docs/adr/             # Architectural Decision Records (ADR 001 - 003)
├── maintai/              # Core Python package
│   ├── api/              # FastAPI endpoints, schemas, and security dependencies
│   ├── config.py         # Application configuration & environment variables
│   ├── data.py           # Data preprocessing and splitting
│   ├── dataset.py        # Synthetic dataset generator
│   ├── predict.py        # Model loading and inference wrapper
│   └── train.py          # Model training pipeline and metric reporting
├── tests/                # Pytest suite (API, security, regression, casser tests)
├── web/                  # HTML5 / JavaScript web client
└── requirements.txt      # Python dependencies
```

---

*Project developed by **Bounjoume Oussama** (Group G6)*
