"""
Name:       Enrique
CS230:      Section XXX
Data:       Starbucks Store Locations (directory.csv)
URL:        (link to Streamlit Cloud once published)

Description:
    This program explores the global presence of Starbucks using an
    interactive web application built with Streamlit. Users can discover
    which countries have the most stores, explore locations by state or
    province, find nearest starbucks, and find the top cities in any
    country. The app uses filtering, sorting, charts, and an interactive
    map to tell the story of Starbucks around the world.

References:
    - Streamlit documentation: https://docs.streamlit.io
    - PyDeck documentation:    https://deckgl.readthedocs.io
    - Dataset source:          https://www.kaggle.com/datasets/starbucks/store-locations
"""

import streamlit as st
from utils import load_data, apply_sidebar_style, STARBUCKS_GREEN, BACKGROUND_DARK, TEXT_LIGHT

# ── Page configuration (must be the very first Streamlit call) ────────────────
st.set_page_config(
    page_title = "Starbucks Explorer",
    page_icon  = "☕",
    layout     = "wide",
)

# ── Apply sidebar style ───────────────────────────────────────────────────────
apply_sidebar_style()   # #[FUNCCALL2] – also called in every other page

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()        # #[FUNCCALL2]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📌 Navigate")
    st.markdown("""
    Use the **pages menu** above to explore:

    - 🌍 **Top Countries** — which countries have the most stores?
    - 🗺️ **By State** — explore stores on a map by state/province
    - 📍 **Nearest Location** — find the closest Starbucks to you
    - 🏙️ **Top Cities** — which cities have the most Starbucks?
    """)

# ── Hero section ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, {BACKGROUND_DARK} 0%, #2d5a27 100%);
        padding: 3rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
    ">
        <h1 style="color: #ffffff; font-size: 3rem; margin-bottom: 0.5rem;">
            ☕ Starbucks Explorer
        </h1>
        <p style="color: #d4e9d4; font-size: 1.2rem; max-width: 650px;">
            Explore <strong style="color:#CBA258">{len(df):,} Starbucks locations</strong>
            across <strong style="color:#CBA258">{df['Country'].nunique()} countries</strong>.
            Discover patterns, compare regions, and find out where the world
            runs on green cups.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Quick stats row ───────────────────────────────────────────────────────────
total_stores   = len(df)
total_countries = df["Country"].nunique()
total_cities   = df["City"].nunique()
top_country    = df["Country"].value_counts().idxmax()   # #[MAXMIN]
top_country_n  = df["Country"].value_counts().max()

col1, col2, col3, col4 = st.columns(4)

def metric_card(col, emoji, value, label):
    """Display a styled metric card. #[FUNC2P] #[FUNCCALL2]"""
    col.markdown(
        f"""
        <div style="
            background-color: {BACKGROUND_DARK};
            border-left: 5px solid {STARBUCKS_GREEN};
            padding: 1.2rem 1rem;
            border-radius: 10px;
            text-align: center;
        ">
            <div style="font-size:2rem">{emoji}</div>
            <div style="color:#ffffff; font-size:1.8rem; font-weight:700">{value}</div>
            <div style="color:#aaaaaa; font-size:0.85rem">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

metric_card(col1, "🏪", f"{total_stores:,}",    "Total Stores")
metric_card(col2, "🌍", f"{total_countries}",   "Countries")
metric_card(col3, "🏙️", f"{total_cities:,}",   "Cities")
metric_card(col4, "🥇", f"{top_country} ({top_country_n:,})", "Biggest Market")

# ── What can you explore section ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"## What can you explore?")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    #### 🌍 Top Countries
    Which countries have the most Starbucks locations?
    Use a slider to adjust how many countries to compare and see an
    interactive ranking chart.
    """)
    st.markdown(f"""
    #### 📍 Nearest Location
    Type any address or city and instantly find the closest
    Starbucks to you on an interactive map with distances.
    """)

with c2:
    st.markdown(f"""
    #### 🗺️ Explore by State
    Pick a country and a state or province to see every Starbucks
    plotted on an interactive map — with store name and address on hover.
    """)
    st.markdown(f"""
    #### 🏙️ Top Cities
    Which city in your chosen country has the most Starbucks?
    See a ranked chart and spotlight the top location.
    """)

st.markdown("---")
st.caption("CS230 Final Project · Data: Starbucks Store Locations (Kaggle)")