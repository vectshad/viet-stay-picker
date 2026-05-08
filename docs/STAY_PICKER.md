# stay_picker_v2 — Documentation

## File structure

```
stay_picker_v2/
├── app.py           — Main app: sidebar filters, 3 tabs (Card, Compare, Map)
├── data_loader.py   — Reads stays.xlsx, normalizes all columns, extracts filter options
├── map_builder.py   — Builds Folium map with stay markers + optional itinerary overlay
├── stays.xlsx       — Source data — edit this to add/remove properties
├── requirements.txt
└── README.md
```

## How data flows

```
stays.xlsx → data_loader.py → app.py (filters) → card view / compare / map
                                                 → map_builder.py (Folium map)
```

The only file you need to edit to add/remove properties is `stays.xlsx`.
The sheet must be named exactly **`Stays`**.

---

## stays.xlsx column reference

| Column | Type | Example | Notes |
|---|---|---|---|
| `Location` | Text | `Da Nang` or `HCM` | Used for location filter chip |
| `Name` | Text | `MercuryBeach 2BRs-POOL` | Display name on card |
| `Bedroom` | Number | `2` | |
| `Bed` | Number | `3` | |
| `Max Guests` | Number | `5` | Filter: min capacity |
| `Washing Machine` | Text | `Yes` / `Yes (shared/outside room)` / `No` | |
| `Iron` | Text | `Yes` / `No` | |
| `Pool` | Text | `Yes` / `No` | |
| `Beach View` | Text | `Yes` / `No` | |
| `Distance Category` | Text | `Beachfront` / `<500m` / `<1km` / `>1km` | Auto-normalized — see below |
| `Rating` | Decimal | `4.86` | Airbnb star rating |
| `Reviews` | Number | `133` | Review count |
| `Fee/night (IDR)` | Number | `1226074` | Plain number, no dots or formatting |
| `Photo URL` | URL | `https://a0.muscache.com/...` | Right-click Airbnb photo → Copy image address |
| `Remarks` | Text | `Beach view, great sunrise` | Optional, shown on card |
| `Link` | URL | `https://www.airbnb.com/rooms/...` | Full Airbnb listing URL |
| `Maps` | URL | `https://www.google.com/maps/@16.06,...` | Must contain `@lat,lon` — see below |
| `Price Date Checked` | Date | `2026-05-08` | Optional — shown as "checked on" label |

---

## Distance Category — auto-normalization

`data_loader.py` normalizes any format automatically. All of these work:

| What you type | Normalized to | Meaning |
|---|---|---|
| `Beachfront` | `Beachfront` | On the beach (~0–100m) |
| `<500m` or `500m` | `<500m` | Under 5 min walk |
| `<1km` or `1km` | `<1km` | ~10 min walk or 2 min Grab |
| `>1km` | `>1km` | Need Grab |
| `1.4km` or `1.4 km` | `>1km` | Raw km — auto-bucketed |
| `3,9km` | `>1km` | Comma decimal — handled |
| `350m` | `<500m` | Plain meters — handled |
| `21km` | `>1km` | Large value — always `>1km` |

**Reference points:**
- Da Nang → My Khe Beach
- HCM → Ben Thanh Market

---

## How to get the correct Maps URL

Shortened `goo.gl` links do NOT work for map pins — the app can't extract coordinates from them.

**Correct method:**
1. Search the property on Google Maps
2. Right-click the exact location pin
3. Click the coordinates that appear (e.g. `16.0612, 108.2479`)
4. Copy the full URL from your browser — it should contain `@16.0612,108.2479`

```
❌ Wrong:  https://maps.app.goo.gl/67JCoxr83RLmuibC6
✅ Right:  https://www.google.com/maps/@16.0612,108.2479,17z
```

---

## How to get the Photo URL

1. Open the Airbnb listing
2. Right-click the main cover photo
3. Click **Copy image address** (Chrome) or **Copy image link** (Safari)

The URL will look like: `https://a0.muscache.com/im/pictures/miso/Hosting-.../original/....jpeg`

---

## Sidebar filters

| Filter | Widget | How it works |
|---|---|---|
| Location | Radio chips | All / Da Nang / HCM |
| Price / night | Slider | Min–max from data |
| Min bedrooms | Radio chips | Any / 2 / 3 |
| Min rating | Slider | 4.0–5.0 |
| Max distance | Select slider | Beachfront → <500m → <1km → >1km (any) |
| Beach view | Toggle | Yes only |
| Pool | Toggle | Yes only |
| Washing machine | Toggle | Yes only |
| Iron | Toggle | Yes only |
| Min guests | Number input | Default 5 |
| Sort by | Dropdown | Price low/high, Rating, Reviews, Distance |

---

## Three tabs

### Card view
- Each property as a card: photo, location badge, distance badge, price/night, rating, amenity pills
- Click **+ Compare** to add to comparison list (up to 3)
- **Airbnb** and **Maps** buttons open directly

### Compare view
- Requires ≥ 2 properties selected from Card view
- Photos side-by-side, then full comparison table
- Green ✓ = yes, Red ✗ = no

### Map view
- All filtered properties as Folium markers
- Blue = Da Nang, Green = HCM, Red = in compare list
- Click any marker for details + Airbnb link
- Toggle to overlay itinerary stops (see wiring instructions in `NEXT_FEATURES.md`)

---

## Reload data

Click **🔄 Reload data from Excel** in the sidebar after editing `stays.xlsx` — no app restart needed. Cache TTL is 30 seconds.

---

## Known issues

| Issue | Notes |
|---|---|
| Map pins missing for `goo.gl` URLs | By design — use full coordinate URL |
| Photo not loading | URL must be direct image link (`.jpg`, `.webp`), not the Airbnb listing page URL |
| Price filter not working | `Fee/night (IDR)` must be a plain number like `900000`, not `900.000` or `900k` |
| Yes/No filters not working | Use `Yes`, `Yes (shared/outside room)`, or `No` — not `ada` / `tidak ada` |
| Itinerary overlay not wired yet | See `NEXT_FEATURES.md` for how to enable it |
