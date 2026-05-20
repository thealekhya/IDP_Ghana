"""
Ghana Healthcare AI Agent — Main Entry Point

This script:
1. Builds the LanceDB vector store (if not already built)
2. Builds the SQLite database (if not already built)
3. Launches the interactive agent

Run with:  python app.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path)
# override=True ensures changes to .env take effect even if env vars were set earlier
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

# Verify at least one API key if not offline
offline = os.getenv("OFFLINE_MODE", "").strip() in {"1", "true", "True", "yes", "YES"}
provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
if not offline:
    if provider == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            print("ERROR: GEMINI_API_KEY not set (LLM_PROVIDER=gemini).")
            print("   Add GEMINI_API_KEY to .env, or set OFFLINE_MODE=1")
            sys.exit(1)
    else:
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set (LLM_PROVIDER=openai).")
            print("   Add OPENAI_API_KEY to .env, or set OFFLINE_MODE=1")
            sys.exit(1)


def setup():
    """One-time setup: build vector store and SQLite DB."""
    csv_path = os.path.join("data", "ghana_healthcare.csv")
    lance_path = os.path.join("data", "lancedb")

    if not os.path.exists(csv_path):
        print(f"Dataset not found at {csv_path}")
        sys.exit(1)

    # Build LanceDB vector store
    if not os.path.exists(lance_path):
        print("\nFirst run: building vector store...")
        from backend.vectorstore.lancedb_store import create_vectorstore
        create_vectorstore(csv_path, lance_path)
    else:
        print("Vector store already exists.")

    # Build SQLite DB
    db_path = csv_path.replace(".csv", ".db")
    if not os.path.exists(db_path):
        print("\nFirst run: building SQLite database...")
        from backend.sql.text2sql import Text2SQL
        Text2SQL(csv_path)
    else:
        print("SQLite database already exists.")


def main():
    """Run the interactive agent."""
    print("=" * 60)
    print("Ghana Healthcare AI Agent")
    print("Powered by LangGraph + LanceDB + GPT-4o")
    print("=" * 60)

    # Setup data stores
    setup()

    # Import agent (after setup so DBs exist)
    from backend.agent.graph import ask_agent

    print("\nAgent ready! Ask questions about healthcare in Ghana.")
    print("   Type 'quit' to exit.\n")

    # Example queries to try
    print("Try these sample queries:")
    examples = [
        "How many hospitals are in Accra?",
        "Tell me about Accra Specialist Eye Hospital",
        "List clinics in Ashanti region",
        "Which facilities offer ophthalmology services?",
        "Find NGOs working in Ghana healthcare",
    ]
    for i, ex in enumerate(examples, 1):
        print(f"   {i}. {ex}")
    print()

    # Interactive loop
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not query:
            continue

        print("\nProcessing...")
        try:
            answer = ask_agent(query)
            print(f"\nAgent: {answer}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
