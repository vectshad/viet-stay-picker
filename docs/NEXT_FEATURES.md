# Next Features & Claude Code Prompts

Copy any prompt directly into Claude Code. Each one includes enough context to work standalone.

---

## stay_picker_v2

### 1. Wire itinerary overlay on the map

**What it does:** Shows your trip_planner itinerary stops as orange dots on the stay picker map,
so you can see how far each Airbnb is from your actual activities.

**Claude Code prompt:**
```
In stay_picker_v2/app.py, wire the itinerary overlay for the map tab.

Create a new file stay_picker_v2/itinerary_stops.py with this content:
STOPS = [
    {"name": "Da Nang Airport",         "lat": 16.057,  "lon": 108.203, "day": "Rabu"},
    {"name": "Coconut Village Hoi An",  "lat": 15.870,  "lon": 108.375, "day": "Rabu"},
    {"name": "Hoi An Old Town",         "lat": 15.877,  "lon": 108.329, "day": "Rabu"},
    {"name": "Ba Na Hills",             "lat": 15.995,  "lon": 107.996, "day": "Kamis"},
    {"name": "My Khe Beach",            "lat": 16.062,  "lon": 108.247, "day": "Jumat"},
    {"name": "Ben Thanh Market",        "lat": 10.773,  "lon": 106.698, "day": "Sabtu"},
    {"name": "War Remnants Museum",     "lat": 10.780,  "lon": 106.692, "day": "Sabtu"},
    {"name": "Thien Hau Pagoda",        "lat": 10.753,  "lon": 106.661, "day": "Minggu"},
    {"name": "Nguyen Hue Walking St",   "lat": 10.774,  "lon": 106.704, "day": "Minggu"},
    {"name": "Tan Son Nhat Airport",    "lat": 10.817,  "lon": 106.657, "day": "Senin"},
]

Then in app.py map tab, replace `itin_stops = None` with:
from itinerary_stops import STOPS
itin_stops = STOPS if show_itin else None
```

---

### 2. Add cost calculator per property

**What it does:** Lets you enter number of nights per city and shows total cost split 5 ways.

**Claude Code prompt:**
```
In stay_picker_v2/app.py, add a cost calculator to each property card.

Below the price line in the card view, add a small number input (1–10 nights, default 3 for Da Nang
and 3 for HCM). Show:
- Total cost = Fee/night × nights
- Per person = total ÷ 5
Format as "3 nights → Rp 3.678.222 total · Rp 735.644/person"

Use st.number_input with key=f"nights_{idx}" so each card has its own value.
Style it as small muted text below the price, not a prominent element.
```

---

### 3. Export compare table as image

**What it does:** Download button on compare tab that saves the comparison as a PNG for sharing on WhatsApp.

**Claude Code prompt:**
```
In stay_picker_v2/app.py compare tab, add a "Download comparison as image" button.

Use the `imgkit` or `playwright` library to render the comparison table HTML to PNG.
If those are unavailable, use pandas DataFrame.to_html() + pdfkit as fallback.
The image should include: property names, photos, all comparison rows.
Show a st.download_button with the PNG bytes.
```

---

### 4. Google Sheets as live data source

**What it does:** Replaces stays.xlsx with a Google Sheet so all 5 friends can edit it in real time.

**Claude Code prompt:**
```
In stay_picker_v2/data_loader.py, add an option to load data from a public Google Sheet
instead of stays.xlsx.

Add a constant at the top:
GOOGLE_SHEET_URL = ""  # paste published CSV URL here if using Sheets

If GOOGLE_SHEET_URL is set, use pd.read_csv(GOOGLE_SHEET_URL) instead of read_excel().
The sheet must have the same column names as stays.xlsx.

To get the URL: File → Share → Publish to web → CSV format → copy link.
Keep the xlsx fallback working when GOOGLE_SHEET_URL is empty.
```

---

### 5. Price date indicator on cards

**What it does:** Shows "checked on 8 May" under each price so you know if the price is stale.

**Claude Code prompt:**
```
In stay_picker_v2/, add support for a "Price Date Checked" column in stays.xlsx.

1. In data_loader.py: read the column, parse as date, fill empty with None.
2. In app.py card view: below the price line, if Price Date Checked is set, show
   a small muted line: "checked 8 May 2026"
   If more than 14 days old, show it in amber with a ⚠ prefix.
```

---

## trip_planner

### 6. Save/load itinerary to JSON

**What it does:** Persists the itinerary so it survives page refresh and can be shared.

**Claude Code prompt:**
```
In trip_planner/app.py, add save/load functionality for the itinerary.

On startup: if itinerary.json exists in the project folder, load it into st.session_state.days
instead of the hardcoded default.

In the sidebar: add a "💾 Save itinerary" button that writes st.session_state.days
to itinerary.json using json.dump.

Also add an "📂 Load from file" file uploader that accepts a .json file and loads it
into st.session_state.days with validation (must be a list of dicts with "day" and "stops" keys).
```

---

### 7. Weather overlay on timeline

**What it does:** Shows weather forecast next to each day on the timeline tab.

**Claude Code prompt:**
```
In trip_planner/app.py timeline tab, add weather forecast for each day.

Use the free Open-Meteo API (no key needed):
- Da Nang coords: lat=16.0544, lon=108.2022
- HCM coords: lat=10.8231, lon=106.6297
- URL: https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&start_date={date}&end_date={date}&timezone=Asia/Bangkok

For each day in the timeline, fetch the forecast for that date and show:
"⛅ 32°C / 27°C · 60% rain" in small muted text next to the day header.

Cache results with @st.cache_data(ttl=3600) to avoid hitting the API on every render.
```

---

### 8. Budget tracker tab

**What it does:** Pulls from Budgeting_Viet_2026.xlsx and shows spending vs budget per category.

**Claude Code prompt:**
```
In trip_planner/app.py, add a new "💰 Budget" tab (6th tab).

Read Budgeting_Viet_2026.xlsx from the project folder using pd.read_excel().
Show:
1. Total budget vs estimated spend (progress bar)
2. Breakdown by category (flights, accommodation, food, activities, transport)
   as a bar chart using st.bar_chart
3. Per-person split for 5 people

If the file is not found, show a placeholder with instructions to place the xlsx in the folder.
```

---

### 9. Link hotel stays to map

**What it does:** Shows the selected Airbnb from stay_picker as a home-base pin on the trip_planner map.

**Claude Code prompt:**
```
In trip_planner/map_builder.py and app.py, add support for showing the selected hotel/Airbnb
as a special marker on the itinerary map.

Add an optional parameter to build_map(): selected_stays (list of dicts with name, lat, lon, location).

In app.py, add a small section above the map in the Map View tab:
"🏠 Add your stay" — two text inputs for Da Nang stay name + Maps URL and HCM stay name + Maps URL.
Extract coordinates from the Maps URL using the existing _extract_coords() from stay_picker map_builder.
Pass them to build_map() and plot as a house icon (home) in a distinct white/black color.
```

---

## Notes for Claude Code

- Always read the relevant `.md` file in `docs/` before making changes
- The two apps are independent — changes to one don't affect the other
- `stays.xlsx` sheet must always be named `Stays` — this is validated in `data_loader.py`
- Nominatim (place search) has a 1 req/sec rate limit — don't remove the `time.sleep(1)`
- All map tiles use CartoDB Positron (free, no key) — don't switch to Google Maps tiles
