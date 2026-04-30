"""
utils.py
--------
Shared helper functions for the Starbucks Explorer app.
This file is imported by every page so that data loading
and common operations are never repeated.
"""

import pandas as pd
import streamlit as st
import pycountry

# ── Constants ────────────────────────────────────────────────────────────────

DATA_PATH = "directory.csv"

# Starbucks brand green palette used across all pages
STARBUCKS_GREEN   = "#00704A"
STARBUCKS_LIGHT   = "#CBA258"   # warm gold accent
BACKGROUND_DARK   = "#1E3932"   # deep forest green
TEXT_LIGHT        = "#F1F8F5"

# ── Data loading & cleaning ───────────────────────────────────────────────────

#[FUNCCALL2]  – called in every page via  `from utils import load_data`
@st.cache_data   # #[ST3] caching so the CSV is only read once
def load_data() -> pd.DataFrame:
    """
    Load and clean the Starbucks directory CSV.

    Cleaning steps
    --------------
    1. Drop rows with missing City (only 15 rows – too incomplete to show).
    2. Drop the single row with no coordinates (would break the map).
    3. Drop the Phone Number column (stored as floats, no country codes – looks bad).
    4. Fill missing Postcode values with 'N/A'.
    5. Reset the index so row numbers are tidy after dropping.

    Returns
    -------
    pd.DataFrame  –  clean Starbucks dataset ready to use.
    """
    df = pd.read_csv(DATA_PATH)

    # 1. Remove rows without a city name
    df = df.dropna(subset=["City"])                     # #[FILTER1]

    # 2. Remove rows with missing coordinates (breaks pydeck map)
    df = df.dropna(subset=["Latitude", "Longitude"])    # #[FILTER2]

    # 3. Drop columns we will never display
    df = df.drop(columns=["Phone Number", "Timezone"])  # #[COLUMNS]

    # 4. Fill blank postcodes so tables look clean
    df["Postcode"] = df["Postcode"].fillna("N/A")

    # 5. Clean index
    df = df.reset_index(drop=True)

    # 6. Replace 2-letter country codes with full names
    def code_to_name(code):
        try:
            return pycountry.countries.get(alpha_2=code).name
        except Exception:
            return code   # fallback: keep original code if not found

    df["Country"] = df["Country"].apply(code_to_name)

    return df


# ── Lookup helpers ────────────────────────────────────────────────────────────

def get_country_list(df: pd.DataFrame) -> list:
    """Return a sorted list of all unique country codes in the dataset."""
    return sorted(df["Country"].unique().tolist())


#[FUNC2P]  – two parameters, second one has a default value
def get_states_for_country(df: pd.DataFrame, country: str = "US") -> list:
    """
    Return a sorted list of states/provinces for the given country.

    Parameters
    ----------
    df      : the full cleaned DataFrame
    country : 2-letter country code (default 'US')
    """
    filtered = df[df["Country"] == country]
    return sorted(filtered["State/Province"].unique().tolist())


#[FUNCRETURN2]  – returns two values
def get_country_stats(df: pd.DataFrame, country: str) -> tuple:
    """
    Return basic stats for a single country.

    Returns
    -------
    total_stores : int   – total number of Starbucks in that country
    top_city     : str   – name of the city with the most stores
    """
    country_df   = df[df["Country"] == country]
    total_stores = len(country_df)                          # #[MAXMIN] used below too
    top_city     = (
        country_df["City"]
        .value_counts()
        .idxmax()                                           # city with MAX stores
    )
    return total_stores, top_city


# ── Filtering helpers ─────────────────────────────────────────────────────────

def filter_by_country(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """Filter the DataFrame to a single country."""
    return df[df["Country"] == country]                     # #[FILTER1]


def filter_by_country_and_state(df: pd.DataFrame,
                                 country: str,
                                 state: str) -> pd.DataFrame:
    """Filter the DataFrame to a specific country AND state/province."""
    return df[                                              # #[FILTER2]
        (df["Country"] == country) &
        (df["State/Province"] == state)
    ]


# ── Display helpers ───────────────────────────────────────────────────────────

def clean_display_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a user-friendly version of the DataFrame for st.dataframe().
    Keeps only the columns that make sense to a general audience
    and renames them to plain English.
    """
    cols = {
        "Store Name"     : "Store Name",
        "Ownership Type" : "Ownership",
        "Street Address" : "Address",
        "City"           : "City",
        "State/Province" : "State / Province",
        "Country"        : "Country",
        "Postcode"       : "Postcode",
    }
    #[ITERLOOP]  – iterating through the column mapping dictionary
    available = {k: v for k, v in cols.items() if k in df.columns}
    return df[list(available.keys())].rename(columns=available)


# ── Sidebar theme helper ──────────────────────────────────────────────────────

def apply_sidebar_style():
    """
    Inject custom CSS to style the sidebar with Starbucks colours.
    Call once at the top of each page.
    """
    st.markdown(
        f"""
        <style>
        /* Sidebar background with subtle gradient */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {BACKGROUND_DARK} 0%, #142b20 100%);
            border-right: 2px solid {STARBUCKS_GREEN};
        }}
        /* Remove top gap in sidebar content */
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 0rem !important;
            margin-top: -4rem !important;

        }}
        /* Sidebar labels and text */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {{
            color: {TEXT_LIGHT} !important;
        }}
        /* Dropdown input text */
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
            color: #1E3932 !important;
        }}
        /* Hide Streamlit's native top navigation so our custom links show instead */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        /* Sidebar navigation links */
        [data-testid="stSidebar"] a {{
            color: {TEXT_LIGHT} !important;
            padding: 6px 12px;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            background-color: rgba(0, 112, 74, 0.3) !important;
        }}
        /* Active page highlight */
        [data-testid="stSidebarNav"] a[aria-selected="true"] {{
            background-color: {STARBUCKS_GREEN} !important;
            font-weight: 700;
        }}
        /* Slider accent color */
        [data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {{
            background-color: {STARBUCKS_GREEN} !important;
        }}
        /* Divider line */
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.15);
            margin: 12px 0;
        }}
        /* Fix page title - override Streamlit purple with green */
        h1, h2, h3, h4 {{
            color: {STARBUCKS_GREEN} !important;
        }}
        /* Target Streamlit's internal heading elements */
        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3 {{
            color: {STARBUCKS_GREEN} !important;
        }}
        /* Override the page title at the very top */
        [data-testid="stAppViewBlockContainer"] h1,
        [data-testid="stAppViewBlockContainer"] h2,
        [data-testid="stAppViewBlockContainer"] h3 {{
            color: {STARBUCKS_GREEN} !important;
        }}
        /* Metric value */
        [data-testid="stMetricValue"] {{
            color: {STARBUCKS_GREEN} !important;
            font-weight: 700;
        }}
        /* Hide Streamlit default black header */
        [data-testid="stHeader"] {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar header shown on every page
    st.sidebar.markdown(
        f"""
        <div style="text-align:center; padding: 8px 0 12px 0;">
            <div style="font-size: 2.6rem; margin-bottom: 4px;">☕</div>
            <div style="color:#ffffff; font-weight:800; font-size:1.05rem;
                        letter-spacing:2px; text-transform:uppercase;">
                Starbucks Explorer
            </div>
            <div style="color:#CBA258; font-size:0.75rem; margin-top:4px;">
                25,584 locations · 73 countries
            </div>
        </div>
        <hr/>
        <div style="display:flex; justify-content:space-around;
                    padding: 8px 0 12px 0; text-align:center;">
            <div>
                <div style="color:#CBA258; font-size:1.1rem; font-weight:700;">73</div>
                <div style="color:#aaa; font-size:0.7rem;">Countries</div>
            </div>
            <div style="border-left:1px solid rgba(255,255,255,0.15);"></div>
            <div>
                <div style="color:#CBA258; font-size:1.1rem; font-weight:700;">25.6k</div>
                <div style="color:#aaa; font-size:0.7rem;">Stores</div>
            </div>
            <div style="border-left:1px solid rgba(255,255,255,0.15);"></div>
            <div>
                <div style="color:#CBA258; font-size:1.1rem; font-weight:700;">5.4k</div>
                <div style="color:#aaa; font-size:0.7rem;">Cities</div>
            </div>
        </div>
        <hr/>
        """,
        unsafe_allow_html=True,
    )

    # Custom page navigation links below the header
    st.sidebar.page_link("Home.py",                    label="🏠 Home")
    st.sidebar.page_link("pages/1_Top_Countries.py",   label="🌍 Top Countries")
    st.sidebar.page_link("pages/2_Closest_Location.py",label="📍 Closest Location")
    st.sidebar.page_link("pages/3_Top_Cities.py",      label="🏙️ Top Cities")

    st.sidebar.markdown(
        """
        <div style="
            position: fixed;
            bottom: 2rem;
            width: 220px;
            background: rgba(0,112,74,0.15);
            border: 1px solid rgba(0,112,74,0.3);
            border-radius: 10px;
            padding: 12px 14px;
            text-align: center;
        ">
            <div style="font-size:1.4rem">☕</div>
            <div style="color:#CBA258; font-size:0.75rem; font-style:italic; margin-top:4px;">
                "But first, coffee."
            </div>
            <div style="color:#888; font-size:0.65rem; margin-top:6px;">
                CS230 Final Project
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )