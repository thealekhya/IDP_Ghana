import csv
import json
import time
import urllib.request
import urllib.parse
import os

API_KEY = "6RPWewaZuVVZTTgm2cxp"
CSV_FILE = "Virtue Foundation Ghana v0.3 - Sheet1.csv"
OUTPUT_FILE = "ui/public/hospitals_data.json"

hospitals = []

print("Starting geocoding process...")
try:
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # We'll limit to 300 hospitals for the hackathon UI to keep the map fast
            # and to complete the script within a minute. 300 pins still looks very impressive!
            if count >= 300: 
                break
                
            name = row.get("name", "")
            city = row.get("address_city", "")
            if not name: continue
            
            # Formulate query for MapTiler API
            query = f"{name}, {city}, Ghana"
            url = f"https://api.maptiler.com/geocoding/{urllib.parse.quote(query)}.json?key={API_KEY}"
            
            try:
                req = urllib.request.urlopen(url)
                res = json.loads(req.read())
                features = res.get("features", [])
                
                if features:
                    # Get the first result's coordinates (Lng, Lat)
                    coords = features[0]["geometry"]["coordinates"]
                    hospitals.append({
                        "id": count,
                        "name": name,
                        "city": city,
                        "lat": coords[1],
                        "lng": coords[0],
                        "status": "Active Service"
                    })
            except Exception as e:
                # Silently ignore individual lookup failures to keep going
                pass
                
            count += 1
            if count % 20 == 0:
                print(f"Geocoded {count} hospitals...")
                
            time.sleep(0.2) # Rate limit protection

    # Ensure public folder exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(hospitals, f, indent=2)
        
    print(f"Successfully geocoded {len(hospitals)} hospitals and saved to {OUTPUT_FILE}")
except Exception as e:
    print(f"Error: {e}")
