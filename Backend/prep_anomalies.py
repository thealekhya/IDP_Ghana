import csv
import json

CSV_FILE = "data/medical_consistency_flags.csv"
JSON_FILE = "ui/public/anomalies.json"

anomalies = []
with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        anomalies.append(row)

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(anomalies, f, indent=2)

print(f"Processed {len(anomalies)} anomalies and saved to {JSON_FILE}")
