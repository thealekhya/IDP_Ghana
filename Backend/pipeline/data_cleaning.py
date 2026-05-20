"""
Data Cleaning Pipeline — standardizes and deduplicates the Ghana healthcare dataset.

This module:
  1. Deduplicates rows by pk_unique_id (same facility from multiple source URLs)
  2. Standardizes region names (e.g. "Ashanti" / "Ashanti Region" / "ASHANTI" → "Ashanti")
  3. Parses JSON array columns (specialties, procedure, equipment, capability)
  4. Handles nulls, data types, and formatting issues
  5. Flags data quality anomalies

Usage:
    python -m pipeline.data_cleaning          # Cleans CSV → writes cleaned CSV + rebuilds DBs
    from pipeline.data_cleaning import clean_dataframe
"""

import os
import re
import json
import pandas as pd
import numpy as np
from typing import Optional


# ── Region name mapping ──
# The dataset has wildly inconsistent region names
REGION_MAPPING = {
    # Greater Accra variations
    "greater accra": "Greater Accra",
    "greater accra region": "Greater Accra",
    "accra": "Greater Accra",
    "accra region": "Greater Accra",
    "accra metropolitan": "Greater Accra",
    "ga": "Greater Accra",
    # Ashanti
    "ashanti": "Ashanti",
    "ashanti region": "Ashanti",
    "kumasi": "Ashanti",
    # Western
    "western": "Western",
    "western region": "Western",
    "western north": "Western North",
    "western north region": "Western North",
    # Northern
    "northern": "Northern",
    "northern region": "Northern",
    "north east": "North East",
    "north east region": "North East",
    # Volta
    "volta": "Volta",
    "volta region": "Volta",
    # Central
    "central": "Central",
    "central region": "Central",
    # Bono / Brong Ahafo
    "bono": "Bono",
    "bono region": "Bono",
    "bono east": "Bono East",
    "bono east region": "Bono East",
    "brong ahafo": "Bono",
    "brong-ahafo": "Bono",
    "brong ahafo region": "Bono",
    # Eastern
    "eastern": "Eastern",
    "eastern region": "Eastern",
    # Upper East
    "upper east": "Upper East",
    "upper east region": "Upper East",
    # Upper West
    "upper west": "Upper West",
    "upper west region": "Upper West",
    # Ahafo
    "ahafo": "Ahafo",
    "ahafo region": "Ahafo",
    # Savannah
    "savannah": "Savannah",
    "savannah region": "Savannah",
    # Oti
    "oti": "Oti",
    "oti region": "Oti",
}


def _safe_parse_json(val) -> list:
    """Parse a JSON array string to a Python list. Returns [] on failure."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "null", "[]", ""}:
        return []

    # Try direct parse
    for candidate in [s, s.replace('""', '"')]:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if x is not None and str(x).strip()]
            return [str(parsed)]
        except (json.JSONDecodeError, ValueError):
            continue

    # Fallback: comma-separated
    if "," in s:
        return [x.strip().strip("'\"") for x in s.split(",") if x.strip()]

    return [s] if s else []


def standardize_region(region_val) -> Optional[str]:
    """Map messy region names to standardized form."""
    if region_val is None or (isinstance(region_val, float) and np.isnan(region_val)):
        return None
    raw = str(region_val).strip()
    if not raw or raw.lower() in {"nan", "none", "null"}:
        return None

    key = raw.lower().strip()
    # Remove trailing "region" if present for matching
    if key in REGION_MAPPING:
        return REGION_MAPPING[key]

    # Try partial matching
    for pattern, standard in REGION_MAPPING.items():
        if pattern in key or key in pattern:
            return standard

    # Return cleaned original if no match
    return raw.title()


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate by pk_unique_id — keep the row with the most non-null values.
    The dataset has duplicates because the same facility appears from multiple source URLs.
    """
    if "pk_unique_id" not in df.columns:
        return df

    # Count non-null values per row as a quality score
    df["_quality_score"] = df.notna().sum(axis=1)

    # Sort by quality score (descending) and drop duplicates
    df = df.sort_values("_quality_score", ascending=False)
    df = df.drop_duplicates(subset=["pk_unique_id"], keep="first")
    df = df.drop(columns=["_quality_score"])

    return df.reset_index(drop=True)


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag suspicious data and return a DataFrame of anomalies.
    """
    anomalies = []

    for idx, row in df.iterrows():
        name = row.get("name", "Unknown")
        uid = row.get("pk_unique_id", idx)
        issues = []

        # Hospital with 0 doctors but has capacity
        capacity = row.get("capacity")
        n_doctors = row.get("numberDoctors")
        if (capacity and pd.notna(capacity) and float(capacity) > 0 and
                (n_doctors is None or (pd.notna(n_doctors) and float(n_doctors) == 0))):
            issues.append("Hospital has bed capacity but 0 doctors reported")

        # No contact info at all
        phone = row.get("phone_numbers", "")
        email = row.get("email", "")
        website = row.get("officialWebsite", "")
        if (not phone or str(phone).lower() in {"nan", "none", "[]", ""}) and \
           (not email or str(email).lower() in {"nan", "none", ""}) and \
           (not website or str(website).lower() in {"nan", "none", ""}):
            issues.append("No contact information (phone, email, or website)")

        # Facility claiming specialties but has no equipment mentioned
        specialties = _safe_parse_json(row.get("specialties", ""))
        equipment = _safe_parse_json(row.get("equipment", ""))
        if len(specialties) > 3 and len(equipment) == 0:
            issues.append(f"Claims {len(specialties)} specialties but no equipment listed")

        # No region
        region = row.get("address_stateOrRegion", "")
        if not region or str(region).lower() in {"nan", "none", ""}:
            issues.append("Missing region/state information")

        if issues:
            for issue in issues:
                anomalies.append({
                    "pk_unique_id": uid,
                    "facility_name": name,
                    "anomaly_type": issue,
                })

    return pd.DataFrame(anomalies)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline for the Ghana healthcare dataset.

    Steps:
      1. Deduplicate by pk_unique_id
      2. Standardize region names
      3. Clean JSON array columns
      4. Normalize facility types
      5. Handle nulls
    """
    original_len = len(df)

    # Step 1: Deduplicate
    df = deduplicate(df)
    deduped_len = len(df)
    print(f"[clean] Deduplication: {original_len} → {deduped_len} rows ({original_len - deduped_len} duplicates removed)")

    # Step 2: Standardize regions
    if "address_stateOrRegion" in df.columns:
        df["address_stateOrRegion"] = df["address_stateOrRegion"].apply(standardize_region)
        print(f"[clean] Standardized region names: {df['address_stateOrRegion'].nunique()} unique regions")

    # Step 3: Parse and re-serialize JSON array columns as clean JSON
    json_cols = ["specialties", "procedure", "equipment", "capability", "phone_numbers"]
    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda v: json.dumps(_safe_parse_json(v)))

    # Step 4: Normalize facility type spellings
    if "facilityTypeId" in df.columns:
        ftype_map = {
            "farmacy": "pharmacy",
            "pharmacy": "pharmacy",
            "hospital": "hospital",
            "clinic": "clinic",
            "doctor": "doctor",
            "dentist": "dentist",
        }
        df["facilityTypeId"] = df["facilityTypeId"].apply(
            lambda v: ftype_map.get(str(v).strip().lower(), str(v).strip()) if pd.notna(v) else v
        )

    # Step 5: Clean string columns — trim whitespace, replace empty-like with None
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].apply(
            lambda v: None if (v is None or str(v).strip().lower() in {"nan", "none", "null", ""}) else str(v).strip()
        )

    # Step 6: Ensure country is "Ghana"
    if "address_country" in df.columns:
        df["address_country"] = df["address_country"].fillna("Ghana")

    print(f"[clean] Cleaning complete: {len(df)} rows, {len(df.columns)} columns")
    return df


def clean_and_rebuild(
    csv_path: str = None,
    output_csv: str = None,
    rebuild_dbs: bool = True,
):
    """
    Full pipeline: clean CSV → save cleaned CSV → rebuild SQLite + LanceDB.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))

    if csv_path is None:
        csv_path = os.path.join(base_dir, "data", "ghana_healthcare.csv")
    if output_csv is None:
        output_csv = os.path.join(base_dir, "data", "ghana_healthcare_clean.csv")

    print(f"[clean] Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"[clean] Loaded {len(df)} rows, {len(df.columns)} columns")

    # Clean
    df_clean = clean_dataframe(df)

    # Detect anomalies
    anomalies = detect_anomalies(df_clean)
    anomaly_path = os.path.join(base_dir, "data", "anomalies.csv")
    if not anomalies.empty:
        anomalies.to_csv(anomaly_path, index=False)
        print(f"[clean] ⚠️  Found {len(anomalies)} anomalies → saved to {anomaly_path}")

        # Print summary
        print("\n[clean] Anomaly Summary:")
        for atype, count in anomalies["anomaly_type"].value_counts().items():
            print(f"  • {atype}: {count}")
    else:
        print("[clean] ✅ No anomalies detected")

    # Save cleaned CSV
    df_clean.to_csv(output_csv, index=False)
    print(f"\n[clean] Saved cleaned dataset → {output_csv}")

    # Rebuild databases
    if rebuild_dbs:
        _rebuild_databases(df_clean, base_dir)

    return df_clean


def _rebuild_databases(df_clean: pd.DataFrame, base_dir: str):
    """Rebuild SQLite and LanceDB from the cleaned DataFrame."""
    import sqlite3

    # ── Rebuild SQLite ──
    db_path = os.path.join(base_dir, "data", "ghana_healthcare.db")
    print(f"\n[clean] Rebuilding SQLite database at {db_path}...")

    # Rename 'procedure' to 'procedure_text' for SQL keyword safety
    df_sql = df_clean.copy()
    if "procedure" in df_sql.columns:
        df_sql = df_sql.rename(columns={"procedure": "procedure_text"})

    conn = sqlite3.connect(db_path)
    df_sql.to_sql("facilities", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[clean] ✅ SQLite rebuilt with {len(df_sql)} rows")

    # ── Rebuild LanceDB ──
    lance_path = os.path.join(base_dir, "data", "lancedb")
    print(f"\n[clean] Rebuilding LanceDB vector store at {lance_path}...")

    # Save cleaned CSV temporarily for the vectorstore builder
    temp_csv = os.path.join(base_dir, "data", "ghana_healthcare_clean.csv")
    df_clean.to_csv(temp_csv, index=False)

    from backend.vectorstore.lancedb_store import create_vectorstore
    create_vectorstore(temp_csv, lance_path)
    print("[clean] ✅ LanceDB rebuilt with embeddings")


# ── CLI entry point ──
if __name__ == "__main__":
    clean_and_rebuild()
