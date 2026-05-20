"""
LanceDB Vector Store — semantic search over Ghana healthcare facilities.

This is the RAG backbone. It embeds facility descriptions and lets the
agent find relevant facilities by meaning, not just keywords.
"""

import os
import json
import pandas as pd
import lancedb
from sentence_transformers import SentenceTransformer

# Use a small, fast model — good enough for hackathon
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def _maybe_parse_json_list(val: object) -> list[str] | None:
    """
    Some CSV columns contain JSON arrays serialized as strings, e.g.:
    ["ophthalmology","internalMedicine"] or ["Phone: +233..."].
    Convert them to a list of strings when possible.
    """
    if val is None:
        return None
    if isinstance(val, list):
        return [str(x) for x in val if x is not None and str(x).strip()]

    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return None
    if not (s.startswith("[") and s.endswith("]")):
        return None

    # pandas CSV escaping produces doubled quotes inside JSON-like strings
    # e.g. [""]a""] -> ["a"] after normalization
    try_candidates = [s, s.replace('""', '"')]
    for cand in try_candidates:
        try:
            parsed = json.loads(cand)
            if isinstance(parsed, list):
                out = [str(x) for x in parsed if x is not None and str(x).strip()]
                return out if out else None
        except Exception:
            continue
    return None


def _build_search_text(row: pd.Series) -> str:
    """Combine key columns into one searchable string per facility."""
    parts = []
    cols = [
        "name",
        "description",
        "specialties",
        "capability",
        "procedure",
        "equipment",
        "address_city",
        "address_stateOrRegion",
        "facilityTypeId",
        "operatorTypeId",
        "organization_type",
        "phone_numbers",
        "email",
        "officialWebsite",
        "websites",
    ]
    for col in cols:
        raw = row.get(col, "")
        parsed_list = _maybe_parse_json_list(raw)
        if parsed_list:
            parts.extend(parsed_list)
            continue

        val = str(raw).strip()
        if val and val.lower() not in {"nan", "null", "none"}:
            parts.append(val)
    return " ".join(parts)


def create_vectorstore(csv_path: str, db_path: str = "./data/lancedb"):
    """
    One-time setup: read CSV, embed every row, store in LanceDB.
    Run this ONCE, then the agent just calls `search()`.
    """
    print("[vectorstore] Loading CSV...")
    df = pd.read_csv(csv_path)

    # Drop rows with no name
    df = df.dropna(subset=["name"])

    # Build the text we'll embed
    print("[vectorstore] Building search text...")
    df["search_text"] = df.apply(_build_search_text, axis=1)

    # Generate embeddings (takes ~30 seconds for 1000 rows)
    print("[vectorstore] Generating embeddings (this may take a bit)...")
    embeddings = EMBED_MODEL.encode(
        df["search_text"].tolist(),
        show_progress_bar=True,
        batch_size=64,
    )
    df["vector"] = embeddings.tolist()

    # Keep only useful columns to avoid LanceDB issues with messy data
    keep_cols = [
        "name", "pk_unique_id", "organization_type", "facilityTypeId",
        "operatorTypeId", "address_city", "address_stateOrRegion",
        "address_country", "specialties", "description", "capability",
        "procedure", "equipment", "phone_numbers", "email",
        "officialWebsite", "capacity", "yearEstablished",
        "search_text", "vector",
    ]
    # Only keep columns that actually exist
    keep_cols = [c for c in keep_cols if c in df.columns]
    df_store = df[keep_cols].copy()

    # Normalize non-vector columns to strings to avoid Arrow type issues
    # (some columns like capacity can contain floats/ints mixed with strings)
    for col in df_store.columns:
        if col == "vector":
            continue
        s = df_store[col]
        s = s.fillna("")
        s = s.map(lambda v: "" if v in ("", None) else str(v))
        s = s.replace({"nan": "", "None": "", "null": ""})
        df_store[col] = s

    # Write to LanceDB
    print(f"[vectorstore] Writing to LanceDB at {db_path}...")
    os.makedirs(db_path, exist_ok=True)
    db = lancedb.connect(db_path)
    table = db.create_table("healthcare", df_store, mode="overwrite")
    print(f"[vectorstore] Done. Stored {len(df_store)} records.")
    return table


def search(query: str, db_path: str = "./data/lancedb", top_k: int = 5) -> str:
    """
    Semantic search: find the most relevant facilities for a query.
    Returns a formatted string the LLM can use as context.
    """
    db = lancedb.connect(db_path)
    table = db.open_table("healthcare")

    # Embed the query
    query_vec = EMBED_MODEL.encode([query])[0].tolist()

    # Search
    results = table.search(query_vec).limit(top_k).to_pandas()

    if results.empty:
        return "No matching facilities found."

    # Format results for the LLM
    context_parts = []
    for i, row in results.iterrows():
        uid = row.get("pk_unique_id", "")
        name = row.get('name', 'Unknown')
        entry = f"**{name}**"
        if uid:
            entry += f" [ID: {uid}]"

        ftype = row.get("facilityTypeId", "")
        if ftype:
            entry += f" ({ftype})"

        city = row.get("address_city", "")
        region = row.get("address_stateOrRegion", "")
        if city or region:
            entry += f" — {city}, {region}".rstrip(", ")

        desc = row.get("description", "")
        if desc:
            entry += f"\nDescription: {desc}"

        specs = row.get("specialties", "")
        if specs and specs != "[]":
            entry += f"\nSpecialties: {specs}"

        cap = row.get("capability", "")
        if cap and cap != "[]":
            entry += f"\nCapabilities: {cap}"

        equip = row.get("equipment", "")
        if equip and equip != "[]":
            entry += f"\nEquipment: {equip}"

        phone = row.get("phone_numbers", "")
        if phone:
            entry += f"\nPhone: {phone}"

        email = row.get("email", "")
        if email:
            entry += f"\nEmail: {email}"

        context_parts.append(entry)

    return "\n\n---\n\n".join(context_parts)


# ── Run this file directly to build the vector store ──
if __name__ == "__main__":
    import sys
    csv = sys.argv[1] if len(sys.argv) > 1 else "./data/ghana_healthcare.csv"
    create_vectorstore(csv)
