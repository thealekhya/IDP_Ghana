"""
Medical Desert Detection — identifies healthcare coverage gaps across Ghana.

This is the SOCIAL IMPACT module (25% of hackathon score).
It analyzes the dataset to find regions with inadequate healthcare coverage,
missing specialties, and other critical gaps.
"""

import sqlite3
import os
import pandas as pd


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ghana_healthcare.db")


def _query_db(sql: str) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def get_region_facility_counts() -> pd.DataFrame:
    """Count distinct facilities per region, broken down by type."""
    return _query_db("""
        SELECT
            CASE
                WHEN UPPER(address_stateOrRegion) LIKE '%GREATER ACCRA%' OR UPPER(address_stateOrRegion) = 'ACCRA' THEN 'Greater Accra'
                WHEN UPPER(address_stateOrRegion) LIKE '%ASHANTI%' THEN 'Ashanti'
                WHEN UPPER(address_stateOrRegion) LIKE '%WESTERN%' THEN 'Western'
                WHEN UPPER(address_stateOrRegion) LIKE '%NORTHERN%' THEN 'Northern'
                WHEN UPPER(address_stateOrRegion) LIKE '%VOLTA%' THEN 'Volta'
                WHEN UPPER(address_stateOrRegion) LIKE '%CENTRAL%' AND UPPER(address_stateOrRegion) NOT LIKE '%CENTRAL TONGU%' THEN 'Central'
                WHEN UPPER(address_stateOrRegion) LIKE '%BONO%' OR UPPER(address_stateOrRegion) LIKE '%BRONG%' THEN 'Bono/Brong Ahafo'
                WHEN UPPER(address_stateOrRegion) LIKE '%EASTERN%' THEN 'Eastern'
                WHEN UPPER(address_stateOrRegion) LIKE '%UPPER EAST%' THEN 'Upper East'
                WHEN UPPER(address_stateOrRegion) LIKE '%UPPER WEST%' THEN 'Upper West'
                WHEN UPPER(address_stateOrRegion) LIKE '%AHAFO%' THEN 'Ahafo'
                WHEN UPPER(address_stateOrRegion) LIKE '%SAVANNAH%' THEN 'Savannah'
                WHEN UPPER(address_stateOrRegion) LIKE '%NORTH EAST%' THEN 'North East'
                WHEN UPPER(address_stateOrRegion) LIKE '%OTI%' THEN 'Oti'
                WHEN UPPER(address_stateOrRegion) LIKE '%WESTERN NORTH%' THEN 'Western North'
                WHEN address_stateOrRegion IS NULL OR TRIM(address_stateOrRegion) = '' THEN 'Unknown'
                ELSE TRIM(address_stateOrRegion)
            END AS region,
            COUNT(DISTINCT pk_unique_id) AS total_facilities,
            COUNT(DISTINCT CASE WHEN facilityTypeId = 'hospital' THEN pk_unique_id END) AS hospitals,
            COUNT(DISTINCT CASE WHEN facilityTypeId = 'clinic' THEN pk_unique_id END) AS clinics,
            COUNT(DISTINCT CASE WHEN facilityTypeId = 'doctor' THEN pk_unique_id END) AS doctors,
            COUNT(DISTINCT CASE WHEN facilityTypeId = 'dentist' THEN pk_unique_id END) AS dentists,
            COUNT(DISTINCT CASE WHEN facilityTypeId = 'farmacy' THEN pk_unique_id END) AS pharmacies,
            COUNT(DISTINCT CASE WHEN organization_type = 'ngo' THEN pk_unique_id END) AS ngos
        FROM facilities
        WHERE region != 'Unknown'
        GROUP BY region
        ORDER BY total_facilities ASC
    """)


def get_specialty_coverage() -> pd.DataFrame:
    """For each major specialty, show which regions have it and which don't."""
    # Key specialties that matter for healthcare coverage
    specialties = [
        "ophthalmology", "pediatrics", "cardiology", "generalSurgery",
        "emergencyMedicine", "gynecologyAndObstetrics", "internalMedicine",
        "orthopedicSurgery", "dentistry", "familyMedicine",
    ]

    rows = []
    for spec in specialties:
        df = _query_db(f"""
            SELECT DISTINCT
                CASE
                    WHEN UPPER(address_stateOrRegion) LIKE '%GREATER ACCRA%' OR UPPER(address_stateOrRegion) = 'ACCRA' THEN 'Greater Accra'
                    WHEN UPPER(address_stateOrRegion) LIKE '%ASHANTI%' THEN 'Ashanti'
                    WHEN UPPER(address_stateOrRegion) LIKE '%WESTERN%' THEN 'Western'
                    WHEN UPPER(address_stateOrRegion) LIKE '%NORTHERN%' THEN 'Northern'
                    WHEN UPPER(address_stateOrRegion) LIKE '%VOLTA%' THEN 'Volta'
                    WHEN UPPER(address_stateOrRegion) LIKE '%CENTRAL%' AND UPPER(address_stateOrRegion) NOT LIKE '%CENTRAL TONGU%' THEN 'Central'
                    WHEN UPPER(address_stateOrRegion) LIKE '%BONO%' OR UPPER(address_stateOrRegion) LIKE '%BRONG%' THEN 'Bono/Brong Ahafo'
                    WHEN UPPER(address_stateOrRegion) LIKE '%EASTERN%' THEN 'Eastern'
                    WHEN UPPER(address_stateOrRegion) LIKE '%UPPER EAST%' THEN 'Upper East'
                    WHEN UPPER(address_stateOrRegion) LIKE '%UPPER WEST%' THEN 'Upper West'
                    ELSE TRIM(address_stateOrRegion)
                END AS region
            FROM facilities
            WHERE specialties LIKE '%{spec}%'
              AND address_stateOrRegion IS NOT NULL
              AND TRIM(address_stateOrRegion) != ''
        """)
        regions_with = set(df["region"].tolist()) if not df.empty else set()
        rows.append({"specialty": spec, "regions_with_coverage": regions_with, "count": len(regions_with)})

    return pd.DataFrame(rows)


def get_public_private_balance() -> pd.DataFrame:
    """Show public vs private facility distribution per region."""
    return _query_db("""
        SELECT
            CASE
                WHEN UPPER(address_stateOrRegion) LIKE '%GREATER ACCRA%' OR UPPER(address_stateOrRegion) = 'ACCRA' THEN 'Greater Accra'
                WHEN UPPER(address_stateOrRegion) LIKE '%ASHANTI%' THEN 'Ashanti'
                WHEN UPPER(address_stateOrRegion) LIKE '%WESTERN%' THEN 'Western'
                WHEN UPPER(address_stateOrRegion) LIKE '%NORTHERN%' THEN 'Northern'
                WHEN UPPER(address_stateOrRegion) LIKE '%VOLTA%' THEN 'Volta'
                WHEN UPPER(address_stateOrRegion) LIKE '%CENTRAL%' AND UPPER(address_stateOrRegion) NOT LIKE '%CENTRAL TONGU%' THEN 'Central'
                WHEN UPPER(address_stateOrRegion) LIKE '%BONO%' OR UPPER(address_stateOrRegion) LIKE '%BRONG%' THEN 'Bono/Brong Ahafo'
                WHEN UPPER(address_stateOrRegion) LIKE '%EASTERN%' THEN 'Eastern'
                WHEN UPPER(address_stateOrRegion) LIKE '%UPPER EAST%' THEN 'Upper East'
                WHEN UPPER(address_stateOrRegion) LIKE '%UPPER WEST%' THEN 'Upper West'
                WHEN address_stateOrRegion IS NULL OR TRIM(address_stateOrRegion) = '' THEN 'Unknown'
                ELSE TRIM(address_stateOrRegion)
            END AS region,
            COUNT(DISTINCT CASE WHEN operatorTypeId = 'public' THEN pk_unique_id END) AS public_facilities,
            COUNT(DISTINCT CASE WHEN operatorTypeId = 'private' THEN pk_unique_id END) AS private_facilities,
            COUNT(DISTINCT pk_unique_id) AS total
        FROM facilities
        WHERE region != 'Unknown'
        GROUP BY region
        ORDER BY total ASC
    """)


def run_full_gap_analysis() -> str:
    """
    Run a comprehensive medical desert analysis and return a formatted report.
    This is the main function called by the agent node.
    """
    report_parts = []

    # ── 1. Regional facility distribution ──
    report_parts.append("🏥 REGIONAL HEALTHCARE COVERAGE ANALYSIS")
    report_parts.append("=" * 55)

    region_df = get_region_facility_counts()
    if not region_df.empty:
        report_parts.append("\n📊 Facilities per Region (sorted by coverage, lowest first):\n")
        for _, row in region_df.iterrows():
            region = row["region"]
            total = row["total_facilities"]
            hosp = row["hospitals"]
            clinic = row["clinics"]
            doc = row["doctors"]
            dent = row["dentists"]
            pharm = row["pharmacies"]
            ngo = row["ngos"]

            # Flag regions with very low coverage
            flag = ""
            if total <= 5:
                flag = " ⚠️ CRITICAL — MEDICAL DESERT"
            elif total <= 15:
                flag = " ⚡ LOW COVERAGE"

            report_parts.append(
                f"  {region}: {total} facilities{flag}\n"
                f"    Hospitals: {hosp} | Clinics: {clinic} | Doctors: {doc} | "
                f"Dentists: {dent} | Pharmacies: {pharm} | NGOs: {ngo}"
            )

        # Identify the worst regions
        desert_regions = region_df[region_df["total_facilities"] <= 5]["region"].tolist()
        low_regions = region_df[(region_df["total_facilities"] > 5) & (region_df["total_facilities"] <= 15)]["region"].tolist()

        if desert_regions:
            report_parts.append(f"\n🚨 MEDICAL DESERTS (≤5 facilities): {', '.join(desert_regions)}")
        if low_regions:
            report_parts.append(f"⚡ LOW COVERAGE REGIONS (6-15 facilities): {', '.join(low_regions)}")

    # ── 2. Specialty coverage gaps ──
    report_parts.append("\n\n🔬 SPECIALTY COVERAGE ANALYSIS")
    report_parts.append("=" * 55)

    spec_df = get_specialty_coverage()
    all_known_regions = set(region_df["region"].tolist()) if not region_df.empty else set()

    if not spec_df.empty:
        for _, row in spec_df.iterrows():
            spec = row["specialty"]
            covered = row["regions_with_coverage"]
            missing = all_known_regions - covered

            status = "✅" if len(missing) == 0 else "⚠️" if len(missing) <= 3 else "🚨"
            report_parts.append(
                f"\n  {status} {spec}: available in {row['count']}/{len(all_known_regions)} regions"
            )
            if missing:
                report_parts.append(f"     MISSING in: {', '.join(sorted(missing))}")

    # ── 3. Public vs Private balance ──
    report_parts.append("\n\n⚖️ PUBLIC vs PRIVATE FACILITY BALANCE")
    report_parts.append("=" * 55)

    balance_df = get_public_private_balance()
    if not balance_df.empty:
        for _, row in balance_df.iterrows():
            region = row["region"]
            pub = row["public_facilities"]
            priv = row["private_facilities"]
            total = row["total"]

            flag = ""
            if pub == 0 and total > 0:
                flag = " ⚠️ NO PUBLIC FACILITIES"
            elif priv > 0 and pub > 0 and priv / (pub + priv) > 0.8:
                flag = " ⚡ Heavily private-sector dependent"

            report_parts.append(f"  {region}: Public={pub}, Private={priv}, Total={total}{flag}")

    # ── 4. Recommendations ──
    report_parts.append("\n\n💡 RECOMMENDATIONS FOR RESOURCE ALLOCATION")
    report_parts.append("=" * 55)

    if not region_df.empty:
        # Regions with no hospitals
        no_hospital = region_df[region_df["hospitals"] == 0]["region"].tolist()
        if no_hospital:
            report_parts.append(f"  🏗️  URGENT: Build hospitals in: {', '.join(no_hospital)}")

        # Regions with no dentists
        no_dentist = region_df[region_df["dentists"] == 0]["region"].tolist()
        if no_dentist:
            report_parts.append(f"  🦷 Dental care gap: {', '.join(no_dentist)}")

        # Regions with no pharmacies
        no_pharm = region_df[region_df["pharmacies"] == 0]["region"].tolist()
        if no_pharm:
            report_parts.append(f"  💊 Pharmacy access gap: {', '.join(no_pharm)}")

    if not spec_df.empty:
        # Specialties with worst coverage
        worst_specs = spec_df.nsmallest(3, "count")
        for _, row in worst_specs.iterrows():
            missing = all_known_regions - row["regions_with_coverage"]
            if missing:
                report_parts.append(
                    f"  🩺 Deploy {row['specialty']} specialists to: {', '.join(sorted(missing)[:5])}"
                )

    return "\n".join(report_parts)


def run_regional_gap_analysis(region: str) -> str:
    """Analyze a specific region's healthcare gaps."""
    region_upper = region.upper()

    # Get facilities in this region
    df = _query_db(f"""
        SELECT DISTINCT name, facilityTypeId, operatorTypeId, specialties,
                        capability, equipment, address_city
        FROM facilities
        WHERE UPPER(address_stateOrRegion) LIKE '%{region_upper}%'
           OR UPPER(address_city) LIKE '%{region_upper}%'
    """)

    if df.empty:
        return f"No facilities found for region matching '{region}'. This may indicate a medical desert or data gap."

    report = [f"🏥 HEALTHCARE ANALYSIS: {region.title()}", "=" * 50]
    report.append(f"\nTotal distinct facilities: {len(df)}")

    # Breakdown by type
    type_counts = df["facilityTypeId"].value_counts()
    report.append("\n📊 Facility Types:")
    for ftype, count in type_counts.items():
        if ftype and str(ftype).strip():
            report.append(f"  • {ftype}: {count}")

    # Operator breakdown
    op_counts = df["operatorTypeId"].value_counts()
    report.append("\n⚖️ Operator Types:")
    for op, count in op_counts.items():
        if op and str(op).strip():
            report.append(f"  • {op}: {count}")

    # Specialties present
    all_specs = set()
    for val in df["specialties"].dropna():
        if "," in str(val) or "[" in str(val):
            for s in str(val).replace("[", "").replace("]", "").replace('"', "").replace("'", "").split(","):
                s = s.strip()
                if s and s.lower() not in {"nan", "none", "null", ""}:
                    all_specs.add(s)

    if all_specs:
        report.append(f"\n🔬 Specialties Available ({len(all_specs)}):")
        for spec in sorted(all_specs):
            report.append(f"  • {spec}")

    # Missing critical specialties
    critical_specialties = {
        "emergencyMedicine", "generalSurgery", "internalMedicine",
        "pediatrics", "gynecologyAndObstetrics", "ophthalmology",
        "cardiology", "orthopedicSurgery",
    }
    missing = critical_specialties - all_specs
    if missing:
        report.append(f"\n🚨 MISSING Critical Specialties:")
        for m in sorted(missing):
            report.append(f"  ❌ {m}")

    # List facilities
    report.append(f"\n📋 Facilities in {region.title()}:")
    for _, row in df.head(20).iterrows():
        name = row.get("name", "Unknown")
        ftype = row.get("facilityTypeId", "")
        city = row.get("address_city", "")
        report.append(f"  • {name} ({ftype}) — {city}")

    if len(df) > 20:
        report.append(f"  ... and {len(df) - 20} more")

    return "\n".join(report)


# ── Quick test ──
if __name__ == "__main__":
    print(run_full_gap_analysis())
