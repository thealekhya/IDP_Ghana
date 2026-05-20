import json
import csv

JSON_FILE = "ui/public/hospitals_data.json"
CSV_FILE = "Virtue Foundation Ghana v0.3 - Sheet1.csv"

# Load JSON
with open(JSON_FILE, "r", encoding="utf-8") as f:
    hospitals = json.load(f)

# Load CSV data into a dictionary by name for fast lookup
csv_data = {}
with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("name", "")
        if name and name not in csv_data:
            csv_data[name] = row

# Helper to parse stringified JSON arrays like '["internalMedicine"]' or just return empty
def parse_json_array(raw_str):
    if not raw_str or raw_str == 'null':
        return []
    try:
        parsed = json.loads(raw_str)
        return parsed if isinstance(parsed, list) else []
    except:
        return []

# Merge
for h in hospitals:
    name = h.get("name", "")
    if name in csv_data:
        row = csv_data[name]
        
        h["specialties"] = parse_json_array(row.get("specialties", ""))
        h["capabilities"] = parse_json_array(row.get("capability", ""))
        h["equipment"] = parse_json_array(row.get("equipment", ""))
        h["procedure"] = parse_json_array(row.get("procedure", ""))
        
        phones = parse_json_array(row.get("phone_numbers", ""))
        h["phone"] = phones[0] if phones else None
        
        email = row.get("email", None)
        h["email"] = email if email != 'null' else None
        
        desc = row.get("description", "")
        h["description"] = desc if desc != 'null' else None

# Save updated JSON
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(hospitals, f, indent=2)

print("Merged successfully!")
