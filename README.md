# Sankofa Health AI

Sankofa Health AI is a full-stack healthcare intelligence platform for exploring healthcare facility coverage, service gaps, and suspicious facility claims in Ghana. It combines an AI chat assistant, healthcare data analysis, vector search, interactive maps, and anomaly detection in one authenticated web application.

The project was built for healthcare planning and decision support. Users can ask natural-language questions, inspect facility data, view hospitals on a map, analyze regional healthcare coverage, and identify inconsistencies in facility capabilities or specialty claims.

## Features

- AI-powered healthcare chat assistant
- User-specific chat history with unique chat UUIDs
- Resume previous conversations from the sidebar
- Clerk-based authentication
- Interactive healthcare facility map
- Facility and regional healthcare data exploration
- RAG-based search using LanceDB and sentence-transformers
- Structured healthcare data querying
- Regional healthcare gap analysis
- Medical consistency and anomaly detection
- Support for OpenAI and Gemini LLM providers
- FastAPI backend with a Next.js frontend

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- LangGraph
- LangChain
- OpenAI API
- Gemini API
- LanceDB
- Sentence Transformers
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
- Mapbox GL
- React Markdown

## Project Structure

```text
.
|-- backend/
|   |-- api.py
|   |-- app.py
|   |-- agent/
|   |-- config/
|   |-- data/
|   |-- pipeline/
|   |-- schemas/
|   |-- sql/
|   `-- vectorstore/
|-- ui/
|   |-- app/
|   |-- public/
|   |-- package.json
|   |-- next.config.ts
|   `-- middleware.ts
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

## Prerequisites

Install these before running the project:

- Python 3.10 or newer
- Node.js 20 or newer
- npm
- OpenAI API key or Gemini API key
- Clerk project keys
- MapTiler key for map tiles

## Environment Variables

Create the backend environment file:

```powershell
Copy-Item .env.example backend\.env
```

Then update `backend/.env`:

```env
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LANCEDB_PATH=./data/lancedb
```

Use either OpenAI or Gemini. If using Gemini, set:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
```

Create the frontend environment file:

```powershell
New-Item ui\.env.local -ItemType File
```

Add these values to `ui/.env.local`:

```env
NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
CLERK_SECRET_KEY=your-clerk-secret-key
```

Never commit `.env` or `.env.local` files to GitHub.

## Backend Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the backend:

```powershell
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

## Frontend Setup

Open a second terminal from the project root:

```powershell
cd ui
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

## Running the Full App Locally

Start the backend first:

```powershell
cd backend
$env:PYTHONPATH=".."
python api.py
```

Then start the frontend in another terminal:

```powershell
cd ui
npm run dev
```

Open:

```text
http://localhost:3000
```

## Build Commands

Build the frontend:

```powershell
cd ui
npm run build
```

Start the production frontend locally:

```powershell
npm run start
```

Run frontend linting:

```powershell
npm run lint
```

The Python backend does not need compilation. It runs directly with Uvicorn through `api.py`.

## Data Files

Backend healthcare datasets and generated local databases are stored in:

```text
backend/data/
```

Frontend map and anomaly JSON files are stored in:

```text
ui/public/
```

Generated files such as local databases, vector stores, caches, and environment files should not be committed unless intentionally required for deployment.

## Deployment Notes

Recommended deployment setup:

- Deploy the frontend on Vercel with `ui/` as the root directory.
- Deploy the backend separately on a Python hosting platform such as Render, Railway, or Fly.io.
- Add the backend URL to the frontend code or environment configuration before production deployment.
- Add all required environment variables in the hosting dashboards.

For Vercel frontend deployment:

1. Push the project to GitHub.
2. Import the repository in Vercel.
3. Set the Vercel root directory to `ui`.
4. Add frontend environment variables in Vercel.
5. Build command: `npm run build`
6. Output/runtime: Next.js default

## GitHub Safety Checklist

Before pushing to GitHub:

- Confirm `.env`, `backend/.env`, and `ui/.env.local` are ignored.
- Do not commit API keys.
- Do not commit `node_modules/`.
- Do not commit `.next/`.
- Do not commit Python cache folders.
- Avoid committing generated local databases or vector stores unless required.

## Summary

Sankofa Health AI helps users understand healthcare access in Ghana through AI-assisted search, maps, structured analysis, and anomaly detection. It is designed for public health research, NGO coordination, healthcare planning, and data-driven decision-making.
