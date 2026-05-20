"""Just list specialties."""
import pandas as pd, json, os
df = pd.read_csv(os.path.join("data", "ghana_healthcare.csv"))
def p(v):
    if pd.isna(v): return []
    s = str(v).strip()
    if not s or s.lower() in {"nan","none","null","[]"}: return []
    for c in [s, s.replace('""','"')]:
        try:
            r = json.loads(c)
            if isinstance(r,list): return [str(x).strip() for x in r if str(x).strip()]
        except: pass
    return []
all_s = set()
for v in df["specialties"].dropna():
    all_s.update(p(v))
for s in sorted(all_s):
    print(s)
print(f"\nTotal: {len(all_s)}")
