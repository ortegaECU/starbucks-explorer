"""
3_Top_Cities.py
-------------
Page 3: Which cities have the most Starbucks in a given country?
User selects a country and sees a ranked bar chart of top cities,
plus a summary of the #1 city.
Controls moved to main page body so they're always visible.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import streamlit.components.v1 as components
from utils import (load_data, apply_sidebar_style, get_country_list,
                   filter_by_country, STARBUCKS_GREEN, BACKGROUND_DARK)

# -- Page config ---------------------------------------------------------------
st.set_page_config(page_title="Top Cities - Starbucks Explorer",
                   page_icon="🏙️", layout="wide")
apply_sidebar_style()   # #[FUNCCALL2]

# -- Load data -----------------------------------------------------------------
df = load_data()        # #[FUNCCALL2]

# -- Page header ---------------------------------------------------------------
st.markdown("# 🏙️ Top Cities by Number of Starbucks")
st.markdown("Select a country and adjust the controls to explore city rankings.")

st.markdown("---")

# ── Controls in main page (moved from sidebar) ────────────────────────────────
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 2, 1])

with ctrl_col1:
    # #[ST1] - country dropdown
    country_list = get_country_list(df)
    default_country = "United States" if "United States" in country_list else country_list[0]
    selected_country = st.selectbox(
        "Select a Country:",
        options=country_list,
        index=country_list.index(default_country),
    )

with ctrl_col2:
    # #[ST2] - slider for how many cities to show
    top_n = st.slider(
        "Cities to show:",
        min_value=5,
        max_value=25,
        value=10,
        step=1,
    )

with ctrl_col3:
    # #[ST3] - sort order radio
    sort_order = st.radio(
        "Sort order:",
        options=["Most stores first", "Least stores first"],
        index=0,
    )

with ctrl_col4:
    show_table = st.toggle("Show table", value=False)

st.markdown("---")

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
top_city = city_counts.iloc[0]
bottom_city = city_counts.iloc[-1]

# -- Page subheader -----------------------------------------------------------
st.markdown(f"## Top {top_n} Cities in {selected_country}")
st.markdown(
    f"Which cities have the most Starbucks in **{selected_country}**?"
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

# -- Leaderboard (first) -------------------------------------------------------  #[CHART1]
st.markdown("### 🏆 City Leaderboard")
st.markdown("Top cities ranked by number of Starbucks locations.")

scatter_df = city_counts.head(top_n).copy()
max_stores = scatter_df["Number of Stores"].max()   # #[MAXMIN]

medals = {1: "🥇", 2: "🥈", 3: "🥉"}

# Build leaderboard rows                                            #[ITERLOOP]
leaderboard_html = """
<div style="display:flex; flex-direction:column; gap:8px; margin-top:12px;">
"""

for i, (_, row) in enumerate(scatter_df.iterrows(), start=1):
    city = row["City"]
    count = int(row["Number of Stores"])
    pct = count / max_stores * 100
    medal = medals.get(i, f"<span style='color:#aaa;font-size:0.9rem'>#{i}</span>")

    bg = "rgba(0,112,74,0.18)" if i <= 3 else "rgba(255,255,255,0.04)"
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
components.html(leaderboard_html, height=top_n * 75, scrolling=False)

# -- Pie chart (second) --------------------------------------------------------  #[CHART2]
st.markdown("### Share of Stores by City")
st.markdown(
    f"What percentage of all Starbucks in **{selected_country}** belong to each city?"
)

others_count = len(country_df) - top_cities["Number of Stores"].sum()
pie_df = pd.concat([
    top_cities[["City", "Number of Stores"]],
    pd.DataFrame([{"City": "All Others", "Number of Stores": others_count}])
], ignore_index=True)

fig_pie = px.pie(
    pie_df,
    names="City",
    values="Number of Stores",
    hole=0.45,
    title=f"Store Share by City — {selected_country}",
    color_discrete_sequence=px.colors.sequential.Greens_r + ["#cccccc"],
)
fig_pie.update_traces(textinfo="percent+label")
fig_pie.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    title_font_size=16,
    showlegend=False,
    height=480,
)
st.plotly_chart(fig_pie, use_container_width=True)

# -- Optional data table -------------------------------------------------------
if show_table:
    st.markdown(f"### Full City Rankings — {selected_country}")

    ranked = city_counts.reset_index(drop=True).copy()   # #[COLUMNS]
    ranked.index += 1
    ranked.index.name = "Rank"

    pct_list = []                                         # #[ITERLOOP]
    for count in ranked["Number of Stores"]:
        pct_list.append(f"{count / len(country_df) * 100:.1f}%")
    ranked["% of Country Total"] = pct_list

    st.dataframe(ranked, use_container_width=True)