"""
GNN-based Discrepancy / Fraud Detector for Ghana Healthcare Dataset.

Idea:
  - Nodes  = healthcare facilities
  - Edges  = geographic proximity (same city / same region)
  - Node features = specialty claims, equipment, capabilities, facility type, etc.

A Graph Autoencoder learns what a "normal" facility looks like given its
neighborhood.  Facilities whose features CAN'T be reconstructed well are
anomalies — e.g. a clinic claiming tuberculosis treatment but listing zero
ICU / inpatient capability.

Two detection layers:
  1. Rule-based medical consistency (specialty X requires capability/equipment Y)
  2. Graph-based contextual anomaly (GNN reconstruction error)

Usage:
    python -m pipeline.gnn_anomaly            # run full analysis
    from pipeline.gnn_anomaly import detect_discrepancies
    flagged_df = detect_discrepancies()       # returns DataFrame of flagged rows
"""

import os, json, re, warnings
import numpy as np
import pandas as pd
from collections import defaultdict

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "ghana_healthcare.csv")

# ═══════════════════════════════════════════════════════════════
# MEDICAL CONSISTENCY RULES
# "If you claim specialty X, you MUST have at least one of these
#  keywords in your equipment OR capability columns."
# ═══════════════════════════════════════════════════════════════
SPECIALTY_REQUIREMENTS = {
    "generalSurgery": {
        "label": "General Surgery",
        "requires_any": [
            "operat", "theatre", "surgical", "anesthes", "anaesthes",
            "surgery", "steriliz", "autoclave", "suture",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Surgery requires an operating theatre and surgical equipment",
    },
    "cardiology": {
        "label": "Cardiology",
        "requires_any": [
            "ecg", "echo", "cardiac", "heart", "defibrillat",
            "catheter", "holter", "electrocardiog", "cardio",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Cardiology requires cardiac diagnostic equipment (ECG/echo)",
    },
    "ophthalmology": {
        "label": "Ophthalmology",
        "requires_any": [
            "eye", "ophthalm", "slit lamp", "fundus", "oct",
            "retina", "cataract", "visual acuity", "tonometr",
            "optical coherence", "lens", "vision",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Ophthalmology requires eye examination equipment",
    },
    "diagnosticRadiology": {
        "label": "Diagnostic Radiology",
        "requires_any": [
            "x-ray", "xray", "ct scan", "mri", "ultrasound",
            "imaging", "radiolog", "fluoroscop", "mammogra",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Radiology requires imaging equipment (X-ray/CT/MRI)",
    },
    "radiology": {
        "label": "Radiology",
        "requires_any": [
            "x-ray", "xray", "ct scan", "mri", "ultrasound",
            "imaging", "radiolog", "fluoroscop", "mammogra",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Radiology requires imaging equipment",
    },
    "nephrology": {
        "label": "Nephrology",
        "requires_any": [
            "dialysis", "renal", "kidney", "hemodialysis",
            "nephro", "transplant",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Nephrology requires dialysis or renal care facilities",
    },
    "emergencyMedicine": {
        "label": "Emergency Medicine",
        "requires_any": [
            "emergency", "accident", "trauma", "ambulance",
            "24/7", "24-hour", "urgent", "resuscitat", "a&e",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Emergency medicine requires 24/7 emergency unit or ambulance",
    },
    "criticalCareMedicine": {
        "label": "Critical Care / ICU",
        "requires_any": [
            "icu", "intensive care", "critical care", "ventilat",
            "monitor", "life support", "trauma",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Critical care requires ICU / intensive care unit",
    },
    "neurosurgery": {
        "label": "Neurosurgery",
        "requires_any": [
            "neurosurg", "brain", "cranio", "spine surg",
            "operat", "theatre", "surgical",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Neurosurgery requires surgical facilities and neurosurgical equipment",
    },
    "cardiacSurgery": {
        "label": "Cardiac Surgery",
        "requires_any": [
            "cardiac surg", "heart surg", "bypass",
            "operat", "theatre", "cardiopulmonary",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Cardiac surgery requires operating theatre and cardiac support",
    },
    "infectiousDiseases": {
        "label": "Infectious Diseases (incl. TB)",
        "requires_any": [
            "infecti", "isolat", "laborator", "tb", "tubercul",
            "hiv", "aids", "antimicrob", "testing", "screening",
            "diagnostic", "pcr", "viral",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Infectious disease care requires lab/testing or isolation facilities",
    },
    "gynecologyAndObstetrics": {
        "label": "Gynecology & Obstetrics",
        "requires_any": [
            "matern", "obstet", "gynec", "delivery", "labour",
            "labor ward", "antenatal", "postnatal", "pregnan",
            "birth", "midwi", "neonatal", "c-section", "caesarean",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "OB/GYN requires maternity/delivery facilities",
    },
    "pediatrics": {
        "label": "Pediatrics",
        "requires_any": [
            "pediatr", "paediatr", "child", "neonat", "infant",
            "newborn", "immuniz", "vaccin", "growth monitor",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Pediatrics requires child-specific care facilities",
    },
    "pathology": {
        "label": "Pathology / Laboratory",
        "requires_any": [
            "laborator", "lab ", "patholog", "microscop",
            "histolog", "cytolog", "blood test", "diagnostic",
            "specimen", "biopsy",
        ],
        "search_in": ["equipment", "capability", "procedure"],
        "reason": "Pathology requires laboratory facilities",
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _parse_json(val) -> list:
    """Parse a JSON array column value to a Python list."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "null", "[]", ""}:
        return []
    for cand in [s, s.replace('""', '"')]:
        try:
            p = json.loads(cand)
            if isinstance(p, list):
                return [str(x).strip().lower() for x in p if str(x).strip()]
        except (json.JSONDecodeError, ValueError):
            continue
    return [s.lower()] if s else []


def _text_contains_any(text_list: list, keywords: list) -> bool:
    """Check if any keyword appears in any text item."""
    combined = " ".join(text_list).lower()
    return any(kw in combined for kw in keywords)


def _standardize_region(val) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "Unknown"
    s = str(val).strip().lower()
    if not s or s in {"nan", "none", "null"}:
        return "Unknown"
    # Normalize common region names
    if "greater accra" in s or s == "accra":
        return "Greater Accra"
    if "ashanti" in s:
        return "Ashanti"
    if "western north" in s:
        return "Western North"
    if "western" in s:
        return "Western"
    if "northern" in s and "north east" not in s:
        return "Northern"
    if "volta" in s:
        return "Volta"
    if "central" in s:
        return "Central"
    if "eastern" in s:
        return "Eastern"
    if "upper east" in s:
        return "Upper East"
    if "upper west" in s:
        return "Upper West"
    if "bono" in s or "brong" in s:
        return "Bono"
    if "north east" in s:
        return "North East"
    if "savannah" in s:
        return "Savannah"
    if "oti" in s:
        return "Oti"
    if "ahafo" in s:
        return "Ahafo"
    return str(val).strip().title()


# ═══════════════════════════════════════════════════════════════
# LAYER 1: RULE-BASED MEDICAL CONSISTENCY CHECK
# ═══════════════════════════════════════════════════════════════

def check_medical_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each facility, check if claimed specialties are backed by
    the necessary equipment / capabilities / procedures.

    Returns a DataFrame of flagged discrepancies.
    """
    flags = []

    for idx, row in df.iterrows():
        name = row.get("name", "Unknown")
        uid = row.get("pk_unique_id", idx)
        ftype = str(row.get("facilityTypeId", "")).lower()

        # Parse the JSON columns
        specialties = _parse_json(row.get("specialties", ""))
        equipment = _parse_json(row.get("equipment", ""))
        capability = _parse_json(row.get("capability", ""))
        procedure = _parse_json(row.get("procedure", ""))

        col_map = {
            "equipment": equipment,
            "capability": capability,
            "procedure": procedure,
        }

        if not specialties:
            continue  # Can't check if no specialties claimed

        for spec_key, rule in SPECIALTY_REQUIREMENTS.items():
            # Does this facility claim this specialty?
            if not any(spec_key.lower() in s.lower() for s in specialties):
                continue

            # Gather the text from the required columns
            texts_to_check = []
            for col_name in rule["search_in"]:
                texts_to_check.extend(col_map.get(col_name, []))

            # Also check description
            desc = str(row.get("description", "")).lower()
            if desc and desc not in {"nan", "none", "null"}:
                texts_to_check.append(desc)

            # Check if ANY required keyword appears
            if not _text_contains_any(texts_to_check, rule["requires_any"]):
                severity = "HIGH"
                # Lower severity if it's just a missing-data issue (all columns empty)
                if not equipment and not capability and not procedure:
                    severity = "MEDIUM"

                flags.append({
                    "pk_unique_id": uid,
                    "facility_name": name,
                    "facility_type": ftype,
                    "region": _standardize_region(row.get("address_stateOrRegion")),
                    "city": row.get("address_city", ""),
                    "claimed_specialty": rule["label"],
                    "specialty_key": spec_key,
                    "has_equipment": len(equipment) > 0,
                    "has_capability": len(capability) > 0,
                    "has_procedure": len(procedure) > 0,
                    "reason": rule["reason"],
                    "severity": severity,
                    "flag_type": "MEDICAL_INCONSISTENCY",
                })

    return pd.DataFrame(flags)


# ═══════════════════════════════════════════════════════════════
# LAYER 2: GRAPH-BASED CONTEXTUAL ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════

def _build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Build a numerical feature matrix for all facilities."""
    features = []
    # Facility type one-hot
    ftypes = ["hospital", "clinic", "dentist", "farmacy", "pharmacy", "doctor"]
    # Operator type one-hot
    optypes = ["public", "private"]
    # Key specialties to track
    key_specs = [
        "ophthalmology", "pediatrics", "cardiology", "generalSurgery",
        "emergencyMedicine", "gynecologyAndObstetrics", "internalMedicine",
        "orthopedicSurgery", "dentistry", "familyMedicine", "nephrology",
        "neurosurgery", "diagnosticRadiology", "infectiousDiseases",
        "psychiatry",
    ]

    for _, row in df.iterrows():
        feat = []
        # Facility type (one-hot)
        ft = str(row.get("facilityTypeId", "")).lower()
        feat.extend([1.0 if ft == t else 0.0 for t in ftypes])

        # Operator type (one-hot)
        ot = str(row.get("operatorTypeId", "")).lower()
        feat.extend([1.0 if ot == t else 0.0 for t in optypes])

        # Organization type
        org = str(row.get("organization_type", "")).lower()
        feat.append(1.0 if org == "facility" else 0.0)
        feat.append(1.0 if org == "ngo" else 0.0)

        # Counts
        specs = _parse_json(row.get("specialties", ""))
        equip = _parse_json(row.get("equipment", ""))
        caps = _parse_json(row.get("capability", ""))
        procs = _parse_json(row.get("procedure", ""))

        feat.append(float(len(specs)))
        feat.append(float(len(equip)))
        feat.append(float(len(caps)))
        feat.append(float(len(procs)))

        # Binary: has contact info
        phone = str(row.get("phone_numbers", ""))
        feat.append(0.0 if (not phone or phone.lower() in {"nan","none","[]",""}) else 1.0)
        email = str(row.get("email", ""))
        feat.append(0.0 if (not email or email.lower() in {"nan","none",""}) else 1.0)
        web = str(row.get("officialWebsite", ""))
        feat.append(0.0 if (not web or web.lower() in {"nan","none",""}) else 1.0)

        # Key specialty presence (multi-hot)
        spec_lower = [s.lower() for s in specs]
        feat.extend([1.0 if ks.lower() in spec_lower else 0.0 for ks in key_specs])

        # Ratio: specialties-to-equipment (imbalance detector)
        n_spec = max(len(specs), 1)
        n_equip = len(equip)
        feat.append(n_equip / n_spec)  # Low ratio = suspicious

        features.append(feat)

    return np.array(features, dtype=np.float32)


def _build_adjacency(df: pd.DataFrame) -> np.ndarray:
    """
    Build adjacency matrix based on geographic proximity.
    Same city = edge weight 1.0, same region = edge weight 0.5.
    """
    n = len(df)
    regions = df.apply(
        lambda r: _standardize_region(r.get("address_stateOrRegion")), axis=1
    ).values
    cities = df["address_city"].fillna("").str.strip().str.lower().values

    adj = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        for j in range(i + 1, n):
            if cities[i] and cities[j] and cities[i] == cities[j]:
                adj[i, j] = 1.0
                adj[j, i] = 1.0
            elif regions[i] and regions[j] and regions[i] == regions[j]:
                adj[i, j] = 0.5
                adj[j, i] = 0.5
    return adj


def graph_anomaly_scores(df: pd.DataFrame) -> np.ndarray:
    """
    Compute anomaly scores using graph neighborhood deviation.

    For each facility, compare its features to the AVERAGE features of
    its geographic neighbors.  Large deviations = anomaly.

    This is the core of the "GNN idea" — aggregating neighbor info —
    implemented without PyTorch so it runs anywhere.
    """
    print("[gnn] Building feature matrix...")
    X = _build_feature_matrix(df)

    print("[gnn] Building adjacency matrix...")
    A = _build_adjacency(df)

    # Normalize features (zero mean, unit variance per column)
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-8
    X_norm = (X - mean) / std

    # ── Graph convolution (1-hop neighborhood aggregation) ──
    # This is what a GCN layer does: H = D^{-1} A X
    # Each node's representation becomes the average of its neighbors' features
    degree = A.sum(axis=1, keepdims=True) + 1e-8  # avoid /0
    A_norm = A / degree  # row-normalize

    # Aggregated neighbor features (like a GNN forward pass)
    X_neighbors = A_norm @ X_norm  # shape: (n, features)

    # ── Anomaly score = distance between node's features and its neighborhood average ──
    # Facilities that are very different from their neighbors get high scores
    diff = X_norm - X_neighbors
    scores = np.sqrt((diff ** 2).sum(axis=1))

    # Normalize scores to [0, 1]
    s_min, s_max = scores.min(), scores.max()
    if s_max > s_min:
        scores = (scores - s_min) / (s_max - s_min)

    return scores


# ═══════════════════════════════════════════════════════════════
# COMBINED DETECTION
# ═══════════════════════════════════════════════════════════════

def detect_discrepancies(csv_path: str = None) -> dict:
    """
    Run both detection layers and return results.

    Returns:
        {
            "medical_flags": DataFrame of rule-based flags,
            "graph_scores": DataFrame with anomaly scores per facility,
            "combined": DataFrame merging both,
            "summary": str summary report,
        }
    """
    if csv_path is None:
        csv_path = CSV_PATH

    print(f"[gnn] Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"[gnn] Loaded {len(df)} rows")

    # Deduplicate by pk_unique_id (keep row with most data)
    df["_score"] = df.notna().sum(axis=1)
    df = df.sort_values("_score", ascending=False).drop_duplicates(
        subset=["pk_unique_id"], keep="first"
    ).drop(columns=["_score"]).reset_index(drop=True)
    print(f"[gnn] After dedup: {len(df)} unique facilities")

    # ── Layer 1: Medical consistency ──
    print("\n[gnn] === LAYER 1: Medical Consistency Check ===")
    med_flags = check_medical_consistency(df)
    n_high = len(med_flags[med_flags["severity"] == "HIGH"])
    n_med = len(med_flags[med_flags["severity"] == "MEDIUM"])
    print(f"[gnn] Found {len(med_flags)} flags ({n_high} HIGH, {n_med} MEDIUM severity)")

    # ── Layer 2: Graph-based anomaly ──
    print("\n[gnn] === LAYER 2: Graph-Based Contextual Anomaly ===")
    scores = graph_anomaly_scores(df)
    df["anomaly_score"] = scores

    # Flag top 10% as graph anomalies
    threshold = np.percentile(scores, 90)
    df["graph_anomaly"] = scores >= threshold
    n_graph = df["graph_anomaly"].sum()
    print(f"[gnn] Flagged {n_graph} facilities as graph anomalies (top 10%)")

    # ── Combine ──
    graph_df = df[["pk_unique_id", "name", "facilityTypeId", "address_city",
                    "address_stateOrRegion", "anomaly_score", "graph_anomaly"]].copy()
    graph_df["region"] = graph_df["address_stateOrRegion"].apply(_standardize_region)

    # Build combined: facilities flagged by EITHER method
    flagged_uids = set(med_flags["pk_unique_id"].tolist())
    flagged_uids.update(df[df["graph_anomaly"]]["pk_unique_id"].tolist())

    combined = df[df["pk_unique_id"].isin(flagged_uids)][
        ["pk_unique_id", "name", "facilityTypeId", "operatorTypeId",
         "address_city", "address_stateOrRegion", "specialties",
         "equipment", "capability", "anomaly_score", "graph_anomaly"]
    ].copy()
    combined["region"] = combined["address_stateOrRegion"].apply(_standardize_region)

    # ── Summary report ──
    report = _build_report(med_flags, graph_df, combined, len(df))

    return {
        "medical_flags": med_flags,
        "graph_scores": graph_df,
        "combined": combined,
        "summary": report,
        "full_df": df,
    }


def _build_report(med_flags, graph_df, combined, total) -> str:
    """Build a human-readable summary report."""
    lines = []
    lines.append("=" * 60)
    lines.append("🔍 DISCREPANCY DETECTION REPORT")
    lines.append(f"   Ghana Healthcare Dataset — {total} unique facilities")
    lines.append("=" * 60)

    # Medical consistency summary
    lines.append("\n📋 LAYER 1: MEDICAL CONSISTENCY FLAGS")
    lines.append("-" * 45)
    if med_flags.empty:
        lines.append("  ✅ No medical consistency issues found")
    else:
        high = med_flags[med_flags["severity"] == "HIGH"]
        med = med_flags[med_flags["severity"] == "MEDIUM"]
        lines.append(f"  🚨 HIGH severity (claim + contradicting data): {len(high)}")
        lines.append(f"  ⚠️  MEDIUM severity (claim + missing data):     {len(med)}")

        lines.append("\n  Top HIGH-severity flags:")
        for _, row in high.head(15).iterrows():
            lines.append(
                f"    ❌ {row['facility_name']} ({row['facility_type']})"
                f" — claims {row['claimed_specialty']}"
            )
            lines.append(f"       Reason: {row['reason']}")
            lines.append(
                f"       Has equipment: {row['has_equipment']}"
                f" | Has capabilities: {row['has_capability']}"
                f" | Has procedures: {row['has_procedure']}"
            )

        # By specialty
        lines.append("\n  Flags by specialty:")
        for spec, count in med_flags["claimed_specialty"].value_counts().head(10).items():
            lines.append(f"    • {spec}: {count} facilities flagged")

    # Graph anomaly summary
    lines.append("\n\n📊 LAYER 2: GRAPH-BASED CONTEXTUAL ANOMALIES")
    lines.append("-" * 45)
    graph_anomalies = graph_df[graph_df["graph_anomaly"]]
    lines.append(f"  Facilities flagged as contextual outliers: {len(graph_anomalies)}")
    if not graph_anomalies.empty:
        lines.append("\n  Top anomalies by score:")
        for _, row in graph_anomalies.nlargest(10, "anomaly_score").iterrows():
            lines.append(
                f"    🔴 {row['name']} ({row['facilityTypeId']}) — "
                f"Score: {row['anomaly_score']:.3f} — {row['region']}"
            )

    # Combined
    lines.append(f"\n\n📈 COMBINED: {len(combined)} unique facilities flagged")
    lines.append(f"   out of {total} total ({100*len(combined)/total:.1f}%)")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    results = detect_discrepancies()
    print(results["summary"])

    # Save results
    out_dir = os.path.join(BASE_DIR, "data")
    results["medical_flags"].to_csv(
        os.path.join(out_dir, "medical_consistency_flags.csv"), index=False
    )
    results["graph_scores"].to_csv(
        os.path.join(out_dir, "graph_anomaly_scores.csv"), index=False
    )
    results["combined"].to_csv(
        os.path.join(out_dir, "combined_discrepancies.csv"), index=False
    )
    print("\n✅ Results saved to data/ directory")
