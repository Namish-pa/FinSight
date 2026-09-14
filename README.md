# FinSight

A financial analytics platform that combines a **deterministic KPI engine**, a **natural-language query interface**, and a **linear regression forecasting module** — all served through a FastAPI backend and a minimal React dashboard.

Built as a portfolio project demonstrating a clean separation between AI-powered features and purely deterministic financial calculations.

---

## Why This Project

Built to mirror the kind of work done in financial analytics consulting: cash flow optimization, BI dashboarding, and — increasingly — AI-driven finance tooling. Three deliberate choices reflect that:

- **A deterministic KPI layer sits alongside the AI layer, not instead of it.** DSO, AR aging, and cash runway are computed with plain SQL/pandas — never delegated to an LLM — because financial metrics that drive real decisions need to be exact and auditable, not "usually right." The LLM is reserved for what it's actually good at: flexible, ad-hoc natural-language questions.
- **The system knows what it doesn't know.** Ask it something the schema can't support (e.g. "what's our profit margin?" — there's no cost/revenue split in this data) and it says so, rather than quietly substituting a similar-sounding calculation. That distinction came out of an actual bug caught during development — see Key Design Decisions below.
- **Minimal, high-contrast dashboard design** — built to put the numbers first, with no visual noise competing for attention.

---

## What It Does

| Layer            | What it computes                                      | How                                        |
| ---------------- | ----------------------------------------------------- | ------------------------------------------ |
| **KPI Engine**   | DSO, AR Aging Buckets, Cash Runway, Monthly Cash Flow | Pure SQL + pandas, no LLM                  |
| **Query Engine** | Answers plain-English questions about the data        | Gemini → SQL → SQLite → Groq summary       |
| **Forecasting**  | 3-month net cash flow projection                      | NumPy linear regression on complete months |
| **API**          | Exposes all of the above over HTTP                    | FastAPI                                    |
| **Dashboard**    | Visualises everything in a minimal, monochrome UI     | React + Vite + Recharts                    |

---

## Project Structure

```
finsight/
├── client/                  # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── KPIs.jsx         # DSO, Cash Runway, AR Aging table
│   │   │   ├── Forecast.jsx     # Cash flow chart + projection
│   │   │   └── QueryEngine.jsx  # Natural language query input
│   │   ├── App.jsx
│   │   ├── api.js               # fetch wrappers for the FastAPI backend
│   │   └── index.css            # Monochrome e-reader design system
│   ├── index.html
│   └── package.json
│
└── server/                  # Python backend
    ├── api/
    │   ├── main.py              # FastAPI app (GET /kpis, GET /forecast, POST /ask)
    │   └── test_api.py          # Manual smoke-test script
    ├── data/
    │   ├── schema.sql           # SQLite schema (accounts, transactions, invoices, clients)
    │   └── generate_data.py     # Synthetic data generator; populates finsight.db
    ├── kpi/
    │   ├── db.py                # SQLite connection helper
    │   └── metrics.py           # calculate_dso, calculate_aging_buckets,
    │                            # calculate_cash_runway, calculate_monthly_cashflow
    ├── forecasting/
    │   └── models.py            # forecast_linear_regression (NumPy polyfit, deg=1)
    ├── query_engine/
    │   ├── engine.py            # ask(question) → QueryResult
    │   ├── llm.py               # Gemini (SQL gen) + Groq (summarisation) clients
    │   ├── prompts.py           # System prompt with schema context and safety rules
    │   ├── db.py                # SQL execution against finsight.db
    │   └── models.py            # QueryResult dataclass
    ├── .env.example             # Required environment variable template
    ├── pyproject.toml
    └── uv.lock
```

---

## Prerequisites

- **Python 3.11+** with [uv](https://github.com/astral-sh/uv) (`pip install uv`)
- **Node.js 18+** with npm

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Namish-pa/FinSight.git
cd FinSight
```

### 2. Configure environment variables

```bash
cd server
cp .env.example .env
```

Open `server/.env` and fill in your API keys:

```
GEMINI_API_KEY=your_gemini_key_here   # https://aistudio.google.com/app/apikey
GROQ_API_KEY=your_groq_key_here       # https://console.groq.com/keys
```

The KPI and forecasting modules are purely deterministic and **do not require any API keys**.

### 3. Install backend dependencies

```bash
cd server
uv sync
```

### 4. Generate the database

```bash
uv run python data/generate_data.py
```

This creates `server/data/finsight.db` with ~20 months of synthetic financial data (accounts, transactions, invoices, clients).

### 5. Install frontend dependencies

```bash
cd ../client
npm install
```

---

## Running Locally

You need two terminal sessions.

**Terminal 1 — Backend (FastAPI)**

```bash
cd server
uv run uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite)**

```bash
cd client
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## API Endpoints

All endpoints are served at `http://localhost:8000`.

| Method | Path            | Description                                                                          |
| ------ | --------------- | ------------------------------------------------------------------------------------ |
| `GET`  | `/api/kpis`     | Returns DSO, AR aging buckets, cash runway, and monthly cash flow                    |
| `GET`  | `/api/forecast` | Returns historical cash flow + 3-month linear regression forecast                    |
| `POST` | `/api/ask`      | Accepts `{"question": "..."}`, returns SQL, raw rows, and a natural-language summary |

You can verify the backend independently with:

```bash
cd server
uv run python api/test_api.py
```

---

## Key Design Decisions

**Strict module isolation.** The `kpi/` and `forecasting/` modules import nothing from `query_engine/`. Each layer has its own `db.py`. The `api/` layer is the only place they are composed together.

**No hallucination for unavailable metrics.** The query engine's system prompt explicitly instructs the LLM to refuse questions that require financial concepts not present in the schema (e.g., profit margin, gross margin). It will not substitute a similar-sounding calculation.

**Partial month exclusion in forecasting.** The linear regression fit automatically excludes the current/anchor month if it is incomplete, preventing a low-count partial month from distorting the trend slope.

**Deterministic balance computation.** Account balances in the database are derived from `opening_balance + SUM(transactions)` rather than random static values, ensuring the cash runway KPI is consistent with actual transaction history.

**SQL safety guard.** Every generated query is parsed with `sqlparse` before execution — only single, pure `SELECT` statements are allowed. This blocks both direct destructive requests and stacked-query injection attempts (e.g. `SELECT ...; DROP TABLE ...;`), independent of whether the LLM itself would have generated one.

---

## What I'd Do With More Time

- **Schema-aware RAG for the query engine** — the current approach injects the full schema directly into every prompt, which works well at 5 tables but wouldn't scale past a few dozen; a real enterprise deployment would need retrieval to select only relevant tables per question.
- **Row-level security** for multi-tenant access, so different users only see data they're authorized for.
- **Swap SQLite for PostgreSQL** and add proper connection pooling for concurrent access.
- **Embed the dashboard in Power BI** instead of a custom React frontend, to match how BI is typically delivered in enterprise finance teams.
- **Add anomaly detection** on top of the monthly cash flow series — flagging months that deviate significantly from the forecasted trend, rather than just projecting forward.

---

## Environment Variables

| Variable         | Required                     | Description                                |
| ---------------- | ----------------------------- | ------------------------------------------ |
| `GEMINI_API_KEY` | Yes (for query engine only)  | Used for natural language → SQL generation |
| `GROQ_API_KEY`   | Yes (for query engine only)  | Used for fast result summarisation         |

The KPI, forecasting, and data modules run entirely without API keys.

---

## License

MIT — see [`LICENSE`](https://github.com/Namish-pa/FinSight/blob/main/LICENSE) for details.