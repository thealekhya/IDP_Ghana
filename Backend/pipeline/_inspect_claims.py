"""Inspect what specialties, equipment, and capabilities actually look like in the data."""
import pandas as pd
import json
import os

df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ghana_healthcare.csv"))

def parse_json_col(val):
    if pd.isna(val): return []
    s = str(val).strip()
    if not s or s.lower() in {"nan","none","null","[]"}: return []
    for cand in [s, s.replace('""','"')]:
        try:
            p = json.loads(cand)
            if isinstance(p, list): return [str(x).strip() for x in p if str(x).strip()]
        except: pass
    return [s] if s else []

# Collect all unique specialties
all_specs = set()
for v in df["specialties"].dropna():
    all_specs.update(parse_json_col(v))
print("=== ALL SPECIALTIES ===")
for s in sorted(all_specs):
    print(f"  {s}")
print(f"\nTotal unique specialties: {len(all_specs)}")

# Collect all unique equipment
all_equip = set()
for v in df["equipment"].dropna():
    all_equip.update(parse_json_col(v))
print(f"\n=== ALL EQUIPMENT (first 50) ===")
for e in sorted(all_equip)[:50]:
    print(f"  {e}")
print(f"\nTotal unique equipment items: {len(all_equip)}")

# Collect all unique capabilities
all_cap = set()
for v in df["capability"].dropna():
    all_cap.update(parse_json_col(v))
print(f"\n=== ALL CAPABILITIES (first 50) ===")
for c in sorted(all_cap)[:50]:
    print(f"  {c}")
print(f"\nTotal unique capabilities: {len(all_cap)}")

# Collect all unique procedures
all_proc = set()
if "procedure" in df.columns:
    for v in df["procedure"].dropna():
        all_proc.update(parse_json_col(v))
print(f"\n=== ALL PROCEDURES (first 50) ===")
for p in sorted(all_proc)[:50]:
    print(f"  {p}")
print(f"\nTotal unique procedures: {len(all_proc)}")

# Show a few rows with specialties + equipment side by side
print("\n=== SAMPLE: Specialty vs Equipment pairs ===")
count = 0
for _, row in df.iterrows():
    specs = parse_json_col(row.get("specialties",""))
    equip = parse_json_col(row.get("equipment",""))
    caps = parse_json_col(row.get("capability",""))
    if specs and len(specs) > 1:
        name = row.get("name","?")
        ftype = row.get("facilityTypeId","?")
        print(f"\n{name} ({ftype}):")
        print(f"  Specialties: {specs}")
        print(f"  Equipment:   {equip[:5]}{'...' if len(equip)>5 else ''}")
        print(f"  Capabilities:{caps[:5]}{'...' if len(caps)>5 else ''}")
        count += 1
        if count >= 8: break

# Region + city coverage
print("\n=== CITIES WITH COUNTS ===")
print(df["address_city"].value_counts().head(20))
