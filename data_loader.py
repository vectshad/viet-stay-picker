"""
data_loader.py — Load and clean stays data from Excel
"""

import pandas as pd
import streamlit as st
from pathlib import Path

EXCEL_FILE = Path(__file__).parent / "stays.xlsx"

REQUIRED_COLS = [
    "Location", "Name", "Bedroom", "Bed", "Max Guests",
    "Washing Machine", "Iron", "Pool", "Beach View",
    "Distance Category", "Rating", "Reviews",
    "Fee/night (IDR)", "Photo URL", "Remarks", "Link", "Maps",
]

DISTANCE_ORDER = ["Beachfront", "<500m", "<1km", ">1km"]

# Numeric km value for each category — used for sorting and range filter
DISTANCE_KM = {
    "Beachfront": 0.05,
    "<500m":      0.35,
    "<1km":       0.75,
    ">1km":       2.0,
}


def normalize_distance(val) -> str:
    """
    Normalize any distance string into one of the 4 standard categories.
    Handles: Beachfront, <500m, <1km, >1km (standard)
    Also handles raw km values like: 5.5km, 3,9km, 21km, 3.6km, 1.4km, etc.
    """
    if pd.isna(val):
        return ">1km"
    s = str(val).strip().lower().replace(",", ".")

    # Already standard
    if s == "beachfront":
        return "Beachfront"
    if s in ("<500m", "< 500m", "500m"):
        return "<500m"
    if s in ("<1km", "< 1km", "1km"):
        return "<1km"
    if s in (">1km", "> 1km"):
        return ">1km"

    # Try to parse raw numeric km value like "5.5km", "3.9km", "21km"
    import re
    m = re.match(r"([\d.]+)\s*km", s)
    if m:
        km = float(m.group(1))
        if km <= 0.1:
            return "Beachfront"
        if km < 0.5:
            return "<500m"
        if km < 1.0:
            return "<1km"
        return ">1km"

    # Try plain meters: "350m", "800m"
    m = re.match(r"([\d.]+)\s*m$", s)
    if m:
        meters = float(m.group(1))
        if meters <= 100:
            return "Beachfront"
        if meters < 500:
            return "<500m"
        if meters < 1000:
            return "<1km"
        return ">1km"

    return ">1km"  # fallback


def normalize_yn(val) -> str:
    """Normalize yes/no variants to 'Yes' or 'No'."""
    if pd.isna(val):
        return "No"
    s = str(val).strip().lower()
    if s.startswith("yes"):
        return "Yes"
    if s.startswith("no"):
        return "No"
    return str(val).strip()


@st.cache_data(ttl=30)
def load_stays() -> pd.DataFrame:
    """Load stays from Excel, normalize columns, return DataFrame."""
    if not EXCEL_FILE.exists():
        return pd.DataFrame(columns=REQUIRED_COLS)

    df = pd.read_excel(EXCEL_FILE, sheet_name="Stays", engine="openpyxl", header=1)

    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Add missing columns as empty
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = None

    # Normalize yes/no columns
    for col in ["Washing Machine", "Iron", "Pool", "Beach View"]:
        df[col] = df[col].apply(normalize_yn)

    # Numeric coercion
    df["Bedroom"] = pd.to_numeric(df["Bedroom"], errors="coerce").fillna(0).astype(int)
    df["Bed"] = pd.to_numeric(df["Bed"], errors="coerce").fillna(0).astype(int)
    df["Max Guests"] = pd.to_numeric(df["Max Guests"], errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0).astype(int)
    df["Fee/night (IDR)"] = pd.to_numeric(df["Fee/night (IDR)"], errors="coerce").fillna(0).astype(int)

    # Clean strings
    df["Location"] = df["Location"].fillna("").str.strip()
    df["Name"] = df["Name"].fillna("Unnamed Property").str.strip()
    df["Remarks"] = df["Remarks"].fillna("")
    df["Link"] = df["Link"].fillna("")
    df["Maps"] = df["Maps"].fillna("")
    df["Photo URL"] = df["Photo URL"].fillna("")

    # Normalize Distance Category — handles any format including raw km values
    df["Distance Category"] = df["Distance Category"].apply(normalize_distance)

    # Add numeric km value for sorting/filtering
    df["distance_km"] = df["Distance Category"].map(DISTANCE_KM).fillna(2.0)

    # Drop fully empty rows
    df = df[df["Name"] != ""].reset_index(drop=True)

    return df


def get_filter_options(df: pd.DataFrame) -> dict:
    """Extract unique values for filter widgets."""
    return {
        "locations": sorted(df["Location"].unique().tolist()),
        "bedrooms": sorted(df["Bedroom"].unique().tolist()),
        "distance_cats": [d for d in DISTANCE_ORDER if d in df["Distance Category"].unique()],
        "price_min": int(df["Fee/night (IDR)"].min()) if len(df) else 0,
        "price_max": int(df["Fee/night (IDR)"].max()) if len(df) else 5000000,
        "rating_min": float(df["Rating"].min()) if df["Rating"].notna().any() else 4.0,
        "dist_km_max": float(df["distance_km"].max()) if len(df) else 2.0,
    }
