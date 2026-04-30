"""
2_Closest_Location.py
--------------------------------------------------------
Page 2: Where is the nearest Starbucks to me?
User types any address or city and the app finds the closest stores
using the Haversine formula, then plots them on an interactive map.
Controls moved to main page body so they're always visible.
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from utils import load_data, apply_sidebar_style, STARBUCKS_GREEN, BACKGROUND_DARK

# -- Page config ---------------------------------------------------------------
st.set_page_config(page_title="Nearest Starbucks - Explorer",
                   page_icon="📍", layout="wide")
apply_sidebar_style()   # #[FUNCCALL2]

# -- Load data -----------------------------------------------------------------
df = load_data()        # #[FUNCCALL2]

# -- Haversine formula ---------------------------------------------------------  #[FUNC2P]
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance in kilometers between two points
    on Earth using the Haversine formula.

    Parameters
    ----------
    lat1, lon1 : float - coordinates of point 1 (user location)
    lat2, lon2 : float - coordinates of point 2 (store location)

    Returns
    -------
    float - distance in kilometers
    """
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# -- Geocode address -----------------------------------------------------------  #[FUNCRETURN2]
@st.cache_data(show_spinner=False)
def geocode_address(address: str) -> tuple:
    import time
    try:
        time.sleep(1)  # Nominatim requires 1 second between requests
        geolocator = Nominatim(user_agent="sbux_cs230_enrique")
        location = geolocator.geocode(address, timeout=15)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception:
        return None, None

# -- Page header ---------------------------------------------------------------
st.markdown("# 📍 Find Your Nearest Starbucks")
st.markdown(
    "Enter an address, city, or landmark below and we'll find "
    "the closest Starbucks locations using straight-line distance."
)

st.markdown("---")

# ── Controls in main page (moved from sidebar) ────────────────────────────────
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 1, 2])

with ctrl_col1:
    # #[ST1] - text input for address
    user_address = st.text_input(
        "Enter your address or city:",
        placeholder="e.g. Boston, MA  or  1 Apple Park, Cupertino",
    )

with ctrl_col2:
    # #[ST2] - slider for how many results to show
    top_k = st.slider(
        "Nearest stores to show:",
        min_value=1,
        max_value=5,
        value=2,
    )

with ctrl_col3:
    # #[ST3] - radio to filter by ownership type
    ownership_filter = st.radio(
        "Filter by ownership type:",
        options=["All", "Company Owned", "Licensed", "Joint Venture", "Franchise"],
        index=0,
        horizontal=True,
    )

search_btn = st.button("🔍 Find Nearest Starbucks", type="primary", use_container_width=False)

st.markdown("---")

# -- Main logic ----------------------------------------------------------------
if not user_address or not search_btn:
    col1, col2 = st.columns(2)
    col1.info("👆 Enter an address above and click **Find Nearest Starbucks** to get started.")
    col1.markdown("""
    **How it works:**
    1. Type any address or city
    2. Choose how many results to show
    3. Optionally filter by ownership type
    4. Click the search button
    """)
    col2.markdown("""
    **Example searches:**
    - `Boston, MA`
    - `Times Square, New York`
    - `London, UK`
    - `1600 Pennsylvania Ave, Washington DC`
    """)

else:
    with st.spinner(f"Finding your location: {user_address}..."):
        user_lat, user_lon = geocode_address(user_address)   # #[FUNCRETURN2]

    if user_lat is None:
        st.error("Could not find that address. Try being more specific, e.g. 'Boston, MA, USA'")
    else:
        st.success(f"Found location: {user_lat:.4f}, {user_lon:.4f}")

        # Apply ownership filter                              #[FILTER1] #[FILTER2]
        if ownership_filter == "All":
            search_df = df.copy()
        else:
            search_df = df[df["Ownership Type"] == ownership_filter].copy()  # #[FILTER2]

        # Calculate distance from user to every store        #[ITERLOOP]
        distances = []
        for _, row in search_df.iterrows():
            dist = haversine(user_lat, user_lon, row["Latitude"], row["Longitude"])
            distances.append(dist)

        search_df["Distance (km)"] = distances
        search_df["Distance (mi)"] = (search_df["Distance (km)"] * 0.621371).round(2)

        # Sort by distance and take top K                    #[SORT] #[MAXMIN]
        nearest = search_df.sort_values("Distance (km)").head(top_k)
        closest = nearest.iloc[0]   # #[MAXMIN] - the single nearest store

        # -- Stat callouts -------------------------------------------------
        col1, col2, col3 = st.columns(3)
        col1.metric("Nearest Store", closest["Store Name"])
        col2.metric("Distance", f"{closest['Distance (mi)']:.2f} mi  /  {closest['Distance (km)']:.2f} km")
        col3.metric("City", f"{closest['City']}, {closest['Country']}")

        st.markdown("---")
        st.markdown(f"### {top_k} Nearest Starbucks to '{user_address}'")
        st.markdown("🔴 Red dot = your location &nbsp;&nbsp; 🟢 Green dots = Starbucks stores")

        # -- Build map layers ----------------------------------------------  #[MAP]
        user_point = pd.DataFrame([{
            "Latitude": user_lat,
            "Longitude": user_lon,
            "label": "Your Location",
        }])

        user_layer = pdk.Layer(
            "ScatterplotLayer",
            data=user_point,
            get_position=["Longitude", "Latitude"],
            get_color=[220, 50, 50, 240],
            get_radius=300,
            pickable=True,
            auto_highlight=True,
        )

        nearest = nearest.copy()
        nearest["color"] = [[0, 112, 74, 210]] * len(nearest)  # #[COLUMNS]

        stores_layer = pdk.Layer(
            "ScatterplotLayer",
            data=nearest,
            get_position=["Longitude", "Latitude"],
            get_color="color",
            get_radius=200,
            pickable=True,
            auto_highlight=True,
        )

        view = pdk.ViewState(
            latitude=user_lat,
            longitude=user_lon,
            zoom=11,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[stores_layer, user_layer],
            initial_view_state=view,
            tooltip={
                "html": "<b>{Store Name}</b><br/>{Street Address}<br/>{City} · {Distance (mi)} mi",
                "style": {
                    "backgroundColor": "#1E3932",
                    "color": "white",
                    "fontSize": "13px",
                    "padding": "8px",
                    "borderRadius": "6px",
                }
            },
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        )

        st.pydeck_chart(deck)

        # -- Results table -------------------------------------------------
        st.markdown("### Results")
        display_cols = ["Store Name", "Street Address", "City",
                        "Country", "Ownership Type", "Distance (mi)", "Distance (km)"]
        st.dataframe(
            nearest[display_cols].reset_index(drop=True),
            use_container_width=True
        )

        st.caption("Location data via OpenStreetMap / Nominatim")