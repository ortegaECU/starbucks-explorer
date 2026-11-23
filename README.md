# ☕ Starbucks Explorer

**An interactive Streamlit web app to explore 25,000+ Starbucks locations around the world.**

Teodoro (Enrique) Ortega · Bentley University · CS230 Final Project

🔗 **Live app:** _add your Streamlit Cloud link here_

---

## What it does

Starbucks Explorer turns a raw dataset of every Starbucks store into an app anyone can use to answer simple questions:

- **Where is Starbucks the biggest?** See which countries have the most stores.
- **Where is the closest Starbucks to me?** Type any address and get the nearest stores on a map.
- **Which cities have the most stores?** Pick a country and rank its top cities.

<!-- Add screenshots here once you take them, for example:
![Home page](screenshots/home.png)
-->

## Pages

| Page | What you can do | Built with |
| --- | --- | --- |
| **Home** | Overview of the dataset with summary metrics | Streamlit |
| **1. Top Countries** | Choose how many countries to compare (slider), see a ranked bar chart and a world map colored by store density | Plotly bar chart, Plotly choropleth, pycountry |
| **2. Closest Location** | Enter an address, choose how many stores to show and filter by ownership type; the app finds the nearest stores and plots them on an interactive map | geopy (ArcGIS geocoder), Haversine distance, PyDeck |
| **3. Top Cities** | Select a country, the number of cities and the sort order; see a ranked table and a pie chart of each city's share | Plotly pie chart, pandas |

## How it works

1. **Data loading and cleaning** (`utils.py`): loads `directory.csv`, converts country codes to full names and caches the data so pages load fast.
2. **Filtering and aggregation:** pandas `groupby` and sorting to count stores by country, state and city.
3. **Distance calculation:** the Haversine formula computes the great-circle distance (km) between the user's address and every store, then returns the closest ones.
4. **Visualization:** Plotly for charts and maps, PyDeck for the interactive store map, custom CSS for the Starbucks-themed sidebar.

## Data

- **Source:** [Starbucks Store Locations — Kaggle](https://www.kaggle.com/datasets/starbucks/store-locations)
- **Size:** 25,600 stores, 13 columns
- **Main fields:** store name, ownership type, city, state/province, country, latitude, longitude

## Run it locally

```bash
git clone https://github.com/ortegaECU/starbucks-explorer.git
cd starbucks-explorer
pip install -r requirements.txt
streamlit run Home.py
```

Then open `http://localhost:8501` in your browser.

You can also open the repo in **GitHub Codespaces**: the dev container installs everything and starts the app automatically.

## Project structure

```
├── Home.py                    # landing page
├── utils.py                   # data loading, filters, shared styling
├── pages/
│   ├── 1_Top_Countries.py
│   ├── 2_Closest_Location.py
│   └── 3_Top_Cities.py
├── directory.csv              # dataset
├── requirements.txt
└── .devcontainer/             # Codespaces setup
```

## Tech stack

Python · Streamlit · pandas · Plotly · PyDeck · geopy · pycountry

## What I learned

- Building a multi-page web app with Streamlit and sharing code between pages
- Working with geographic data: geocoding, distance calculations and maps
- Turning a large raw dataset into charts and filters that a non-technical user can explore
