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

    # Reference points defined early so they feed into center/zoom calculation
    REF_POINTS = [
        {"name": "My Khe Beach",         "lat": 16.062, "lon": 108.247, "icon": "umbrella-beach", "color": "green"},
        {"name": "Ben Thanh Market",     "lat": 10.773, "lon": 106.698, "icon": "shopping-bag",   "color": "blue"},
        {"name": "Ba Na Hills",          "lat": 15.995, "lon": 107.996, "icon": "mountain",       "color": "orange"},
        {"name": "Hoi An Old Town",      "lat": 15.877, "lon": 108.329, "icon": "landmark",       "color": "purple"},
        {"name": "Da Nang Airport",      "lat": 16.057, "lon": 108.203, "icon": "plane",          "color": "cadetblue"},
        {"name": "Tan Son Nhat Airport", "lat": 10.817, "lon": 106.657, "icon": "plane",          "color": "cadetblue"},
    ]

    # Build all points to compute center — include ref points so multi-city is
    # always detected even when the filtered stays are all in one city.
    all_lats, all_lons = [], []
    valid = df[df["lat"].notna() & df["lon"].notna()]
    all_lats += valid["lat"].tolist()
    all_lons += valid["lon"].tolist()
    all_lats += [r["lat"] for r in REF_POINTS]
    all_lons += [r["lon"] for r in REF_POINTS]

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

    # --- Reference points (always shown) ---
    ref_group = folium.FeatureGroup(name="📌 Reference points")
    for ref in REF_POINTS:
        folium.Marker(
            location=[ref["lat"], ref["lon"]],
            tooltip=f"📌 {ref['name']}",
            popup=folium.Popup(
                f'<div style="font-family:sans-serif;font-size:13px;font-weight:600">'
                f'📌 {ref["name"]}</div>',
                max_width=180,
            ),
            icon=folium.Icon(color=ref["color"], icon=ref["icon"], prefix="fa"),
        ).add_to(ref_group)
    ref_group.add_to(m)

    # --- HCM Districts layer ---
    HCM_DISTRICTS = [
        {"name": "D1",         "lat": 10.775, "lon": 106.700, "visited": True},
        {"name": "D2",         "lat": 10.793, "lon": 106.737, "visited": True},
        {"name": "D3",         "lat": 10.779, "lon": 106.688, "visited": True},
        {"name": "D4",         "lat": 10.759, "lon": 106.702, "visited": False},
        {"name": "D5",         "lat": 10.755, "lon": 106.662, "visited": True},
        {"name": "D6",         "lat": 10.748, "lon": 106.637, "visited": False},
        {"name": "D7",         "lat": 10.733, "lon": 106.718, "visited": False},
        {"name": "D8",         "lat": 10.742, "lon": 106.662, "visited": False},
        {"name": "D9",         "lat": 10.842, "lon": 106.777, "visited": True},
        {"name": "D10",        "lat": 10.774, "lon": 106.666, "visited": False},
        {"name": "D11",        "lat": 10.763, "lon": 106.650, "visited": False},
        {"name": "D12",        "lat": 10.859, "lon": 106.648, "visited": False},
        {"name": "Bình Thạnh", "lat": 10.812, "lon": 106.714, "visited": False},
        {"name": "Gò Vấp",    "lat": 10.838, "lon": 106.670, "visited": False},
        {"name": "Phú Nhuận", "lat": 10.800, "lon": 106.680, "visited": False},
        {"name": "Tân Bình",  "lat": 10.800, "lon": 106.653, "visited": False},
        {"name": "Tân Phú",   "lat": 10.793, "lon": 106.627, "visited": False},
        {"name": "Bình Tân",  "lat": 10.763, "lon": 106.615, "visited": False},
        {"name": "Thủ Đức",  "lat": 10.855, "lon": 106.763, "visited": False},
    ]
    dist_group = folium.FeatureGroup(name="🏙 HCM Districts")
    for d in HCM_DISTRICTS:
        bg = "#E8593C" if d["visited"] else "#888780"
        label = (
            f'<div style="background:{bg};color:white;font-size:10px;font-weight:700;'
            f'padding:2px 5px;border-radius:3px;white-space:nowrap;'
            f'box-shadow:0 1px 3px rgba(0,0,0,.35)">{d["name"]}</div>'
        )
        folium.Marker(
            location=[d["lat"], d["lon"]],
            tooltip=f'🏙 {d["name"]}{"  ★ itinerary" if d["visited"] else ""}',
            icon=folium.DivIcon(html=label, icon_size=(60, 20), icon_anchor=(30, 10)),
        ).add_to(dist_group)
    dist_group.add_to(m)

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
