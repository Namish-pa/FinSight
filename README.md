# FinSight

**FinSight** is a Python‑based financial analytics platform designed to simplify data ingestion, forecasting, and interactive querying. It provides a modular architecture with a clear separation between data handling, forecasting models, and a dashboard UI.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FinSight enables analysts and developers to quickly prototype financial data pipelines, generate forecasts using state‑of‑the‑art time‑series models, and explore results through an interactive dashboard. The codebase follows best practices for dependency management (using **uv**), type safety (via **pydantic**), and environment configuration (via **python‑dotenv**).

---

## Features

- **Modular design** – Separate packages for data ingestion (`data/`), forecasting (`forecasting/`), query handling (`query_engine/`) and visualization (`dashboard/`).
- **Typed configuration** – Centralised settings powered by Pydantic for validation and auto‑completion.
- **Extensible forecasting** – Plug‑in architecture allowing custom models.
- **Interactive dashboard** – Built with modern web technologies (HTML, CSS, JavaScript) for a rich UI experience.
- **Reproducible environment** – Dependency lockfile (`uv.lock`) ensures deterministic builds.

---

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finsight
   ```
2. **Set up a virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   ```
3. **Install dependencies**
   ```bash
   uv sync   # Uses the lockfile to install exact versions
   ```
4. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in required values (e.g., API keys).

---

## Quick Start

```bash
# Run the dashboard (development server)
cd dashboard
npm install   # Install front‑end dependencies
npm run dev   # Starts the dev server at http://localhost:3000
```

For a quick data‑pipeline test:
```bash
python -m data.ingest   # Loads sample data into the local store
python -m forecasting.run   # Generates forecasts
python -m query_engine.run   # Starts the query interface
```

---

## Project Structure

```
finSight/
├── .env               # Environment variables (local)
├── .env.example       # Example configuration file
├── dashboard/         # Front‑end UI (HTML/CSS/JS)
├── data/              # Data ingestion utilities
├── forecasting/       # Forecasting models and pipelines
├── query_engine/      # Query handling and API endpoints
├── pyproject.toml     # Project metadata and dependencies
├── requirements.txt   # Legacy requirements (for reference)
├── uv.lock            # Locked dependency versions
└── README.md          # This documentation
```

---

## Configuration

All configurable values are stored in the `.env` file. The project uses **python‑dotenv** to load these variables at runtime. Key variables include:
- `API_KEY` – Authentication token for external data providers.
- `DB_URL` – Connection string for the results database.
- `LOG_LEVEL` – Logging verbosity (e.g., `INFO`, `DEBUG`).

Refer to `.env.example` for a full list of supported keys.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Ensure code style compliance with `ruff` and type checking with `mypy`.
4. Add or update tests as needed.
5. Submit a pull request with a clear description of changes.

For major changes, open an issue first to discuss the proposed modifications.

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---


