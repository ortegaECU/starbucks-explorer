"""
4_Ciudades.py
-------------
Page 4: Which cities have the most Starbucks in a given country?
User selects a country and sees a ranked bar chart of top cities,
plus a summary of the #1 city.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils import (load_data, apply_sidebar_style, get_country_list,
                   filter_by_country, STARBUCKS_GREEN, BACKGROUND_DARK)

# -- Page config ---------------------------------------------------------------
st.set_page_config(page_title="Top Cities - Starbucks Explorer",
                   page_icon="🏙️", layout="wide")
apply_sidebar_style()   # #[FUNCCALL2]

# -- Load data -----------------------------------------------------------------
df = load_data()        # #[FUNCCALL2]

# -- Sidebar -------------------------------------------------------------------
with st.sidebar:
    st.title("🏙️ Top Cities")
    st.markdown("---")

    # #[ST1] - country dropdown
    country_list = get_country_list(df)
    selected_country = st.selectbox(
        "Select a Country:",
        options = country_list,
        index   = country_list.index("US"),
    )

    # #[ST2] - slider for how many cities to show
    top_n = st.slider(
        "How many cities to show?",
        min_value = 5,
        max_value = 25,
        value     = 10,
        step      = 1,
    )

    st.markdown("---")

    # #[ST3] - sort order toggle
    sort_order = st.radio(
        "Sort order:",
        options = ["Most stores first", "Least stores first"],
        index   = 0,
    )

    show_table = st.toggle("Show data table", value=False)

# -- Filter & process ----------------------------------------------------------
country_df = filter_by_country(df, selected_country)              # #[FILTER1]

# Count stores per city and sort                                   #[SORT]
city_counts = (
    country_df.groupby("City")
    .size()
    .reset_index(name="Number of Stores")
    .sort_values("Number of Stores",
                 ascending=(sort_order == "Least stores first"))
)

top_cities = city_counts.head(top_n)                              # #[FILTER1]

# Max and min city                                                 #[MAXMIN]
top_city    = city_counts.iloc[0]
bottom_city = city_counts.iloc[-1]

# -- Page header ---------------------------------------------------------------
st.markdown(f"# 🏙️ Top {top_n} Cities in {selected_country}")
st.markdown(
    f"Which cities have the most Starbucks in **{selected_country}**? "
    f"Use the sidebar to adjust the ranking and number of cities shown."
)

# -- Stat callouts -------------------------------------------------------------
total_cities = city_counts[city_counts["Number of Stores"] > 0].shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("🥇 City with Most Stores",
            top_city["City"],
            f"{top_city['Number of Stores']:,} stores")
col2.metric("Total Cities with Starbucks",
            f"{total_cities:,}")
col3.metric("Total Stores in Country",
            f"{len(country_df):,}")

st.markdown("---")

# -- Horizontal bar chart ------------------------------------------------------  #[CHART1]
ascending_chart = sort_order == "Most stores first"

fig = px.bar(
    top_cities.sort_values("Number of Stores", ascending=ascending_chart),
    x           = "Number of Stores",
    y           = "City",
    orientation = "h",
    color       = "Number of Stores",
    color_continuous_scale = ["#a8d5a2", STARBUCKS_GREEN, BACKGROUND_DARK],
    text        = "Number of Stores",
    title       = f"Top {top_n} Cities by Starbucks Count — {selected_country}",
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
    height              = max(400, top_n * 40),
    margin              = dict(l=10, r=80, t=50, b=30),
)

st.plotly_chart(fig, use_container_width=True)

# -- Leaderboard --------------------------------------------------------------  #[CHART2]
st.markdown("### 🏆 City Leaderboard")
st.markdown("Top cities ranked by number of Starbucks locations.")

scatter_df = city_counts.head(top_n).copy()
max_stores = scatter_df["Number of Stores"].max()   # #[MAXMIN]

# Medal emojis for top 3
medals = {1: "🥇", 2: "🥈", 3: "🥉"}

# Build leaderboard rows                                            #[ITERLOOP]
leaderboard_html = """
<div style="display:flex; flex-direction:column; gap:8px; margin-top:12px;">
"""

for i, (_, row) in enumerate(scatter_df.iterrows(), start=1):
    city   = row["City"]
    count  = int(row["Number of Stores"])
    pct    = count / max_stores * 100
    medal  = medals.get(i, f"<span style='color:#aaa;font-size:0.9rem'>#{i}</span>")

    # Top 3 get a highlighted background
    bg     = "rgba(0,112,74,0.18)" if i <= 3 else "rgba(255,255,255,0.04)"
    border = f"2px solid {STARBUCKS_GREEN}" if i == 1 else "1px solid rgba(255,255,255,0.08)"

    leaderboard_html += f"""
    <div style="
        background: {bg};
        border: {border};
        border-radius: 10px;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
    ">
        <div style="font-size:1.4rem; min-width:36px; text-align:center;">{medal}</div>
        <div style="flex:1;">
            <div style="font-weight:700; font-size:1rem; color:#1E3932;">{city}</div>
            <div style="
                background: #e0e0e0;
                border-radius: 4px;
                height: 7px;
                margin-top: 5px;
                overflow: hidden;
            ">
                <div style="
                    width: {pct:.1f}%;
                    background: linear-gradient(90deg, #00704A, #CBA258);
                    height: 100%;
                    border-radius: 4px;
                "></div>
            </div>
        </div>
        <div style="
            font-size:1.2rem;
            font-weight:800;
            color:#00704A;
            min-width:50px;
            text-align:right;
        ">{count:,}</div>
    </div>
    """

leaderboard_html += "</div>"
import streamlit.components.v1 as components
components.html(leaderboard_html, height=top_n * 75, scrolling=False)

# -- Optional data table -------------------------------------------------------
if show_table:
    st.markdown(f"### Full City Rankings — {selected_country}")

    # Add a rank column                                            #[COLUMNS]
    ranked = city_counts.reset_index(drop=True).copy()
    ranked.index += 1
    ranked.index.name = "Rank"

    # Loop to add percentage column                               #[ITERLOOP]
    pct_list = []
    for count in ranked["Number of Stores"]:
        pct_list.append(f"{count / len(country_df) * 100:.1f}%")
    ranked["% of Country Total"] = pct_list

    st.dataframe(ranked, use_container_width=True)