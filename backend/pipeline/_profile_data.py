"""Quick data profiling script."""
import pandas as pd
import os

df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ghana_healthcare.csv"))
print(f"Rows: {len(df)}, Cols: {len(df.columns)}")
print()
print("Columns:", list(df.columns))
print()
print("Sample facility types:")
print(df["facilityTypeId"].value_counts())
print()
print("Sample regions:")
print(df["address_stateOrRegion"].value_counts().head(10))
print()
print("Nulls in key columns:")
for c in ["specialties","equipment","capability","procedure","capacity","numberDoctors","phone_numbers","email"]:
    if c in df.columns:
        null_count = df[c].isna().sum()
        print(f"  {c}: {null_count}/{len(df)} ({100*null_count/len(df):.0f}%)")
print()
print("Unique pk_unique_id:", df["pk_unique_id"].nunique(), "vs total rows:", len(df))
print()
print("Organization types:")
print(df["organization_type"].value_counts() if "organization_type" in df.columns else "N/A")
print()
print("Operator types:")
print(df["operatorTypeId"].value_counts() if "operatorTypeId" in df.columns else "N/A")
