# Vietnam Trip Planner — Project Overview

Two standalone Streamlit apps built for a Vietnam trip (Da Nang → Ho Chi Minh City, late July–early August 2026) with 5 people.

## Apps

| App | Purpose | Folder |
|---|---|---|
| `trip_planner` | Interactive itinerary — map, logic checker, place search, timeline, edit | `trip_planner/` |
| `stay_picker_v2` | Filter & compare Airbnb options from Excel, with map view | `stay_picker_v2/` |

## Stack

- Python + Streamlit
- Folium + OpenStreetMap (Nominatim) — free, no API key
- openpyxl — reads `stays.xlsx` directly
- No paid APIs anywhere

## Group context

- 5 people (3 men, 2 women)
- Need minimum 2BR, max guests ≥ 5
- Da Nang: 29 Jul – 31 Jul 2026
- Ho Chi Minh: 31 Jul – 3 Aug 2026
- Flight home: Monday 3 Aug, VietJet VJ855 SGN→CGK 09:35

## Quick start (copy-paste into terminal)

```bash
pip install -r requirements.txt --user
streamlit run app.py
```

Or with venv:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
```

## Context block for Claude Code

Paste this at the start of every new Claude Code session:

```
I have two Streamlit apps for a Vietnam trip planner:
1. trip_planner/ — itinerary with map, logic checker, place search (5 tabs)
2. stay_picker_v2/ — Airbnb picker from stays.xlsx with filter/compare/map (3 tabs)
Stack: Python, Streamlit, Folium, OpenStreetMap (Nominatim), openpyxl.
No paid APIs. stays.xlsx is the only data source for stay_picker.
Group: 5 people, Da Nang 29 Jul–31 Jul, HCM 31 Jul–3 Aug 2026.
See docs/ folder for full documentation.
```

## Docs in this folder

| File | Contents |
|---|---|
| `PROJECT_OVERVIEW.md` | This file — start here |
| `STAY_PICKER.md` | stay_picker_v2 data format, filters, known issues |
| `TRIP_PLANNER.md` | Itinerary structure, categories, logic checker |
| `NEXT_FEATURES.md` | Backlog with ready-to-use Claude Code prompts |
| `ITINERARY.md` | Full current itinerary day by day |
| `FLIGHTS_AND_STAYS.md` | Flight status, price estimates, Airbnb shortlist |
