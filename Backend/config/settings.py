"""Central configuration for the hackathon project."""

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Paths
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_PATH = os.path.join(DATA_PATH, "ghana_healthcare.csv")
LANCEDB_PATH = os.getenv("LANCEDB_PATH", os.path.join(DATA_PATH, "lancedb"))

# LLM Settings
LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0

# Embedding Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector Search
TOP_K_RESULTS = 5
