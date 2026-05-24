# Sankofa Health AI

**Sankofa** is a word from the Akan people of Ghana. It is commonly expressed as the idea of "go back and fetch it": learning from the past, recovering what is valuable, and using that knowledge to build a wiser future. The name fits this project because Sankofa Health AI looks back at healthcare facility data, service records, regional coverage, and suspicious claims to help communities and planners make better decisions for the future of healthcare access in Ghana.

Sankofa Health AI is a full-stack healthcare intelligence platform for exploring healthcare facility coverage, service gaps, and suspicious facility claims in Ghana. It combines an AI chat assistant, healthcare data analysis, vector search, interactive maps, and anomaly detection in one web application.

The project is designed for healthcare planning and decision support. Users can ask natural-language questions, inspect facility data, view hospitals on a map, analyze regional healthcare coverage, and identify inconsistencies in facility capabilities or specialty claims.

## Features

- AI-powered healthcare chat assistant
- Natural-language querying over Ghana healthcare facility data
- Structured SQL-style analysis through a local SQLite database
- RAG-based semantic search using LanceDB and sentence-transformers
- Regional healthcare gap analysis
- Medical consistency and anomaly detection
- Interactive map of healthcare facilities
- Facility markers with details such as name, contact information, status, and specialties
- Support for Gemini and OpenAI LLM providers
- FastAPI backend with a Next.js frontend
- Clerk authentication support in the frontend

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- LangGraph
- LangChain
- Gemini API through `langchain-google-genai`
- OpenAI API through `langchain-openai`
- LanceDB
- Sentence Transformers
- SQLite
- Pandas
- NumPy
- PyArrow
- Pydantic
- python-dotenv

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Clerk Authentication
- Leaflet
- React Leaflet
- React Markdown
- MapTiler map tiles

## Folder Structure

```text
IDP_Ghana/
|-- .env                         # Local secrets and runtime config; ignored by Git
|-- .gitignore
|-- LICENSE
|-- README.md
|-- requirements.txt             # Python backend dependencies
|-- backend/
|   |-- api.py                   # FastAPI API server
|   |-- app.py                   # Original/CLI-style backend entrypoint
|   |-- facility_and_ngo_fields.py
|   |-- free_form.py
|   |-- geocode.py
|   |-- medical_specialties.py
|   |-- merge_data.py
|   |-- organization_extraction.py
|   |-- prep_anomalies.py
|   |-- package.json
|   |-- package-lock.json
|   |-- Virtue Foundation Ghana v0.3 - Sheet1.csv
|   |-- agent/
|   |   |-- __init__.py
|   |   |-- gap_analysis.py      # Regional service gap analysis
|   |   |-- graph.py             # LangGraph workflow
|   |   |-- nodes.py             # Agent node logic
|   |   |-- state.py             # Agent state schema
|   |-- config/
|   |   |-- __init__.py
|   |   |-- llm.py               # Gemini/OpenAI LLM selection
|   |   |-- settings.py          # Data path settings
|   |-- data/
|   |   |-- ghana_healthcare.csv
|   |   |-- ghana_healthcare.db
|   |   |-- combined_discrepancies.csv
|   |   |-- graph_anomaly_scores.csv
|   |   |-- medical_consistency_flags.csv
|   |   |-- lancedb/
|   |-- pipeline/
|   |   |-- data_cleaning.py
|   |   |-- gnn_anomaly.py
|   |   |-- _inspect_claims.py
|   |   |-- _list_specs.py
|   |   |-- _profile_data.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- facility_and_ngo_fields.py
|   |   |-- free_form.py
|   |   |-- medical_specialties.py
|   |   |-- organization_extraction.py
|   |-- sql/
|   |   |-- __init__.py
|   |   |-- text2sql.py
|   |-- vectorstore/
|   |   |-- __init__.py
|   |   |-- lancedb_store.py
|-- Frontend/
|   |-- app/
|   |   |-- layout.tsx
|   |   |-- page.tsx
|   |   |-- globals.css
|   |   |-- AuthUserMenu.tsx
|   |   |-- anomalies/
|   |   |-- chat/
|   |   |-- home/
|   |   |-- map/
|   |   |   |-- LeafletMap.tsx
|   |   |   |-- page.tsx
|   |-- public/
|   |   |-- anomalies.json
|   |   |-- hospitals_data.json
|   |   |-- file.svg
|   |   |-- globe.svg
|   |   |-- next.svg
|   |   |-- vercel.svg
|   |   |-- window.svg
|   |-- middleware.ts
|   |-- next.config.ts           # Loads the root .env for frontend runtime values
|   |-- package.json
|   |-- package-lock.json
|   |-- postcss.config.mjs
|   |-- tsconfig.json
```


## Prerequisites

Install these before running the project:

- Python 3
- Node.js 20 or newer
- npm
- Gemini API key or OpenAI API key
- MapTiler API key for map tiles
- Clerk keys if using authentication features

## Environment Variables

This project is configured to use a single root `.env` file:

```text
IDP_Ghana/.env
```

Create the file at the project root and add the values you need:

```env
# LLM provider
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# Backend data
LANCEDB_PATH=./data/lancedb

# Frontend map
NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-key

# Clerk authentication, if enabled
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
CLERK_SECRET_KEY=your-clerk-secret-key
```

Use one LLM provider at a time:

- For Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
```

- For OpenAI:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

## Installation

Clone the repository and move into the project root:

```bash
git clone https://github.com/thealekhya/IDP_Ghana.git
cd IDP_Ghana
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS/Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

If Windows PowerShell blocks script activation, run this in the same terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd Frontend
npm install
npm install @clerk/nextjs@latest
```

On Windows PowerShell, use `npm.cmd install` if `npm install` is blocked by execution policy.

## Running the App Locally

The backend and frontend should run in two separate terminals.

### Terminal 1: Backend

From the project root:

```bash
# macOS/Linux
source .venv/bin/activate
cd backend
PYTHONPATH=.. python api.py
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
cd backend
$env:PYTHONPATH=".."
python api.py
```

The backend runs at:

```text
http://localhost:8000
```

Main API endpoint:

```text
POST /api/chat
```

Example request body:

```json
{
  "query": "Which regions in Ghana have the largest healthcare service gaps?"
}
```

Important: run `python api.py` from inside the `backend` folder after activating the virtual environment from the project root. This keeps relative data paths such as `data/ghana_healthcare.csv` working correctly.

### Terminal 2: Frontend

Open a second terminal:

```bash
cd Frontend
npm run dev
```

On Windows PowerShell, use `npm.cmd run dev` if `npm run dev` is blocked.

The frontend runs at:

```text
http://localhost:3000
```

Open `http://localhost:3000` in your browser.

## User Guide

1. Start the backend first and keep the backend terminal open.
2. Start the frontend in a second terminal and keep it open.
3. Open `http://localhost:3000`.
4. Use the chat interface to ask healthcare questions in natural language.
5. Use the map page to inspect healthcare facilities across Ghana.
6. Use anomaly-related pages or queries to review suspicious claims, data inconsistencies, and medical capability mismatches.
7. Use gap-analysis queries to identify regions with weaker healthcare coverage.

Example chat prompts:

```text
Which regions in Ghana have the largest healthcare service gaps?
```

```text
Show suspicious healthcare facility claims.
```

```text
How many hospitals are listed in the dataset?
```

```text
Which facilities provide maternity care?
```

## Common Commands

Run backend:

```bash
# macOS/Linux
source .venv/bin/activate
cd backend
PYTHONPATH=.. python api.py
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
cd backend
$env:PYTHONPATH=".."
python api.py
```

Run frontend:

```bash
cd Frontend
npm run dev
```

Build frontend:

```bash
cd Frontend
npm run build
```

Start production frontend after building:

```bash
npm run start
```

Run frontend linting:

```bash
npm run lint
```

Note: linting requires a valid ESLint configuration. If ESLint 9 reports that `eslint.config.js` is missing, add or migrate the ESLint config before relying on the lint command.

## Data Files

Backend healthcare datasets and generated local databases are stored in:

```text
backend/data/
```

Important backend data files include:

- `ghana_healthcare.csv`: main healthcare facility dataset
- `ghana_healthcare.db`: SQLite database generated from the dataset
- `combined_discrepancies.csv`: combined anomaly/discrepancy output
- `graph_anomaly_scores.csv`: graph-based anomaly scores
- `medical_consistency_flags.csv`: medical consistency flags
- `lancedb/`: local LanceDB vector index

Frontend public data is stored in:

```text
Frontend/public/
```

Important frontend files include:

- `hospitals_data.json`: facility data used by the map
- `anomalies.json`: anomaly data used by the frontend

## Troubleshooting

### `ModuleNotFoundError: No module named 'backend'`

Run the backend with `PYTHONPATH` set to the project root:

```bash
# macOS/Linux
source .venv/bin/activate
cd backend
PYTHONPATH=.. python api.py
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
cd backend
$env:PYTHONPATH=".."
python api.py
```

### `Dataset not found at data\ghana_healthcare.csv`

Run `python api.py` from inside the `backend` folder. The dataset exists at:

```text
backend/data/ghana_healthcare.csv
```

### `OPENAI_API_KEY is not set but LLM_PROVIDER=openai`

The app is using OpenAI mode. To use Gemini, set this in the root `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-flash
```

### Invalid MapTiler API key

Add a valid MapTiler key to the root `.env`:

```env
NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-key
```

Then stop and restart the frontend dev server.

### `npm` is blocked in PowerShell

Use:

```powershell
npm.cmd run dev
```

instead of:

```powershell
npm run dev
```

## GitHub Safety Checklist

Before pushing to GitHub:

- Do not commit `.env` files.
- Do not commit API keys.
- Do not commit `.venv/`.
- Do not commit `node_modules/`.
- Do not commit `.next/`.
- Do not commit Python cache folders such as `__pycache__/`.
- Check status before pushing:

```powershell
git status
```

Files are not staged unless you explicitly run `git add`.

## Deployment Notes

Recommended deployment setup:

- Deploy the frontend on Vercel with `Frontend/` as the root directory.
- Deploy the backend separately on a Python hosting platform such as Render, Railway, or Fly.io.
- Configure production environment variables in the hosting dashboards.
- Set the frontend to call the deployed backend URL instead of local `localhost:8000`.
- Keep secrets out of source control and use each platform's secret manager.

## Summary

Sankofa Health AI uses Ghana healthcare data to support better understanding of healthcare access, service gaps, and suspicious facility claims. It brings together AI-assisted search, structured querying, anomaly detection, and map-based exploration to help turn raw healthcare records into practical insight.
