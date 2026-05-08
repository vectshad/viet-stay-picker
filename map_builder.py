"""
map_builder.py — Build Folium map of stays + optional itinerary stops
"""

import folium
from folium import plugins
import pandas as pd

LOCATION_COLORS = {
    "Da Nang": "#378ADD",
    "HCM": "#1D9E75",
}
DEFAULT_COLOR = "#888780"

ITINERARY_COLOR = "#E8593C"


def build_stays_map(
    df: pd.DataFrame,
    selected_names: list[str] = None,
    itinerary_stops: list[dict] = None,
) -> folium.Map:
    """
    Build a Folium map with stay markers + optional itinerary stops.

    df: stays DataFrame (must have Maps col with Google Maps URLs or lat/lon)
    selected_names: list of property names to highlight
    itinerary_stops: list of dicts with keys: name, lat, lon, day (optional)
    """
    # Try to extract coordinates from Maps URLs
    df = df.copy()
    df["lat"] = None
    df["lon"] = None

    for idx, row in df.iterrows():
        lat, lon = _extract_coords(str(row.get("Maps", "")))
        df.at[idx, "lat"] = lat
        df.at[idx, "lon"] = lon

    # Build all points to compute center
    all_lats, all_lons = [], []
    valid = df[df["lat"].notna() & df["lon"].notna()]
    all_lats += valid["lat"].tolist()
    all_lons += valid["lon"].tolist()

    if itinerary_stops:
        all_lats += [s["lat"] for s in itinerary_stops if s.get("lat")]
        all_lons += [s["lon"] for s in itinerary_stops if s.get("lon")]

    multi_city = all_lats and (max(all_lats) - min(all_lats)) > 2

    if multi_city:
        center = [13.5, 108.0]  # Central Vietnam — shows both Da Nang and HCM
        zoom = 7
    elif all_lats:
        center = [sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)]
        zoom = 13
    else:
        center = [16.05, 108.20]  # Default Da Nang
        zoom = 13

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron",
        attr="© OpenStreetMap © CartoDB",
    )
    plugins.Fullscreen().add_to(m)

    # --- Stays layer ---
    stays_group = folium.FeatureGroup(name="🏠 Stays")
    for _, row in df.iterrows():
        if pd.isna(row["lat"]) or pd.isna(row["lon"]):
            continue

        is_selected = selected_names and row["Name"] in selected_names
        loc_color = LOCATION_COLORS.get(row["Location"], DEFAULT_COLOR)

        price_str = f"Rp {int(row['Fee/night (IDR)']):,}/night" if row["Fee/night (IDR)"] else "—"
        rating_str = f"★ {row['Rating']}" if pd.notna(row["Rating"]) else "—"

        popup_html = f"""
        <div style="font-family:'Segoe UI',sans-serif;min-width:200px;max-width:260px">
            <div style="background:{loc_color};color:white;padding:8px 10px;
                        border-radius:6px 6px 0 0;font-weight:600;font-size:13px">
                {row['Name']}
            </div>
            <div style="padding:8px 10px;border:1px solid #eee;border-radius:0 0 6px 6px;font-size:12px">
                <b>{price_str}</b> &nbsp;·&nbsp; {rating_str}<br>
                <span style="color:#888">{row['Bedroom']}BR · {row['Bed']} beds · max {row['Max Guests']} guests</span><br>
                <span style="color:#888">{row['Distance Category']} from center</span>
                {'<br><a href="' + row["Link"] + '" target="_blank" style="color:' + loc_color + '">View on Airbnb →</a>' if row["Link"] else ''}
            </div>
        </div>
        """

        icon_color = "blue" if row["Location"] == "Da Nang" else "green"
        if is_selected:
            icon_color = "red"

        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"🏠 {row['Name']} — {price_str}",
            icon=folium.Icon(
                color=icon_color,
                icon="home",
                prefix="fa",
            ),
        ).add_to(stays_group)

    stays_group.add_to(m)

    # --- Itinerary stops layer (optional) ---
    if itinerary_stops:
        itin_group = folium.FeatureGroup(name="📍 Itinerary stops")
        for stop in itinerary_stops:
            if not stop.get("lat") or not stop.get("lon"):
                continue
            folium.CircleMarker(
                location=[stop["lat"], stop["lon"]],
                radius=6,
                color=ITINERARY_COLOR,
                fill=True,
                fill_color=ITINERARY_COLOR,
                fill_opacity=0.7,
                tooltip=f"📍 {stop.get('name', '')} ({stop.get('day', '')})",
            ).add_to(itin_group)
        itin_group.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def _extract_coords(maps_url: str):
    """
    Try to extract lat/lon from a Google Maps URL.
    Handles formats like:
      https://maps.app.goo.gl/... (shortened — can't extract directly)
      https://www.google.com/maps?q=16.0544,108.2022
      https://maps.google.com/@16.0544,108.2022,15z
    Returns (lat, lon) or (None, None).
    """
    import re
    if not maps_url or maps_url == "nan":
        return None, None

    # Pattern: @lat,lon or q=lat,lon or /search/lat,+lon
    patterns = [
        r"@(-?\d+\.\d+),(-?\d+\.\d+)",
        r"q=(-?\d+\.\d+),(-?\d+\.\d+)",
        r"ll=(-?\d+\.\d+),(-?\d+\.\d+)",
        r"search/(-?\d+\.\d+),\+?(-?\d+\.\d+)",
    ]
    for p in patterns:
        m = re.search(p, maps_url)
        if m:
            return float(m.group(1)), float(m.group(2))
    return None, None
