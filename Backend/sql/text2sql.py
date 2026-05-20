"""
Text-to-SQL module — converts natural language to SQL queries.

Uses an LLM to translate user questions into SQL, then runs them
against a local SQLite copy of the dataset (or Databricks in prod).
"""

import os
import sqlite3
import re
import pandas as pd
from backend.config.llm import get_llm

# ── Table schema the LLM sees ──
TABLE_SCHEMA = """
Table: facilities
Columns:
  - name              TEXT    -- Facility or NGO name
  - pk_unique_id      INT     -- Unique ID per organization (rows with same pk_unique_id are the same org)
  - organization_type TEXT    -- 'facility' or 'ngo'
  - facilityTypeId    TEXT    -- hospital, clinic, pharmacy, doctor, dentist (nullable)
  - operatorTypeId    TEXT    -- public, private (nullable)
  - specialties       TEXT    -- JSON array of specialty strings, e.g. '["ophthalmology","pediatrics"]'
  - procedure_text    TEXT    -- JSON array of procedures performed
  - equipment         TEXT    -- JSON array of equipment
  - capability        TEXT    -- JSON array of capabilities
  - description       TEXT    -- Free-text description of the facility
  - address_line1     TEXT    -- Street address
  - address_city      TEXT    -- City (e.g. Accra, Kumasi, Tamale)
  - address_stateOrRegion TEXT -- Region (e.g. Greater Accra, Ashanti, Western, Northern)
  - address_country   TEXT    -- Always 'Ghana'
  - phone_numbers     TEXT    -- JSON array of phone numbers
  - email             TEXT    -- Email address
  - officialWebsite   TEXT    -- Website URL
  - yearEstablished   INT     -- Year founded (nullable)
  - capacity          INT     -- Bed capacity (nullable)
  - numberDoctors     INT     -- Number of doctors (nullable)

IMPORTANT NOTES:
- Use DISTINCT on pk_unique_id when counting organizations (duplicates exist per source_url)
- specialties is a JSON array stored as text; use LIKE '%%keyword%%' to search within it
- Many columns are nullable, use COALESCE or IS NOT NULL checks
- Region names are INCONSISTENT in the data! Examples: 'Ashanti', 'Ashanti Region', 'ASHANTI' all exist.
  Always use: UPPER(address_stateOrRegion) LIKE '%%ASHANTI%%' (match the root name, not the full string)
  Also check address_city with OR in case region is stored there.
- Known regions: Greater Accra, Ashanti, Western, Northern, Volta, Central, Bono East, Brong Ahafo, Ahafo
- Known cities: Accra, Kumasi, Tamale, Takoradi, Cape Coast, Ho, Sunyani, Koforidua
- facilityTypeId values: 'hospital', 'clinic', 'dentist', 'farmacy' (note: misspelled in data), 'doctor'
- operatorTypeId values: 'public', 'private'
"""


class Text2SQL:
    """Convert natural language → SQL → results."""

    def __init__(self, csv_path: str = "./data/ghana_healthcare.csv"):
        self.db_path = csv_path.replace(".csv", ".db")
        # Build the configured LLM if possible; otherwise fall back to heuristics.
        try:
            self.llm = get_llm()
        except Exception:
            self.llm = None
        self._ensure_db(csv_path)

    def _is_quota_error(self, err: Exception) -> bool:
        msg = str(err).lower()
        return (
            ("insufficient_quota" in msg)
            or ("exceeded your current quota" in msg)
            or ("resource_exhausted" in msg)
            or ("quota exceeded" in msg)
            or ("rate limit" in msg)
        )

    def _heuristic_sql(self, question: str) -> str | None:
        """
        Minimal fallback SQL generator for common hackathon questions.
        Returns None if it can't confidently map the question.
        """
        q = question.strip().lower()

        m = re.search(r"how many\s+(hospitals?|clinics?|pharmacies?)\s+.*\s+in\s+([a-z\s]+)\??$", q, re.IGNORECASE)
        if m:
            ftype = m.group(1)
            place = m.group(2).strip().title()
            ftype_norm = "hospital" if "hospital" in ftype else "clinic" if "clinic" in ftype else "pharmacy"
            return (
                "SELECT COUNT(DISTINCT pk_unique_id) AS count "
                "FROM facilities "
                f"WHERE facilityTypeId = '{ftype_norm}' "
                f"AND (UPPER(address_city) LIKE '%{place.upper()}%' OR UPPER(address_stateOrRegion) LIKE '%{place.upper()}%');"
            )

        m = re.search(r"list\s+(hospitals?|clinics?|pharmacies?)\s+in\s+([a-z\s]+)\??$", q, re.IGNORECASE)
        if m:
            ftype = m.group(1)
            place = m.group(2).strip().title()
            ftype_norm = "hospital" if "hospital" in ftype else "clinic" if "clinic" in ftype else "pharmacy"
            return (
                "SELECT DISTINCT name, address_city, address_stateOrRegion, operatorTypeId "
                "FROM facilities "
                f"WHERE facilityTypeId = '{ftype_norm}' "
                f"AND (UPPER(address_stateOrRegion) LIKE '%{place.upper()}%' OR UPPER(address_city) LIKE '%{place.upper()}%') "
                "LIMIT 20;"
            )

        m = re.search(r"(which|find)\s+facilities\s+.*\s+(offer|offers|have|has)\s+([a-z0-9_\\-\\s]+)\\??$", q, re.IGNORECASE)
        if m:
            specialty = m.group(3).strip()
            return (
                "SELECT DISTINCT name, address_city, address_stateOrRegion, facilityTypeId "
                "FROM facilities "
                f"WHERE specialties LIKE '%{specialty}%' "
                "LIMIT 20;"
            )

        return None

    def _ensure_db(self, csv_path: str):
        """Create a SQLite database from the CSV if it doesn't exist."""
        if os.path.exists(self.db_path):
            return

        print("🗄️  Building SQLite database from CSV...")
        df = pd.read_csv(csv_path)

        # Rename 'procedure' column to avoid SQL keyword conflict
        if "procedure" in df.columns:
            df = df.rename(columns={"procedure": "procedure_text"})

        conn = sqlite3.connect(self.db_path)
        df.to_sql("facilities", conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ SQLite database created at {self.db_path}")

    def generate_sql(self, question: str) -> str:
        """Use the LLM to convert a question to SQL."""
        prompt = f"""You are a SQL expert. Convert this natural language question to a SQLite query.

{TABLE_SCHEMA}

Question: {question}

Rules:
- Return ONLY the raw SQL query, no markdown, no explanation
- Use COUNT(DISTINCT pk_unique_id) when counting organizations
- Use LIKE for text searches within JSON array columns
- Limit results to 20 rows max unless user asks for all
- Always include the name column in SELECT

SQL:"""

        if self.llm is None:
            fallback = self._heuristic_sql(question)
            if fallback:
                return fallback
            raise RuntimeError(
                "No OPENAI_API_KEY is set, and no heuristic SQL mapping matched this question. "
                "Try: 'How many hospitals in Accra?' or 'List clinics in Ashanti region'."
            )

        try:
            response = self.llm.invoke(prompt)
            sql = response.content.strip()
        except Exception as e:
            if self._is_quota_error(e):
                fallback = self._heuristic_sql(question)
                if fallback:
                    return fallback
                raise RuntimeError(
                    "OpenAI quota exceeded and no heuristic SQL mapping matched this question. "
                    "Try: 'How many hospitals in Accra?' or 'List clinics in Ashanti region'."
                )
            raise

        # Clean up common LLM output issues
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql

    def execute(self, sql: str) -> str:
        """Execute SQL and return formatted results."""
        try:
            conn = sqlite3.connect(self.db_path)
            result = pd.read_sql_query(sql, conn)
            conn.close()

            if result.empty:
                return "No results found."

            # Format nicely for the LLM
            return result.to_string(index=False, max_rows=25)

        except Exception as e:
            return f"SQL Error: {str(e)}"

    def ask(self, question: str) -> tuple:
        """Full pipeline: question → SQL → results."""
        sql = self.generate_sql(question)
        result = self.execute(sql)
        return sql, result


# ── Quick test ──
if __name__ == "__main__":
    t2s = Text2SQL()
    question = "How many hospitals are in Accra?"
    sql, result = t2s.ask(question)
    print(f"Question: {question}")
    print(f"SQL: {sql}")
    print(f"Result:\n{result}")
