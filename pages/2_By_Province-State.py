"""
2_Por_Estado.py
---------------
Page 2: How many Starbucks are in a specific state or province?
User selects a country and then a state/province to see all stores
plotted on an interactive PyDeck map with auto-zoom.
"""

import streamlit as st
import pydeck as pdk
import math
from utils import (load_data, apply_sidebar_style, get_country_list,
                   get_states_for_country, filter_by_country_and_state,
                   clean_display_table, STARBUCKS_GREEN, BACKGROUND_DARK)

# -- Page config ---------------------------------------------------------------
st.set_page_config(page_title="By State - Starbucks Explorer",
                   page_icon="🗺️", layout="wide")
apply_sidebar_style()   # #[FUNCCALL2]

# -- Load data -----------------------------------------------------------------
df = load_data()        # #[FUNCCALL2]

# -- Helper: auto zoom ---------------------------------------------------------  #[FUNC2P]
def calculate_zoom(lat_range: float, lon_range: float, default: float = 5.0) -> float:
    """
    Estimate an appropriate PyDeck zoom level based on the geographic
    spread (range) of latitude and longitude values.

    Parameters
    ----------
    lat_range : float  - difference between max and min latitude
    lon_range : float  - difference between max and min longitude
    default   : float  - fallback zoom if range is zero (single store)

    Returns
    -------
    float - zoom level between 1 (world) and 13 (street level)
    """
    max_range = max(lat_range, lon_range)
    if max_range == 0:
        return default
    # Larger spread = smaller zoom number
    zoom = math.log2(360 / max_range) - 1
    return round(max(1.0, min(zoom, 13.0)), 1)

# -- Sidebar widgets -----------------------------------------------------------
with st.sidebar:
    st.title("🗺️ Explore by State")
    st.markdown("---")

    # #[ST1] - country dropdown
    country_list = get_country_list(df)
    selected_country = st.selectbox(
        "Select a Country:",
        options = country_list,
        index   = country_list.index("US"),
    )

    # #[ST1] - state dropdown (updates based on country)
    state_list = get_states_for_country(df, selected_country)
    selected_state = st.selectbox(
        "Select a State / Province:",
        options = state_list,
    )

    st.markdown("---")

    # #[ST3] - toggle to show/hide the data table below the map
    show_table = st.toggle("Show store list", value=False)

    # #[ST2] - slider to control map dot size
    dot_size = st.slider(
        "Map dot size:",
        min_value = 500,
        max_value = 5000,
        value     = 1500,
        step      = 500,
    )

# -- Filter data ---------------------------------------------------------------
state_df = filter_by_country_and_state(df, selected_country, selected_state)  # #[FILTER2]

# -- Page header ---------------------------------------------------------------
st.markdown(f"# 🗺️ Starbucks in {selected_state}, {selected_country}")

# -- Stat callouts -------------------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Stores in this State", f"{len(state_df):,}")
col2.metric(
    "City with Most Stores",
    state_df["City"].value_counts().idxmax() if len(state_df) > 0 else "N/A"  # #[MAXMIN]
)
col3.metric(
    "Ownership Types",
    state_df["Ownership Type"].nunique() if len(state_df) > 0 else 0
)

st.markdown("---")

# -- PyDeck map ----------------------------------------------------------------  #[MAP]
if len(state_df) == 0:
    st.warning("No stores found for this selection. Try a different state.")
else:
    st.markdown(f"### All {len(state_df):,} Starbucks in {selected_state}")
    st.markdown("Hover over any dot to see the store name and address.")

    # Color by ownership type
    ownership_colors = {
        "Company Owned" : [0, 112, 74, 200],
        "Licensed"      : [203, 162, 88, 200],
        "Joint Venture" : [41, 98, 195, 200],
        "Franchise"     : [200, 70, 50, 200],
    }

    # Add color column                                               #[COLUMNS]
    state_df = state_df.copy()
    state_df["color"] = state_df["Ownership Type"].apply(
        lambda o: ownership_colors.get(o, [150, 150, 150, 200])
    )

    # Build tooltip text                                             #[ITERLOOP]
    tooltip_rows = []
    for _, row in state_df.iterrows():
        tooltip_rows.append(f"{row['Store Name']} | {row['City']}")
    state_df["tooltip"] = tooltip_rows

    # Auto-zoom based on geographic spread of the stores
    lat_range = state_df["Latitude"].max()  - state_df["Latitude"].min()   # #[MAXMIN]
    lon_range = state_df["Longitude"].max() - state_df["Longitude"].min()
    auto_zoom = calculate_zoom(lat_range, lon_range)

    avg_lat = state_df["Latitude"].mean()
    avg_lon = state_df["Longitude"].mean()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data           = state_df,
        get_position   = ["Longitude", "Latitude"],
        get_color      = "color",
        get_radius     = dot_size,
        pickable       = True,
        auto_highlight = True,
    )

    view = pdk.ViewState(
        latitude  = avg_lat,
        longitude = avg_lon,
        zoom      = auto_zoom,   # dynamic zoom!
        pitch     = 0,
    )

    deck = pdk.Deck(
        layers             = [layer],
        initial_view_state = view,
        tooltip = {
            "html"  : "<b>{Store Name}</b><br/>{Street Address}<br/>{City} · {Ownership Type}",
            "style" : {
                "backgroundColor" : "#1E3932",
                "color"           : "white",
                "fontSize"        : "13px",
                "padding"         : "8px",
                "borderRadius"    : "6px",
            }
        },
        map_style = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )

    st.pydeck_chart(deck)

    # Legend
    st.markdown("**Map Legend:**")
    leg1, leg2, leg3, leg4 = st.columns(4)
    leg1.markdown("🟢 Company Owned")
    leg2.markdown("🟡 Licensed")
    leg3.markdown("🔵 Joint Venture")
    leg4.markdown("🔴 Franchise")

    st.markdown("---")

    # Optional store list
    if show_table:
        st.markdown(f"### Store List — {selected_state}, {selected_country}")
        sorted_df = state_df.sort_values("City")                   # #[SORT]
        display   = clean_display_table(sorted_df)
        st.dataframe(display, use_container_width=True)