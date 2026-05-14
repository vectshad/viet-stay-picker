"""
app.py — Stay Picker: Vietnam Trip 2026
Filter, compare, and map Airbnb/hotel options from stays.xlsx
"""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from data_loader import load_stays, get_filter_options
from map_builder import build_stays_map
from votes import VOTERS, fetch_votes, upsert_vote, delete_vote

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stay Picker — Vietnam 2026",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

.prop-card {
    background: white;
    border: 1px solid #e8e7e1;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 14px;
    transition: box-shadow 0.15s, transform 0.15s;
    cursor: pointer;
}
.prop-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.12); transform: translateY(-2px); }
.prop-card.selected { border-color: #1a1a18; border-width: 2px; }

.card-img-wrap {
    width: 100%; height: 160px; overflow: hidden;
    background: #f1efe8; display: flex;
    align-items: center; justify-content: center;
    position: relative;
}
.card-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.no-photo { font-size: 12px; color: #aaa; }

.loc-badge {
    position: absolute; top: 8px; left: 8px;
    font-size: 10px; font-weight: 600; padding: 3px 8px;
    border-radius: 20px;
}
.loc-danang { background: #e6f1fb; color: #0c447c; }
.loc-hcm { background: #e1f5ee; color: #085041; }
.loc-other { background: #f1efe8; color: #444441; }

.dist-badge {
    position: absolute; top: 8px; right: 8px;
    font-size: 10px; font-weight: 500; padding: 3px 8px;
    border-radius: 20px; background: rgba(255,255,255,0.92);
    color: #444441; border: 1px solid #e8e7e1;
}

.card-body { padding: 10px 12px 6px; }
.card-name {
    font-size: 16px; font-weight: 600; color: #1a1a18; margin-bottom: 3px;
    height: 2.8em; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}
.card-price { font-size: 20px; font-weight: 600; color: #1a1a18; }
.card-price span { font-size: 14px; color: #888; font-weight: 400; }
.card-rating { font-size: 14px; color: #ba7517; margin-top: 1px; }
.card-meta { font-size: 14px; color: #888; margin-top: 2px; }

.amenity-row { display: flex; flex-wrap: wrap; gap: 4px; margin: 8px 0 6px; }
.amenity {
    font-size: 12px; padding: 2px 8px; border-radius: 6px;
    background: #f1efe8; color: #444441;
}
.amenity.yes { background: #e1f5ee; color: #085041; }
.amenity.no { background: #fcebeb; color: #791f1f; }

.card-actions { padding: 10px 12px 12px; display: flex; flex-direction: column; gap: 6px; border-top: 1px solid #e8e7e1; }
.card-action-row { display: flex; gap: 6px; }
.card-btn {
    flex: 1; text-align: center; padding: 8px 4px;
    border-radius: 8px; border: 1px solid #333;
    color: white; text-decoration: none !important;
    font-size: 13px; font-weight: 500;
    background: #1a1a18; cursor: pointer; display: block;
}
.card-btn:hover { background: #3a3a38; color: white !important; text-decoration: none !important; }
.card-btn-details { font-size: 14px; }
.card-btn-selected { background: #444; border-color: #666; }
.price-date { font-size: 10px; color: #aaa; margin-top: 3px; }

.compare-header {
    background: #f8f7f3; border: 1px solid #e8e7e1;
    border-radius: 10px; padding: 10px 14px;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 14px; font-size: 13px; color: #444;
}
.section-title { font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: #888; margin: 16px 0 8px; }

.no-data-msg {
    text-align: center; padding: 60px 20px;
    color: #888; font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "compare_list" not in st.session_state:
    st.session_state.compare_list = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "cards"
if "open_detail" not in st.session_state:
    st.session_state.open_detail = None
if "voter" not in st.session_state:
    st.session_state.voter = None


def toggle_compare(name: str):
    if name in st.session_state.compare_list:
        st.session_state.compare_list.remove(name)
    elif len(st.session_state.compare_list) < 3:
        st.session_state.compare_list.append(name)


@st.dialog("Property Details", width="large")
def show_card_details(prop):
    col_img, col_info = st.columns([1, 1])
    with col_img:
        if prop["Photo URL"]:
            st.image(prop["Photo URL"], use_container_width=True)
    with col_info:
        loc_color = {"Da Nang": "#0c447c", "HCM": "#085041"}.get(prop["Location"], "#444")
        st.markdown(
            f'<span style="background:#e6f1fb;color:{loc_color};font-size:11px;'
            f'font-weight:600;padding:3px 10px;border-radius:20px">{prop["Location"]}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="font-size:12px;color:#888">{prop["Distance Category"]} from beach/center</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"### {prop['Name']}")
        st.markdown(f"**Rp {int(prop['Fee/night (IDR)']):,}/night**".replace(",", "."))
        st.markdown(f"★ {prop['Rating']:.1f} · {int(prop['Reviews'])} reviews" if pd.notna(prop["Rating"]) else "No rating")
        st.markdown(f"{prop['Bedroom']}BR · {prop['Bed']} beds · max {prop['Max Guests']} guests")

    st.divider()

    a1, a2, a3, a4 = st.columns(4)
    for col, label, val in [
        (a1, "Beach view", prop["Beach View"]),
        (a2, "Pool", prop["Pool"]),
        (a3, "Washing machine", prop["Washing Machine"]),
        (a4, "Iron", prop["Iron"]),
    ]:
        icon = "✓" if val.startswith("Yes") else "✗"
        color = "#4ade80" if val.startswith("Yes") else "#f87171"
        col.markdown(f'<div style="font-size:13px;color:{color};font-weight:600">{icon} {label}</div>'
                     f'<div style="font-size:12px;color:#aaa">{val}</div>', unsafe_allow_html=True)

    if prop["Remarks"]:
        st.divider()
        st.markdown(f"**Notes:** {prop['Remarks']}")

    st.divider()
    btn1, btn2 = st.columns(2)
    with btn1:
        if prop["Link"]:
            st.link_button("View on Airbnb →", prop["Link"], use_container_width=True)
    with btn2:
        if prop["Maps"]:
            st.link_button("Open in Maps →", prop["Maps"], use_container_width=True)


# ── Load data ─────────────────────────────────────────────────────────────────
df_all = load_stays()
no_data = len(df_all) == 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 Stay Picker")
    st.caption("Vietnam Trip 2026 · Filter & compare stays")

    if st.button("🔄 Reload data from Excel"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    if no_data:
        st.warning("No data found. Make sure `stays.xlsx` is in the project folder with a `Stays` sheet.")
        st.stop()

    opts = get_filter_options(df_all)

    # Location
    st.markdown("**Location**")
    loc_options = ["All"] + opts["locations"]
    selected_loc = st.radio("", loc_options, horizontal=True, label_visibility="collapsed")

    st.divider()

    # Price
    st.markdown("**Price / night (IDR)**")
    price_range = st.slider(
        "", opts["price_min"], max(opts["price_max"], opts["price_min"] + 1),
        (opts["price_min"], opts["price_max"]),
        step=50000, label_visibility="collapsed",
        format="%d",
    )

    st.divider()

    # Bedrooms
    st.markdown("**Min bedrooms**")
    br_opts = ["Any"] + [str(b) for b in opts["bedrooms"]]
    selected_br = st.radio("", br_opts, horizontal=True, label_visibility="collapsed")

    st.divider()

    # Min rating
    st.markdown("**Min rating**")
    min_rating = st.slider("", 4.0, 5.0, opts["rating_min"], step=0.1,
                            label_visibility="collapsed")

    st.divider()

    # Distance
    st.markdown("**Max distance from beach/center**")
    dist_labels = {
        "Beachfront (~0m)": 0.05,
        "<500m": 0.35,
        "<1km": 0.75,
        ">1km (any)": 99.0,
    }
    selected_dist_label = st.select_slider(
        "", options=list(dist_labels.keys()),
        value=">1km (any)", label_visibility="collapsed"
    )
    max_dist_km = dist_labels[selected_dist_label]

    st.divider()

    # Amenity toggles
    st.markdown("**Amenities**")
    need_beach = st.toggle("Beach view", value=False)
    need_pool = st.toggle("Pool", value=False)
    need_washer = st.toggle("Washing machine", value=False)
    need_iron = st.toggle("Iron", value=False)

    st.divider()

    # Min guests
    st.markdown("**Min guests capacity**")
    min_guests = st.number_input("", min_value=1, max_value=10, value=5,
                                  label_visibility="collapsed")

    st.divider()

    # Sort
    st.markdown("**Sort by**")
    sort_by = st.selectbox("", [
        "Price: low → high",
        "Price: high → low",
        "Rating: high → low",
        "Reviews: most first",
        "Distance: closest first",
        "Most liked (votes)",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**Map options**")
    show_itin = st.toggle("Show itinerary stops", value=False)

    st.divider()
    st.markdown("**👤 Your name**")
    _v_opts = ["— select —"] + VOTERS
    _v_idx = (_v_opts.index(st.session_state.voter)
              if st.session_state.voter in _v_opts else 0)
    _v_sel = st.selectbox("", _v_opts, index=_v_idx, label_visibility="collapsed")
    if _v_sel != "— select —":
        st.session_state.voter = _v_sel

    st.divider()
    st.caption(f"📁 Source: `stays.xlsx`")
    if len(df_all):
        st.caption(f"Total properties: {len(df_all)}")


# ── Filter logic ──────────────────────────────────────────────────────────────
df = df_all.copy()

if selected_loc != "All":
    df = df[df["Location"] == selected_loc]

df = df[
    (df["Fee/night (IDR)"] >= price_range[0]) &
    (df["Fee/night (IDR)"] <= price_range[1])
]

if selected_br != "Any":
    df = df[df["Bedroom"] >= int(selected_br)]

if df["Rating"].notna().any():
    df = df[df["Rating"].isna() | (df["Rating"] >= min_rating)]

if max_dist_km < 99.0:
    df = df[df["distance_km"] <= max_dist_km]

if need_beach:
    df = df[df["Beach View"] == "Yes"]
if need_pool:
    df = df[df["Pool"] == "Yes"]
if need_washer:
    df = df[df["Washing Machine"].str.startswith("Yes")]
if need_iron:
    df = df[df["Iron"] == "Yes"]

df = df[df["Max Guests"] >= min_guests]

# Sort
if sort_by == "Most liked (votes)":
    try:
        _sv = fetch_votes()
    except Exception:
        _sv = {}
    df["vote_score"] = df["Name"].apply(lambda n: sum(_sv.get(n, {}).values()))
    df = df.sort_values("vote_score", ascending=False, na_position="last").reset_index(drop=True)
else:
    sort_map = {
        "Price: low → high": ("Fee/night (IDR)", True),
        "Price: high → low": ("Fee/night (IDR)", False),
        "Rating: high → low": ("Rating", False),
        "Reviews: most first": ("Reviews", False),
        "Distance: closest first": ("distance_km", True),
    }
    sort_col, sort_asc = sort_map[sort_by]
    df = df.sort_values(sort_col, ascending=sort_asc, na_position="last").reset_index(drop=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def loc_badge_class(loc: str) -> str:
    return {"Da Nang": "loc-danang", "HCM": "loc-hcm"}.get(loc, "loc-other")


def format_price(val: int) -> str:
    return f"Rp {val:,}".replace(",", ".")


def star_str(rating) -> str:
    if pd.isna(rating):
        return "No rating"
    filled = int(rating)
    return "★" * filled + "☆" * (5 - filled) + f"  {rating:.1f}"


def _vote_tally_html(prop_votes: dict) -> str:
    if not prop_votes:
        return ""
    ups = sum(1 for v in prop_votes.values() if v == 1)
    downs = sum(1 for v in prop_votes.values() if v == -1)
    parts = []
    if ups:
        parts.append(f'<span style="color:#4ade80">👍 {ups}</span>')
    if downs:
        parts.append(f'<span style="color:#f87171">👎 {downs}</span>')
    return f'<div style="font-size:12px;margin-top:4px">{"&nbsp;&nbsp;".join(parts)}</div>'


def amenity_pill(label: str, val: str) -> str:
    cls = "yes" if val.startswith("Yes") else ("no" if val == "No" else "")
    icon = "✓" if val.startswith("Yes") else ("✗" if val == "No" else "")
    return f'<span class="amenity {cls}">{icon} {label}</span>'


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"## 🏠 Stay Picker — Vietnam 2026")

# Compare strip
if st.session_state.compare_list:
    pills = " ".join([f'<span style="background:#1a1a18;color:white;font-size:11px;'
                      f'padding:3px 10px;border-radius:20px;margin-right:4px">'
                      f'{n}</span>' for n in st.session_state.compare_list])
    st.markdown(
        f'<div class="compare-header">'
        f'<span>Comparing:</span> {pills}'
        f'<span style="margin-left:auto;font-size:12px;color:#aaa">'
        f'Select up to 3 properties</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Tab nav (session-state-based so reruns don't reset the active tab) ────────
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-tabNav"]) {
    gap: 0; border-bottom: 1px solid #333; margin-bottom: 12px;
}
button[data-testid="baseButton-tabNav"] {
    border-radius: 0; border: none; border-bottom: 2px solid transparent;
    background: transparent; color: #888; font-size: 14px; padding: 8px 16px;
}
button[data-testid="baseButton-tabNav"]:hover { color: #ccc; }
button[data-testid="baseButton-tabNav"].active-tab {
    color: #e05c5c; border-bottom-color: #e05c5c;
}
</style>
""", unsafe_allow_html=True)

_tab_cols = st.columns([1.3, 1.3, 1.3, 1.3, 3.5])
_tabs = [("cards", "🃏 Cards"), ("compare", "⚖️ Compare"), ("map", "🗺️ Map"), ("vote", "🗳️ Vote")]
for _col, (_key, _label) in zip(_tab_cols, _tabs):
    with _col:
        if st.button(_label, key=f"tabnav_{_key}", use_container_width=True):
            st.session_state.active_tab = _key

_active = st.session_state.active_tab

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — CARD VIEW
# ──────────────────────────────────────────────────────────────────────────────
if _active == "cards":
    st.caption(f"Showing {len(df)} of {len(df_all)} properties")

    if len(df) == 0:
        st.markdown('<div class="no-data-msg">No properties match your filters.<br>'
                    '<small>Try relaxing the price range or amenity toggles.</small></div>',
                    unsafe_allow_html=True)
    else:
        try:
            _votes_data = fetch_votes()
        except Exception:
            _votes_data = {}

        cols = st.columns(3)
        for idx, row in df.iterrows():
            col = cols[idx % 3]
            is_selected = row["Name"] in st.session_state.compare_list
            card_cls = "prop-card selected" if is_selected else "prop-card"

            with col:
                # Photo
                photo_html = ""
                if row["Photo URL"]:
                    photo_html = f'<img src="{row["Photo URL"]}" alt="{row["Name"]}" />'
                else:
                    photo_html = '<div class="no-photo">No photo</div>'

                loc_cls = loc_badge_class(row["Location"])
                st.markdown(
                    f'<div class="{card_cls}">'
                    f'<div class="card-img-wrap">'
                    f'{photo_html}'
                    f'<span class="loc-badge {loc_cls}">{row["Location"]}</span>'
                    f'<span class="dist-badge">{row["Distance Category"]}</span>'
                    f'</div>'
                    f'<div class="card-body">'
                    f'<div class="card-name">{row["Name"]}</div>'
                    f'<div class="card-price">{format_price(row["Fee/night (IDR)"])} '
                    f'<span>/ night</span></div>'
                    f'<div class="card-rating">{star_str(row["Rating"])} '
                    f'<span style="color:#aaa">({row["Reviews"]} reviews)</span></div>'
                    f'<div class="card-meta">{row["Bedroom"]}BR · {row["Bed"]} beds · '
                    f'max {row["Max Guests"]} guests</div>'
                    f'<div class="amenity-row">'
                    f'{amenity_pill("Beach view", row["Beach View"])}'
                    f'{amenity_pill("Pool", row["Pool"])}'
                    f'{amenity_pill("Washer", row["Washing Machine"])}'
                    f'{amenity_pill("Iron", row["Iron"])}'
                    f'</div>'
                    + (f'<div style="font-size:13px;color:#888;margin-top:2px;'
                       f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
                       f'📝 {row["Remarks"]}</div>' if row["Remarks"] else '')
                    + _vote_tally_html(_votes_data.get(row["Name"], {}))
                    + f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                _voter = st.session_state.voter
                _my_vote = _votes_data.get(row["Name"], {}).get(_voter) if _voter else None
                d_col, up_col, dn_col = st.columns([2, 1, 1])
                with d_col:
                    if st.button("Details", key=f"det_{idx}", use_container_width=True):
                        st.session_state.open_detail = row["Name"]
                        st.rerun()
                with up_col:
                    lbl = "👍 ✓" if _my_vote == 1 else "👍"
                    if st.button(lbl, key=f"cup_{idx}", use_container_width=True, disabled=not _voter):
                        if _my_vote == 1:
                            delete_vote(row["Name"], _voter)
                        else:
                            upsert_vote(row["Name"], _voter, 1)
                        st.rerun()
                with dn_col:
                    lbl = "👎 ✓" if _my_vote == -1 else "👎"
                    if st.button(lbl, key=f"cdn_{idx}", use_container_width=True, disabled=not _voter):
                        if _my_vote == -1:
                            delete_vote(row["Name"], _voter)
                        else:
                            upsert_vote(row["Name"], _voter, -1)
                        st.rerun()
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    compare_label = "✓ Selected" if is_selected else "+ Compare"
                    if st.button(compare_label, key=f"cmp_{idx}", use_container_width=True):
                        toggle_compare(row["Name"])
                        st.rerun()
                with c2:
                    if row["Link"]:
                        st.link_button("Airbnb", row["Link"], use_container_width=True)
                with c3:
                    if row["Maps"]:
                        st.link_button("Maps", row["Maps"], use_container_width=True)

# ── Detail dialog trigger ─────────────────────────────────────────────────────
if st.session_state.open_detail:
    match = df_all[df_all["Name"] == st.session_state.open_detail]
    if len(match):
        show_card_details(match.iloc[0])
    st.session_state.open_detail = None


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — COMPARE
# ──────────────────────────────────────────────────────────────────────────────
if _active == "compare":
    if len(st.session_state.compare_list) < 2:
        st.info("Select at least 2 properties from the Card view to compare them here.")
    else:
        compare_df = df_all[df_all["Name"].isin(st.session_state.compare_list)]

        if st.button("Clear compare list"):
            st.session_state.compare_list = []
            st.rerun()

        st.markdown("---")

        # Photo row
        img_cols = st.columns(len(compare_df))
        for i, (_, row) in enumerate(compare_df.iterrows()):
            with img_cols[i]:
                if row["Photo URL"]:
                    st.image(row["Photo URL"], use_container_width=True)
                st.markdown(f"**{row['Name']}**")
                st.caption(f"{row['Location']} · {row['Distance Category']}")

        st.markdown("---")

        # Compare table
        compare_fields = [
            ("Price / night", lambda r: format_price(r["Fee/night (IDR)"])),
            ("Rating", lambda r: f"★ {r['Rating']:.1f}" if pd.notna(r["Rating"]) else "—"),
            ("Reviews", lambda r: str(r["Reviews"])),
            ("Bedrooms", lambda r: f"{r['Bedroom']}BR"),
            ("Beds", lambda r: str(r["Bed"])),
            ("Max guests", lambda r: str(r["Max Guests"])),
            ("Beach view", lambda r: "✓ Yes" if r["Beach View"] == "Yes" else "✗ No"),
            ("Pool", lambda r: "✓ Yes" if r["Pool"] == "Yes" else "✗ No"),
            ("Washing machine", lambda r: "✓ " + r["Washing Machine"] if r["Washing Machine"].startswith("Yes") else "✗ No"),
            ("Iron", lambda r: "✓ Yes" if r["Iron"] == "Yes" else "✗ No"),
            ("Distance", lambda r: r["Distance Category"]),
            ("Remarks", lambda r: r["Remarks"] or "—"),
        ]

        for label, fn in compare_fields:
            row_cols = st.columns([1] + [1] * len(compare_df))
            row_cols[0].markdown(
                f'<span style="font-size:14px;color:#888">{label}</span>',
                unsafe_allow_html=True,
            )
            for i, (_, prop) in enumerate(compare_df.iterrows()):
                val = fn(prop)
                color = "#4ade80" if val.startswith("✓") else ("#f87171" if val.startswith("✗") else "#e8e6e0")
                row_cols[i + 1].markdown(
                    f'<span style="font-size:15px;color:{color}">{val}</span>',
                    unsafe_allow_html=True,
                )
            st.markdown('<hr style="margin:4px 0;border-color:#333">', unsafe_allow_html=True)

        st.markdown("---")

        # Link buttons
        link_cols = st.columns(len(compare_df))
        for i, (_, row) in enumerate(compare_df.iterrows()):
            with link_cols[i]:
                if row["Link"]:
                    st.link_button("View on Airbnb →", row["Link"], use_container_width=True)
                if row["Maps"]:
                    st.link_button("Open in Maps →", row["Maps"], use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — MAP VIEW
# ──────────────────────────────────────────────────────────────────────────────
if _active == "map":
    st.caption("Blue markers = Da Nang · Green markers = HCM · Red = currently comparing · Orange dots = itinerary stops")

    from itinerary_stops import STOPS as _itin_stops
    itin_stops = _itin_stops if show_itin else None

    m = build_stays_map(
        df,
        selected_names=st.session_state.compare_list,
        itinerary_stops=itin_stops,
    )
    st_folium(m, width="100%", height=650, returned_objects=[])

    # List of properties with no map coords
    no_coords = df[df.apply(
        lambda r: not r["Maps"] or
        (not any(c in str(r["Maps"]) for c in ["@", "q=", "ll=", "search/"])),
        axis=1
    )]
    if len(no_coords):
        with st.expander(f"⚠️ {len(no_coords)} properties missing map coordinates"):
            for _, r in no_coords.iterrows():
                st.markdown(f"- **{r['Name']}** ({r['Location']}) — Maps URL is empty or shortened. "
                            f"Use full Google Maps URL with coordinates for this marker to appear.")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — VOTE
# ──────────────────────────────────────────────────────────────────────────────
if _active == "vote":
    voter = st.session_state.voter

    if not voter:
        st.info("👆 Select your name in the sidebar to start voting.")

    try:
        votes_data = fetch_votes()
        _votes_ok = True
    except Exception as e:
        st.error(f"Could not connect to vote database: {e}")
        votes_data = {}
        _votes_ok = False

    # Sort all properties by score descending
    props_scored = []
    for _, row in df_all.iterrows():
        pv = votes_data.get(row["Name"], {})
        props_scored.append((sum(pv.values()), row, pv))
    props_scored.sort(key=lambda x: -x[0])

    # Header row
    h1, h2, h3, h4 = st.columns([3, 2, 2, 2])
    for col, txt in zip([h1, h2, h3, h4], ["Property", "Score", "Votes", "Your vote"]):
        col.markdown(f'<span style="font-size:11px;font-weight:600;text-transform:uppercase;'
                     f'letter-spacing:.06em;color:#888">{txt}</span>', unsafe_allow_html=True)
    st.markdown('<hr style="margin:4px 0 8px;border-color:#333">', unsafe_allow_html=True)

    for score, row, pv in props_scored:
        c_prop, c_score, c_voters, c_btn = st.columns([3, 2, 2, 2])

        with c_prop:
            loc_color = {"Da Nang": "#378ADD", "HCM": "#1D9E75"}.get(row["Location"], "#888")
            st.markdown(
                f'<div style="font-size:14px;font-weight:600">{row["Name"]}</div>'
                f'<div style="font-size:12px;color:{loc_color}">{row["Location"]} · '
                f'{format_price(row["Fee/night (IDR)"])}</div>',
                unsafe_allow_html=True,
            )

        with c_score:
            score_color = "#4ade80" if score > 0 else ("#f87171" if score < 0 else "#888")
            sign = "+" if score > 0 else ""
            st.markdown(
                f'<div style="font-size:22px;font-weight:700;color:{score_color}">'
                f'{sign}{score}</div>',
                unsafe_allow_html=True,
            )

        with c_voters:
            chips = ""
            for v in VOTERS:
                vote = pv.get(v)
                if vote == 1:
                    chips += (f'<span style="background:#14532d;color:#4ade80;font-size:11px;'
                              f'padding:2px 7px;border-radius:20px;margin:2px 2px 0 0;'
                              f'display:inline-block">👍 {v}</span>')
                elif vote == -1:
                    chips += (f'<span style="background:#450a0a;color:#f87171;font-size:11px;'
                              f'padding:2px 7px;border-radius:20px;margin:2px 2px 0 0;'
                              f'display:inline-block">👎 {v}</span>')
                else:
                    chips += (f'<span style="background:#2a2a28;color:#666;font-size:11px;'
                              f'padding:2px 7px;border-radius:20px;margin:2px 2px 0 0;'
                              f'display:inline-block">— {v}</span>')
            st.markdown(chips, unsafe_allow_html=True)

        with c_btn:
            if voter and _votes_ok:
                my_vote = pv.get(voter)
                b1, b2 = st.columns(2)
                with b1:
                    lbl = "👍 ✓" if my_vote == 1 else "👍"
                    if st.button(lbl, key=f"vup_{row['Name']}", use_container_width=True):
                        if my_vote == 1:
                            delete_vote(row["Name"], voter)
                        else:
                            upsert_vote(row["Name"], voter, 1)
                        st.rerun()
                with b2:
                    lbl = "👎 ✓" if my_vote == -1 else "👎"
                    if st.button(lbl, key=f"vdn_{row['Name']}", use_container_width=True):
                        if my_vote == -1:
                            delete_vote(row["Name"], voter)
                        else:
                            upsert_vote(row["Name"], voter, -1)
                        st.rerun()

        st.markdown('<hr style="margin:6px 0;border-color:#222">', unsafe_allow_html=True)
