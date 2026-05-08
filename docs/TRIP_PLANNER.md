# trip_planner — Documentation

## File structure

```
trip_planner/
├── app.py            — Main app: 5 tabs (Map, Timeline, Logic Check, Edit, Place Search)
├── places.py         — Free place search via Nominatim (OpenStreetMap) — no API key
├── map_builder.py    — Folium map: day-by-day routing, colored markers, route lines
├── logic_checker.py  — Timing overlap & geographic distance analysis
├── requirements.txt
└── README.md
```

---

## Itinerary data structure

All itinerary data lives in `st.session_state.days` — loaded at app startup from the hardcoded
default in `app.py`. It is **not persisted to a file** — lives in memory during the session only.

Each day object:

```python
st.session_state.days = [
    {
        "day": "Rabu, 29 Jul — Hoi An",   # Label shown in UI and map legend
        "stops": [
            {
                "name":     "Da Nang Airport",  # Display name
                "start":    "10:50",             # HH:MM 24h format
                "end":      "12:00",             # HH:MM 24h format
                "notes":    "Landing + imigrasi",
                "category": "airport",           # See valid categories below
                "lat":      16.057,              # Decimal degrees
                "lon":      108.203,
            },
        ]
    },
]
```

---

## Valid stop categories

| Category | Folium icon | Use for |
|---|---|---|
| `attraction` | star | Temples, landmarks, viewpoints, bridges |
| `food` | cutlery | Restaurants, cafés, street food stalls |
| `market` | shopping-cart | Traditional markets, supermarkets |
| `museum` | university | Museums, galleries, heritage sites |
| `beach` | tint | Beach stops, coastal walks |
| `airport` | plane | Airports, flight connection stops |
| `nightlife` | music | Night markets, Bui Vien, bars |
| `hotel` | home | Check-in / check-out stops |
| `transport` | car | Travel legs, Grab rides, bus stops |

---

## Map view

- Colored by day — each day gets its own color from `DAY_COLORS` in `map_builder.py`
- Dashed route line connects stops within the same day
- Numbered circle markers (1, 2, 3...) per day
- Click any marker for popup: stop name, time, category, notes, day label
- Layer control lets you toggle individual days on/off

---

## Logic checker

`logic_checker.py` runs against the full `st.session_state.days` on the Logic Check tab.

| Check | Severity | Trigger |
|---|---|---|
| Missing start time | Info | `stop["start"]` is empty |
| End before start | Error | `end < start` |
| Duration < 15 min | Warning | `(end - start) < 15 minutes` |
| Overlap with next stop | Error | `next_start - end < -5 minutes` |
| Insufficient travel time | Warning | Estimated drive time > gap + 10 min |

Drive time estimate: Haversine distance between consecutive stops ÷ 30 km/h assumed city speed.

---

## Place search (Nominatim)

`places.py` calls the free Nominatim API (OpenStreetMap). No API key required.

- Rate limit: **1 request per second** — enforced by `time.sleep(1)` in `batch_search()`
- Country code defaults to `"vn"` for Vietnam — change the `country_codes` parameter for other countries
- Returns: `name`, `display_name`, `lat`, `lon`, `type`
- For places not found: returns `{"lat": None, "lon": None}` — the app shows a "not found" warning

---

## Five tabs

### Map view
Filter by day or show all. Click a marker for stop details. Folium map with CartoDB Positron tiles.

### Timeline
Color-coded day-by-day schedule. Each stop shows time range, activity name, coordinates, and notes.

### Logic Check
Runs all checks and shows errors (🔴), warnings (🟡), and info (🔵) with day label and message.
Download issues as CSV from this tab.

### Edit Itinerary
Select a day, expand any stop to edit all fields inline.
"Auto-search coordinates" button calls Nominatim for a stop by name.
"Add New Stop" form at the bottom — auto-searches coordinates on submit.

### Place Search
Standalone search: enter a place name, see it on a mini-map, and add it to any day with one click.

---

## Day colors (map_builder.py)

```python
DAY_COLORS = ["#E8593C", "#1D9E75", "#378ADD", "#7F77DD", "#EF9F27", "#D85A30", "#0F6E56"]
```

Day 1 = coral, Day 2 = teal, Day 3 = blue, Day 4 = purple, Day 5 = amber, etc.
Folium icon colors map as: red, green, blue, purple, orange, darkred, darkgreen.

---

## Known issues

| Issue | Notes |
|---|---|
| Itinerary resets on page refresh | `st.session_state` only — no file persistence yet |
| Nominatim slow for batch search | 1 req/sec rate limit — 10 places takes ~10 seconds |
| Some Vietnam places not found | Try adding city name: `"Ba Na Hills Da Nang"` not just `"Ba Na Hills"` |
| Logic checker time math | Uses `datetime.strptime` — times after midnight (e.g. `00:30`) may calculate incorrectly vs same-day times |
