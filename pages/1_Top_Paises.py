"""
1_Top_Paises.py
---------------
Page 1: Which countries have the most Starbucks locations?
User can adjust the Top N slider to compare different numbers of countries.
"""

import streamlit as st
import plotly.express as px
import pycountry
import pandas as pd
from utils import load_data, apply_sidebar_style, STARBUCKS_GREEN, BACKGROUND_DARK

# -- Page config ---------------------------------------------------------------
st.set_page_config(page_title="Top Countries - Starbucks Explorer",
                   page_icon="🌍", layout="wide")
apply_sidebar_style()   # #[FUNCCALL2]

# -- Load data -----------------------------------------------------------------
df = load_data()        # #[FUNCCALL2]

# -- Sidebar widgets -----------------------------------------------------------
with st.sidebar:
    st.title("🌍 Top Countries")
    st.markdown("---")

    # #[ST2] - slider widget
    top_n = st.slider(
        "How many countries to show?",
        min_value = 5,
        max_value = 30,
        value     = 10,
        step      = 1,
    )

    st.markdown("---")

    # #[ST1] - multiselect to highlight specific countries
    all_countries = df["Country"].value_counts().head(30).index.tolist()
    highlight = st.multiselect(
        "Highlight specific countries:",
        options = all_countries,
        default = ["US", "CN", "CA"],
    )

    st.markdown("---")

    # #[ST3] - toggle to show/hide the world map
    show_map = st.toggle("Show world map", value=True)

# -- Data processing -----------------------------------------------------------

# Count stores per country and sort                                  #[SORT]
country_counts = (
    df["Country"]
    .value_counts()
    .reset_index()
)
country_counts.columns = ["Country", "Number of Stores"]
country_counts = country_counts.sort_values("Number of Stores", ascending=False)

# Take the top N                                                     #[FILTER1]
top_df = country_counts.head(top_n).copy()

# Add a column flagging highlighted countries                        #[COLUMNS]
top_df["Highlighted"] = top_df["Country"].apply(
    lambda c: "Selected" if c in highlight else "Other"
)

# Max and min in the current selection                               #[MAXMIN]
max_country = top_df.iloc[0]
min_country = top_df.iloc[-1]

# -- Page header ---------------------------------------------------------------
st.markdown(f"# 🌍 Top {top_n} Countries by Number of Starbucks")
st.markdown(
    f"The **{top_n} countries** with the most Starbucks locations. "
    f"Use the sidebar slider to adjust how many countries to compare."
)

# -- Stat callouts -------------------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    label = "🥇 Largest Market",
    value = max_country["Country"],
    delta = f"{max_country['Number of Stores']:,} stores",
)
col2.metric(
    label = f"#{top_n} in Ranking",
    value = min_country["Country"],
    delta = f"{min_country['Number of Stores']:,} stores",
)
col3.metric(
    label = "Total in Selection",
    value = f"{top_df['Number of Stores'].sum():,}",
    delta = f"out of {len(df):,} worldwide",
)

st.markdown("---")

# -- Bar chart -----------------------------------------------------------------  #[CHART1]
fig = px.bar(
    top_df.sort_values("Number of Stores", ascending=True),
    x           = "Number of Stores",
    y           = "Country",
    orientation = "h",
    color       = "Number of Stores",
    color_continuous_scale = ["#2d5a27", STARBUCKS_GREEN, "#CBA258"],
    text        = "Number of Stores",
    title       = f"Top {top_n} Countries - Starbucks Store Count",
)

fig.update_traces(
    texttemplate = "%{text:,}",
    textposition = "outside",
)

fig.update_layout(
    plot_bgcolor        = "rgba(0,0,0,0)",
    paper_bgcolor       = "rgba(0,0,0,0)",
    font_color          = "#333333",
    title_font_size     = 18,
    coloraxis_showscale = False,
    xaxis_title         = "Number of Stores",
    yaxis_title         = "",
    height              = max(400, top_n * 38),
    margin              = dict(l=10, r=80, t=50, b=30),
)

st.plotly_chart(fig, use_container_width=True)

# -- Donut chart ---------------------------------------------------------------  #[CHART2]
st.markdown("### Share of Global Stores")
st.markdown(
    f"The top {top_n} countries account for "
    f"**{top_df['Number of Stores'].sum() / len(df) * 100:.1f}%** "
    f"of all Starbucks worldwide."
)

others_count = len(df) - top_df["Number of Stores"].sum()
donut_df = pd.concat([
    top_df[["Country", "Number of Stores"]],
    pd.DataFrame([{"Country": "All Others", "Number of Stores": others_count}])
], ignore_index=True)

fig2 = px.pie(
    donut_df,
    names  = "Country",
    values = "Number of Stores",
    hole   = 0.45,
    title  = f"Global Store Share - Top {top_n} vs Rest of World",
    color_discrete_sequence = px.colors.sequential.Greens_r + ["#cccccc"],
)
fig2.update_traces(textinfo="percent+label")
fig2.update_layout(
    plot_bgcolor    = "rgba(0,0,0,0)",
    paper_bgcolor   = "rgba(0,0,0,0)",
    title_font_size = 16,
    showlegend      = False,
    height          = 450,
)
st.plotly_chart(fig2, use_container_width=True)

# -- World choropleth map ------------------------------------------------------  #[MAP]
if show_map:
    st.markdown("### World Map - Store Density")
    st.markdown(
        "The darker the green, the more Starbucks locations in that country. "
        "Hover over any country to see the exact count."
    )

    # Plotly needs 3-letter ISO codes (USA) but our dataset uses 2-letter (US)
    def to_alpha3(code):
        try:
            return pycountry.countries.get(alpha_2=code).alpha_3
        except:
            return None

    map_df = country_counts.copy()
    map_df["iso_alpha3"] = map_df["Country"].apply(to_alpha3)
    map_df = map_df.dropna(subset=["iso_alpha3"])

    fig3 = px.choropleth(
        map_df,
        locations              = "iso_alpha3",
        color                  = "Number of Stores",
        hover_name             = "Country",
        hover_data             = {"Number of Stores": True, "iso_alpha3": False},
        color_continuous_scale = ["#e8f5e9", "#66bb6a", STARBUCKS_GREEN, BACKGROUND_DARK],
        title                  = "Starbucks Locations by Country",
    )

    fig3.update_layout(
        plot_bgcolor        = "rgba(0,0,0,0)",
        paper_bgcolor       = "rgba(0,0,0,0)",
        title_font_size     = 16,
        geo_bgcolor         = "rgba(0,0,0,0)",
        geo_showframe       = False,
        geo_showcoastlines  = True,
        geo_coastlinecolor  = "#aaaaaa",
        geo_landcolor       = "#f0f0f0",
        geo_projection_type="natural earth",
        coloraxis_colorbar  = dict(title="Stores"),
        height              = 480,
        margin              = dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(fig3, use_container_width=True)