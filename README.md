# 🏠 Stay Picker — Vietnam Trip 2026

Interactive Airbnb/hotel picker built with Streamlit.  
Filter, compare side-by-side, and map your stay options — all sourced from a local Excel file.

---

## Features

| Feature | Description |
|---|---|
| 🃏 Card view | Photo, price, rating, amenity pills for each property |
| ⚖️ Compare | Side-by-side comparison table for up to 3 selected properties |
| 🗺️ Map view | Folium map with all stays plotted — click markers for details |
| 🔍 Filters | Location, price, bedrooms, rating, distance, amenities, guest capacity |
| 🔄 Live reload | Click "Reload data" to pick up changes you made to stays.xlsx instantly |

---

## Setup

### 1. Install dependencies

```bash
cd stay_picker
pip install -r requirements.txt --user
```

Or with a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Add your Excel file

Place your `stays.xlsx` file in the `stay_picker/` folder.  
The app reads the sheet named **`Stays`**.

### 3. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Excel File Format

Your `stays.xlsx` must have a sheet named `Stays` with these columns **in any order**:

| Column | Type | Example | Notes |
|---|---|---|---|
| `Location` | Text | `Da Nang` or `HCM` | Used for location filter |
| `Name` | Text | `MercuryBeach w/ Ocean View` | Property display name |
| `Bedroom` | Number | `2` | Number of bedrooms |
| `Bed` | Number | `3` | Number of beds |
| `Max Guests` | Number | `5` | Max guests allowed |
| `Washing Machine` | Text | `Yes` / `Yes (shared/outside room)` / `No` | |
| `Iron` | Text | `Yes` / `No` | |
| `Pool` | Text | `Yes` / `No` | |
| `Beach View` | Text | `Yes` / `No` | |
| `Distance Category` | Text | See below | Proximity to city center/beach |
| `Rating` | Decimal | `4.8` | Airbnb star rating |
| `Reviews` | Number | `124` | Number of reviews |
| `Fee/night (IDR)` | Number | `900000` | Price per night, no dots |
| `Photo URL` | URL | `https://a0.muscache.com/...` | Right-click Airbnb photo → Copy image address |
| `Remarks` | Text | `Beach view, great for sunrise` | Optional notes |
| `Link` | URL | `https://www.airbnb.com/rooms/...` | Full Airbnb listing URL |
| `Maps` | URL | `https://www.google.com/maps?q=16.05,108.20` | Google Maps URL with coordinates |

### Distance Category values

| Value | Meaning |
|---|---|
| `Beachfront` | Property is directly on the beach |
| `<500m` | Under 5 min walk to beach or city center |
| `<1km` | Short 10 min walk or 2 min Grab ride |
| `>1km` | Need Grab, not walkable |

For **Da Nang** properties, distance is from My Khe Beach.  
For **HCM** properties, distance is from Ben Thanh / District 1 center.

### How to get the Photo URL

1. Open the Airbnb listing
2. Right-click on the main cover photo
3. Click **"Copy image address"** (Chrome) or **"Copy image link"** (Safari)
4. Paste into the `Photo URL` column

The URL will look like: `https://a0.muscache.com/im/pictures/miso/...`

### How to get the Maps URL with coordinates

For the map to correctly plot the property marker, use a **full Google Maps URL** that contains coordinates, not a shortened `goo.gl` link.

**Best method:**
1. Search for the property on Google Maps
2. Right-click the exact location pin
3. Click the coordinates that appear (e.g. `16.0612, 108.2479`)
4. The full URL in your browser now contains `@16.0612,108.2479` — copy that URL

**Why shortened URLs don't work:**  
`https://maps.app.goo.gl/...` links require a redirect to resolve, and the app can't follow redirects to extract coordinates. Full URLs like `https://www.google.com/maps/@16.0612,108.2479,17z` work perfectly.

---

## How to Use

### Card view
- Browse all filtered properties as cards
- Each card shows: photo, location badge, distance badge, price/night, rating, amenity pills
- Click **+ Compare** to add a property to your comparison list (up to 3)
- Click **Airbnb** or **Maps** to open the listing or location directly

### Compare view
- Requires at least 2 properties selected from Card view
- Shows photos side-by-side, then a full comparison table
- Green ✓ = yes, Red ✗ = no for yes/no fields

### Map view
- All filtered properties plotted as markers
- Blue = Da Nang, Green = HCM, Red = currently in compare list
- Click any marker for property details and Airbnb link
- Toggle "Show itinerary stops" to overlay your trip_planner itinerary (see below)

### Reload data
- When you update `stays.xlsx`, click **🔄 Reload data from Excel** in the sidebar
- No need to restart the app

---

## Connecting with Trip Planner

The map view can overlay your itinerary stops from the `trip_planner` app.

To enable this, define your stops in a file called `itinerary_stops.py` in the `stay_picker/` folder:

```python
# itinerary_stops.py — paste your key stops here
STOPS = [
    {"name": "Ba Na Hills", "lat": 15.995, "lon": 107.996, "day": "Kamis"},
    {"name": "My Khe Beach", "lat": 16.062, "lon": 108.247, "day": "Jumat pagi"},
    {"name": "Ben Thanh Market", "lat": 10.773, "lon": 106.698, "day": "Sabtu"},
    {"name": "Thien Hau Pagoda", "lat": 10.753, "lon": 106.661, "day": "Minggu"},
]
```

Then in `app.py`, replace the `itin_stops = None` line with:

```python
from itinerary_stops import STOPS
itin_stops = STOPS
```

---

## File Structure

```
stay_picker/
├── app.py              # Main Streamlit app
├── data_loader.py      # Excel reader + filter options
├── map_builder.py      # Folium map construction
├── requirements.txt    # Python dependencies
├── stays.xlsx          # Your data file (you create/update this)
├── itinerary_stops.py  # Optional: itinerary overlay (you create this)
└── README.md           # This file
```

---

## Deploy to Streamlit Cloud (free)

1. Push the `stay_picker/` folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Add `stays.xlsx` to the repo (or use Google Sheets as source — ask Claude to help convert)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "No data found" | Make sure `stays.xlsx` is in the same folder as `app.py`, and the sheet is named exactly `Stays` |
| Properties not showing on map | Use full Google Maps URL with coordinates, not shortened `goo.gl` links |
| Photo not loading | Make sure Photo URL is a direct image URL (ends in `.jpg` or `.webp`), not the Airbnb listing page URL |
| Price filter not working | Make sure `Fee/night (IDR)` column contains plain numbers like `900000`, not formatted text like `900.000` |
| Yes/No filters not working | Make sure amenity columns use `Yes`, `Yes (shared/outside room)`, or `No` — not `ada` / `tidak ada` |
