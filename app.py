# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import os
# from PIL import Image

# # === Configuration ===
# st.set_page_config(page_title="Farmer Climate + Yield Dashboard", layout="wide")

# @st.cache_data
# def load_data():
#     xls = pd.ExcelFile("Final_version_Monthly_District_Data.xlsx")
#     return {sheet: xls.parse(sheet).dropna() for sheet in xls.sheet_names}

# data = load_data()

# # === Sidebar Controls ===
# district = st.sidebar.selectbox("Select District", list(data.keys()))
# df = data[district]

# years = sorted(df["year"].unique())
# year = st.sidebar.selectbox("Select Year", years)

# # === Month & Variables ===
# months = ['June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
# month_nums = ['6', '7', '8', '9', '10', '11', '12']
# var_prefix_map = {
#     "temp": "Temperature (°C)",
#     "humidity": "Humidity (%)",
#     "et0": "ET₀ (mm/day)",
#     "precip_frac": "Precipitation Fraction",
#     "precip_flux": "Rainfall (mm/day)",
#     "tmax": "Max Temp (°C)",
#     "tmin": "Min Temp (°C)"
# }

# df_year = df[df["year"] == year]

# # === Yield Status ===
# yield_series = df['yield']
# q25, q75 = yield_series.quantile(0.25), yield_series.quantile(0.75)
# current_yield = df_year['yield'].values[0]
# status = "🟢 Good" if current_yield >= q75 else "🔴 Risk" if current_yield <= q25 else "🟡 Moderate"

# # === Title ===
# st.markdown(f"## 🌾 {district} — Farmer Dashboard for {year}")

# # === Section 1: Yield Status ===
# st.subheader("📊 Yield Status")
# st.markdown(f"**Yield in {year}:** {current_yield:.2f} tons/ha")
# st.markdown(f"**Category:** {status}")

# # === Section 2: Climate Warning ===
# st.subheader("🌦️ Climate Warnings (Monsoon Months)")
# monsoon_cols = [f"precip_flux_{m}" for m in month_nums]
# past_years = df[df['year'].between(year-5, year-1)]
# current_vals = df_year[monsoon_cols].values.flatten()
# past_avg = past_years[monsoon_cols].mean().values
# deviation = abs(current_vals - past_avg) / (past_avg + 1e-5)

# if (deviation > 0.25).any():
#     st.markdown("🚨 **Warning:** Significant deviation in monsoon climate detected!")
# else:
#     st.markdown("✅ No abnormal weather during monsoon months.")

# # === Section 3: Line Plot for All Variables ===
# st.subheader("📈 Monsoon Climate Trend (June–Dec)")

# fig = go.Figure()
# for prefix, label in var_prefix_map.items():
#     cols = [f"{prefix}_{m}" for m in month_nums if f"{prefix}_{m}" in df.columns]
#     if not cols: continue
#     values = df_year[cols].values.flatten()
#     fig.add_trace(go.Scatter(x=months[:len(values)], y=values, mode="lines+markers", name=label))

# fig.add_trace(go.Scatter(
#     x=months, y=[current_yield]*len(months),
#     mode="lines", name=f"Yield: {current_yield:.2f} tons/ha",
#     line=dict(dash='dash', color='green'), yaxis='y2'
# ))

# fig.update_layout(
#     title=f"📉 Climate Variables Trend (June–Dec) – {district}, {year}",
#     xaxis_title="Month",
#     yaxis=dict(title="Climate Value"),
#     yaxis2=dict(title="Yield (tons/ha)", overlaying='y', side='right', showgrid=False, tickfont=dict(color="green")),
#     legend=dict(orientation="v"), height=600
# )
# st.plotly_chart(fig, use_container_width=True)

# # === Section 4: Dynamic Interactive Bar Plots ===
# st.subheader("📊 Climate Comparison: 2020 vs Avg (Bar Plots)")

# # Reusable month labels
# months = ['June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
# month_nums = ['6', '7', '8', '9', '10', '11', '12']

# recent_year = 2020
# past_df = df[df['year'].between(recent_year - 5, recent_year - 1)]
# current_df = df[df['year'] == recent_year]

# col1, col2 = st.columns(2)
# plot_cols = list(var_prefix_map.keys())

# for i, prefix in enumerate(plot_cols):
#     avg_vals = []
#     current_vals = []

#     for m in month_nums:
#         col_name = f"{prefix}_{m}"
#         if col_name in df.columns:
#             avg_vals.append(past_df[col_name].mean())
#             current_vals.append(current_df[col_name].values[0])

#     fig = go.Figure()
#     fig.add_bar(x=months, y=avg_vals, name="2015–2019 Avg", marker_color='gray')
#     fig.add_bar(x=months, y=current_vals, name=f"{recent_year}", marker_color='orange')

#     fig.update_layout(
#         barmode="group",
#         title=f"{var_prefix_map[prefix]} – {district}",
#         xaxis_title="Month",
#         yaxis_title=var_prefix_map[prefix],
#         height=400,
#         legend=dict(orientation="h")
#     )

#     with [col1, col2][i % 2]:
#         st.plotly_chart(fig, use_container_width=True)













import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from PIL import Image

# === Configuration ===
st.set_page_config(page_title="Farmer Climate + Yield Dashboard", layout="wide")

@st.cache_data
def load_data():
    xls = pd.ExcelFile("Final_version_Monthly_District_Data.xlsx")
    return {sheet: xls.parse(sheet).dropna() for sheet in xls.sheet_names}

data = load_data()

# === Dummy State-to-District Mapping ===
state_district_map = {
    "Assam": list(data.keys())
    # You can later add: "Bihar": [...], "UP": [...], etc.
}

# === Sidebar Controls ===
st.sidebar.markdown("### 🗺️ Select Region")
selected_state = st.sidebar.selectbox("Select State", list(state_district_map.keys()))
district = st.sidebar.selectbox("Select District", state_district_map[selected_state])

df = data[district]
years = sorted(df["year"].unique())
year = st.sidebar.selectbox("Select Year", years)

# === Month & Variables ===
months = ['June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
month_nums = ['6', '7', '8', '9', '10', '11', '12']
var_prefix_map = {
    "temp": "Temperature (°C)",
    "humidity": "Humidity (%)",
    "et0": "ET₀ (mm/day)",
    "precip_frac": "Precipitation Fraction",
    "precip_flux": "Rainfall (mm/day)",
    "tmax": "Max Temp (°C)",
    "tmin": "Min Temp (°C)"
}

df_year = df[df["year"] == year]

# === Yield Status ===
yield_series = df['yield']
q25, q75 = yield_series.quantile(0.25), yield_series.quantile(0.75)
current_yield = df_year['yield'].values[0]
status = "🟢 Good" if current_yield >= q75 else "🔴 Risk" if current_yield <= q25 else "🟡 Moderate"

# === Title ===
st.markdown(f"## 🌾 {district}, {selected_state} — Farmer Dashboard for {year}")

# === Section 1: Yield Status ===
st.subheader("📊 Yield Status")
st.markdown(f"**Yield in {year}:** {current_yield:.2f} tons/ha")
st.markdown(f"**Category:** {status}")

# === Section 2: Climate Warning ===
st.subheader("🌦️ Climate Warnings (Monsoon Months)")
monsoon_cols = [f"precip_flux_{m}" for m in month_nums]
past_years = df[df['year'].between(year-5, year-1)]
current_vals = df_year[monsoon_cols].values.flatten()
past_avg = past_years[monsoon_cols].mean().values
deviation = abs(current_vals - past_avg) / (past_avg + 1e-5)

if (deviation > 0.25).any():
    st.markdown("🚨 **Warning:** Significant deviation in monsoon climate detected!")
else:
    st.markdown("✅ No abnormal weather during monsoon months.")

# === Section 3: Line Plot for All Variables ===
st.subheader("📈 Monsoon Climate Trend (June–Dec)")

fig = go.Figure()
for prefix, label in var_prefix_map.items():
    cols = [f"{prefix}_{m}" for m in month_nums if f"{prefix}_{m}" in df.columns]
    if not cols: continue
    values = df_year[cols].values.flatten()
    fig.add_trace(go.Scatter(x=months[:len(values)], y=values, mode="lines+markers", name=label))

fig.add_trace(go.Scatter(
    x=months, y=[current_yield]*len(months),
    mode="lines", name=f"Yield: {current_yield:.2f} tons/ha",
    line=dict(dash='dash', color='green'), yaxis='y2'
))

fig.update_layout(
    title=f"📉 Climate Variables Trend (June–Dec) – {district}, {year}",
    xaxis_title="Month",
    yaxis=dict(title="Climate Value"),
    yaxis2=dict(title="Yield (tons/ha)", overlaying='y', side='right', showgrid=False, tickfont=dict(color="green")),
    legend=dict(orientation="v"), height=600
)
st.plotly_chart(fig, use_container_width=True)

# === Section 4: Dynamic Interactive Bar Plots ===
st.subheader("📊 Climate Comparison: 2020 vs Avg (Bar Plots)")

recent_year = 2020
past_df = df[df['year'].between(recent_year - 5, recent_year - 1)]
current_df = df[df['year'] == recent_year]

col1, col2 = st.columns(2)
plot_cols = list(var_prefix_map.keys())

for i, prefix in enumerate(plot_cols):
    avg_vals = []
    current_vals = []

    for m in month_nums:
        col_name = f"{prefix}_{m}"
        if col_name in df.columns:
            avg_vals.append(past_df[col_name].mean())
            current_vals.append(current_df[col_name].values[0])

    fig = go.Figure()
    fig.add_bar(x=months, y=avg_vals, name="2015–2019 Avg", marker_color='gray')
    fig.add_bar(x=months, y=current_vals, name=f"{recent_year}", marker_color='orange')

    fig.update_layout(
        barmode="group",
        title=f"{var_prefix_map[prefix]} – {district}",
        xaxis_title="Month",
        yaxis_title=var_prefix_map[prefix],
        height=400,
        legend=dict(orientation="h")
    )

    with [col1, col2][i % 2]:
        st.plotly_chart(fig, use_container_width=True)
