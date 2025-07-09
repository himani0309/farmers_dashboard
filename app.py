
# updated version 3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
}

# === Sidebar Controls ===
st.sidebar.markdown("### 🗌️ Select Region")
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
st.markdown(f"*Yield in {year}:* {current_yield:.2f} tons/ha")
st.markdown(f"*Category:* {status}")

# === Section 2: Climate Warning ===
st.subheader("🌦️ Climate Warnings (Monsoon Months)")
monsoon_cols = [f"precip_flux_{m}" for m in month_nums]
past_years = df[df['year'].between(year-5, year-1)]
current_vals = df_year[monsoon_cols].values.flatten()
past_avg = past_years[monsoon_cols].mean().values
deviation = abs(current_vals - past_avg) / (past_avg + 1e-5)

if (deviation > 0.25).any():
    st.markdown("🚨 *Warning:* Significant deviation in monsoon climate detected!")
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


# === Section 4: Rainfall Pie Chart ===
# === Section 4: Rainfall Pie Chart + Comparison Tables ===
# st.subheader("🌧️ Seasonal Rainfall Distribution")

# # Define seasonal months
# season_months = {
#     "Monsoon": ['6', '7', '8', '9'],
#     "Post-monsoon": ['10', '11']
# }

# # Current year rainfall per season
# rainfall_distribution = {}
# total_rain = 0
# for season, months_list in season_months.items():
#     total = df_year[[f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df_year.columns]].values[0].sum()
#     rainfall_distribution[season] = total
#     total_rain += total

# # Convert to percentage
# current_percent = {season: (rainfall_distribution[season] / total_rain) * 100 for season in rainfall_distribution}

# # --- Pie Chart ---
# labels = list(current_percent.keys())
# values = [round(v, 1) for v in current_percent.values()]
# fig_pie = go.Figure(data=[go.Pie(
#     labels=labels, values=values,
#     textinfo="label+percent",
#     marker=dict(colors=['#0074D9', '#2ECC40'])
# )])
# fig_pie.update_layout(title="💧 Rainfall Season-wise Share")
# st.plotly_chart(fig_pie, use_container_width=True)

# # --- Year-over-Year Table (Previous Year vs Current Year) ---
# left_table = None
# if year > df['year'].min():
#     prev_year_df = df[df['year'] == year - 1]
#     left_table = []
#     for season, months_list in season_months.items():
#         cols = [f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df.columns]
#         prev_total = prev_year_df[cols].values[0].sum()
#         prev_percent = (prev_total / prev_year_df[[f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]].values[0].sum()) * 100
#         curr = current_percent[season]
#         change = curr - prev_percent
#         icon = "📈" if change > 1 else "📉" if change < -1 else "➡️"
#         left_table.append({
#             "Season": season,
#             f"{year - 1} (%)": f"{prev_percent:.1f}%",
#             f"Change": f"{change:+.1f}%",
#             "Trend": icon
#         })

# # --- Cumulative Average Table (1981 to Y-1 vs Y) ---
# right_table = None
# if year > df['year'].min() + 1:
#     past_years_df = df[df['year'].between(df['year'].min(), year - 1)]
#     right_table = []
#     for season, months_list in season_months.items():
#         season_cols = [f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df.columns]
#         all_cols = [f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]
#         seasonal_sum = past_years_df[season_cols].sum(axis=1)
#         total_sum = past_years_df[all_cols].sum(axis=1)
#         cumulative_percent = (seasonal_sum / total_sum).mean() * 100
#         curr = current_percent[season]
#         change = curr - cumulative_percent
#         icon = "📈" if change > 1 else "📉" if change < -1 else "➡️"
#         right_table.append({
#             "Season": season,
#             "Avg (1981–{})".format(year - 1): f"{cumulative_percent:.1f}%",
#             f"{year} (%)": f"{curr:.1f}%",
#             "Change": f"{change:+.1f}%",
#             "Trend": icon
#         })

# # Display the comparison tables
# if left_table or right_table:
#     st.markdown("### 📊 Rainfall Trend Comparison")
#     col1, col2 = st.columns(2)
#     with col1:
#         if left_table:
#             st.markdown(f"**📅 {year-1} → {year} Comparison**")
#             st.table(pd.DataFrame(left_table))
#     with col2:
#         if right_table:
#             st.markdown(f"**📈 Cumulative Trend (1981 → {year})**")
#             st.table(pd.DataFrame(right_table))

# === Section 4: Rainfall Pie Chart + Comparison Tables ===
st.subheader("🌧️ Seasonal Rainfall Distribution")

season_months = {
    "Monsoon": ['6', '7', '8', '9'],
    "Post-monsoon": ['10', '11']
}

# --- Current Year Rainfall ---
rainfall_distribution = {}
total_rain = 0
for season, months_list in season_months.items():
    total = df_year[[f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df_year.columns]].values[0].sum()
    rainfall_distribution[season] = total
    total_rain += total

current_percent = {s: (rainfall_distribution[s] / total_rain) * 100 for s in rainfall_distribution}

# --- Pie Chart ---
labels = list(current_percent.keys())
values = [round(v, 1) for v in current_percent.values()]
fig_pie = go.Figure(data=[go.Pie(
    labels=labels, values=values,
    textinfo="label+percent",
    marker=dict(colors=['#0074D9', '#2ECC40'])
)])
fig_pie.update_layout(title="💧 Rainfall Season-wise Share")
st.plotly_chart(fig_pie, use_container_width=True)

# --- Previous Year Comparison Table ---
left_table_df, right_table_df = None, None
if year > df['year'].min():
    prev_year_df = df[df['year'] == year - 1]
    left_table = []
    for season, months_list in season_months.items():
        cols = [f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df.columns]
        prev_total = prev_year_df[cols].values[0].sum()
        prev_percent = (prev_total / prev_year_df[[f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]].values[0].sum()) * 100
        curr = current_percent[season]
        change = curr - prev_percent
        icon = "📈" if change > 1 else "📉" if change < -1 else "➡️"
        left_table.append({
            "Season": season,
            f"{year - 1} (%)": f"{prev_percent:.1f}%",
            f"Change": f"{change:+.1f}%",
            "Trend": icon
        })
    left_table_df = pd.DataFrame(left_table)

# --- Cumulative Trend from 1981 to Y-1 ---
if year > df['year'].min() + 1:
    past_years_df = df[df['year'].between(df['year'].min(), year - 1)]
    right_table = []
    for season, months_list in season_months.items():
        season_cols = [f"precip_flux_{m}" for m in months_list if f"precip_flux_{m}" in df.columns]
        all_cols = [f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]
        seasonal_sum = past_years_df[season_cols].sum(axis=1)
        total_sum = past_years_df[all_cols].sum(axis=1)
        cumulative_percent = (seasonal_sum / total_sum).mean() * 100
        curr = current_percent[season]
        change = curr - cumulative_percent
        icon = "📈" if change > 1 else "📉" if change < -1 else "➡️"
        right_table.append({
            "Season": season,
            "Avg (1981–{})".format(year - 1): f"{cumulative_percent:.1f}%",
            f"{year} (%)": f"{curr:.1f}%",
            "Change": f"{change:+.1f}%",
            "Trend": icon
        })
    right_table_df = pd.DataFrame(right_table)

# --- Display Both Tables ---
if left_table_df is not None or right_table_df is not None:
    st.markdown("### 📊 Rainfall Trend Comparison")
    col1, col2 = st.columns(2)
    with col1:
        if left_table_df is not None:
            st.markdown(f"**📅 {year-1} → {year} Comparison**")
            st.dataframe(left_table_df.style.applymap(
                lambda x: "color: green" if isinstance(x, str) and '+' in x else ("color: red" if '-' in x else "")
                , subset=["Change"]
            ))
    with col2:
        if right_table_df is not None:
            st.markdown(f"**📈 Cumulative Trend (1981 → {year})**")
            st.dataframe(right_table_df.style.applymap(
                lambda x: "color: green" if isinstance(x, str) and '+' in x else ("color: red" if '-' in x else "")
                , subset=["Change"]
            ))

# --- Optional: Download CSV ---
if left_table_df is not None and right_table_df is not None:
    csv_name = f"rainfall_trend_comparison_{year}.xlsx"
    with pd.ExcelWriter(csv_name, engine='xlsxwriter') as writer:
        left_table_df.to_excel(writer, index=False, sheet_name='Yearly Comparison')
        right_table_df.to_excel(writer, index=False, sheet_name='Cumulative Trend')
    with open(csv_name, "rb") as f:
        st.download_button("📁 Download Rainfall Trend (Excel)", data=f, file_name=csv_name)

# --- Optional: Monsoon % Line Plot over Years ---
st.markdown("### 📈 Monsoon Share Trend Over Years")
monsoon_series = []
post_series = []
years_all = sorted(df['year'].unique())
for y in years_all:
    df_y = df[df['year'] == y]
    mon = df_y[[f"precip_flux_{m}" for m in ['6','7','8','9'] if f"precip_flux_{m}" in df.columns]].values[0].sum()
    post = df_y[[f"precip_flux_{m}" for m in ['10','11'] if f"precip_flux_{m}" in df.columns]].values[0].sum()
    total = mon + post
    monsoon_series.append((y, (mon/total)*100))
    post_series.append((y, (post/total)*100))

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=[y for y,_ in monsoon_series], y=[p for _,p in monsoon_series], name="Monsoon %", mode="lines+markers", line=dict(color='blue')))
fig_line.add_trace(go.Scatter(x=[y for y,_ in post_series], y=[p for _,p in post_series], name="Post-monsoon %", mode="lines+markers", line=dict(color='green')))
fig_line.update_layout(title="🌧️ Monsoon vs Post-monsoon % Trend", xaxis_title="Year", yaxis_title="Percent of Seasonal Rainfall", height=400)
st.plotly_chart(fig_line, use_container_width=True)


# === Section 5: Yield vs District Avg (Baseline) ===
st.subheader("🌾 Yield Comparison with District Average")
st.markdown("*District Average based on 2015–2019 period*")
baseline_years = df[df['year'].between(2015, 2019)]
district_avg_yield = baseline_years['yield'].mean()
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=["Your Yield"], y=[current_yield], name="Your Yield", marker_color="green"))
fig_bar.add_trace(go.Bar(x=["District Avg (2015–2019)"], y=[district_avg_yield], name="District Avg", marker_color="gray"))
fig_bar.update_layout(barmode="group", yaxis_title="tons/ha", title="📈 Your Yield vs District Baseline Avg", height=400)
st.plotly_chart(fig_bar, use_container_width=True)

# === Section 6: Emoji Rainfall Cards ===
st.subheader("🗓️ Monthly Rainfall Status")
emoji_table = []

for m in month_nums:
    col = f"precip_flux_{m}"
    if col not in df_year.columns or f"precip_flux_{m}" not in baseline_years.columns:
        continue

    # Safe indexing: ensure m is between '6' and '12'
    month_idx = int(m) - 6
    if 0 <= month_idx < len(months):
        month_label = months[month_idx]
    else:
        month_label = f"Month {m}"  # fallback label

    curr = df_year[col].values[0]
    avg = baseline_years[col].mean()
    deviation = (curr - avg) / (avg + 1e-5)

    if deviation < -0.2:
        emoji = "❌ Low"
    elif deviation > 0.2:
        emoji = "☔ High"
    else:
        emoji = "✅ Normal"

    emoji_table.append((month_label, f"{curr:.1f} mm", emoji))

st.table(pd.DataFrame(emoji_table, columns=["Month", "Rainfall", "Status"]))

# === Section 7: Temperature vs Average Line Plot ===
st.subheader("🌡️ Temperature vs Average (June–Dec)")
temp_cols = [f"temp_{m}" for m in month_nums if f"temp_{m}" in df.columns]
temp_curr = df_year[temp_cols].values.flatten()
temp_avg = baseline_years[temp_cols].mean().values
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=months, y=temp_curr, name=f"{year} Temperature", mode="lines+markers", line=dict(color="red")))
fig_temp.add_trace(go.Scatter(x=months, y=temp_avg, name="2015–2019 Avg", mode="lines+markers", line=dict(color="gray", dash="dot")))
fig_temp.update_layout(title="🌡️ Monthly Temperature Comparison", xaxis_title="Month", yaxis_title="Temperature (°C)", height=400)
st.plotly_chart(fig_temp, use_container_width=True)

# === Section 8: Accumulated Rainfall Line Plot ===
st.subheader("📈 Accumulated Rainfall Comparison")
curr_rain = df_year[[f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]].values.flatten()
avg_rain = baseline_years[[f"precip_flux_{m}" for m in month_nums if f"precip_flux_{m}" in df.columns]].mean().values
fig_acc = go.Figure()
fig_acc.add_trace(go.Scatter(x=months, y=pd.Series(curr_rain).cumsum(), mode="lines+markers", name="Current Year"))
fig_acc.add_trace(go.Scatter(x=months, y=pd.Series(avg_rain).cumsum(), mode="lines+markers", name="2015–2019 Avg", line=dict(dash="dash")))
fig_acc.update_layout(title="🌧️ Accumulated Rainfall (June–Dec)", xaxis_title="Month", yaxis_title="Cumulative Rainfall (mm)", height=400)
st.plotly_chart(fig_acc, use_container_width=True)

# === Section 9: Seasonal Rainfall Bar + Bullet Chart ===
st.subheader("📊 Seasonal Rainfall — Bar & Bullet Charts")
monsoon_sum = df_year[[f"precip_flux_{m}" for m in ['6', '7', '8', '9']]].sum(axis=1).values[0]
post_sum = df_year[[f"precip_flux_{m}" for m in ['10', '11']]].sum(axis=1).values[0]
monsoon_avg = baseline_years[[f"precip_flux_{m}" for m in ['6', '7', '8', '9']]].mean().sum()
post_avg = baseline_years[[f"precip_flux_{m}" for m in ['10', '11']]].mean().sum()
fig_bar = go.Figure()
fig_bar.add_bar(x=["Monsoon"], y=[monsoon_sum], name=f"{year} Monsoon", marker_color="blue")
fig_bar.add_bar(x=["Monsoon"], y=[monsoon_avg], name="Avg (2015–2019)", marker_color="lightblue")
fig_bar.add_bar(x=["Post-monsoon"], y=[post_sum], name=f"{year} Post-monsoon", marker_color="green")
fig_bar.add_bar(x=["Post-monsoon"], y=[post_avg], name="Avg (2015–2019)", marker_color="lightgreen")
fig_bar.update_layout(barmode="group", title="📊 Total Rainfall per Season", yaxis_title="Rainfall (mm)", height=400)
st.plotly_chart(fig_bar, use_container_width=True)
fig_bullet = go.Figure()
fig_bullet.add_trace(go.Indicator(
    mode = "number+gauge+delta",
    value = monsoon_sum,
    domain = {'x': [0.1, 1], 'y': [0, 1]},
    title = {'text': "Monsoon Rainfall vs Avg (mm)"},
    delta = {'reference': monsoon_avg},
    gauge = {
        'shape': "bullet",
        'axis': {'range': [None, max(monsoon_sum, monsoon_avg) + 200]},
        'threshold': {
            'line': {'color': "red", 'width': 2},
            'thickness': 0.75,
            'value': monsoon_avg
        },
        'bar': {'color': "blue"}
    }
))
fig_bullet.update_layout(height=200)
st.plotly_chart(fig_bullet, use_container_width=True)
# === Section 10: Climate Comparison: [Selected Year] vs 2015–2019 Avg (Bar Plots) ===
st.subheader(f"📊 Climate Comparison: {year} vs Avg (Bar Plots)")

baseline_df = df[df['year'].between(2015, 2019)]
current_df = df[df['year'] == year]

col1, col2 = st.columns(2)
plot_cols = list(var_prefix_map.keys())

for i, prefix in enumerate(plot_cols):
    avg_vals = []
    current_vals = []

    for m in month_nums:
        col_name = f"{prefix}_{m}"
        if col_name in df.columns:
            avg_vals.append(baseline_df[col_name].mean())
            current_vals.append(current_df[col_name].values[0])

    fig = go.Figure()
    fig.add_bar(x=months, y=avg_vals, name="2015–2019 Avg", marker_color='gray')
    fig.add_bar(x=months, y=current_vals, name=f"{year}", marker_color='orange')

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


# === Section 11: Min Temperature vs Average Line Plot ===
st.subheader("❄️ Min Temperature vs Average (June–Dec)")
tmin_cols = [f"tmin_{m}" for m in month_nums if f"tmin_{m}" in df.columns]
tmin_curr = df_year[tmin_cols].values.flatten()
tmin_avg = baseline_years[tmin_cols].mean().values

fig_tmin = go.Figure()
fig_tmin.add_trace(go.Scatter(x=months, y=tmin_curr, name=f"{year} Min Temp", mode="lines+markers", line=dict(color="blue")))
fig_tmin.add_trace(go.Scatter(x=months, y=tmin_avg, name="2015–2019 Avg", mode="lines+markers", line=dict(color="gray", dash="dot")))

fig_tmin.update_layout(title="❄️ Monthly Min Temperature Comparison", xaxis_title="Month", yaxis_title="Min Temp (°C)", height=400)
st.plotly_chart(fig_tmin, use_container_width=True)


# === Section 12: Max Temperature vs Average Line Plot ===
st.subheader("🔥 Max Temperature vs Average (June–Dec)")
tmax_cols = [f"tmax_{m}" for m in month_nums if f"tmax_{m}" in df.columns]
tmax_curr = df_year[tmax_cols].values.flatten()
tmax_avg = baseline_years[tmax_cols].mean().values

fig_tmax = go.Figure()
fig_tmax.add_trace(go.Scatter(x=months, y=tmax_curr, name=f"{year} Max Temp", mode="lines+markers", line=dict(color="orange")))
fig_tmax.add_trace(go.Scatter(x=months, y=tmax_avg, name="2015–2019 Avg", mode="lines+markers", line=dict(color="gray", dash="dot")))

fig_tmax.update_layout(title="🔥 Monthly Max Temperature Comparison", xaxis_title="Month", yaxis_title="Max Temp (°C)", height=400)
st.plotly_chart(fig_tmax, use_container_width=True)

from fpdf import FPDF
import os

st.subheader("📄 Farmer-Friendly Summary Report")
st.markdown("Generate a simple summary PDF in easy language for farmers to understand trends in climate and yield.")

# === Section 13: Farmer-Friendly Summary Report ===
import os
from fpdf import FPDF
import unicodedata

st.subheader("📄 Farmer-Friendly Summary Report")
st.markdown("Generate a simple summary PDF in easy language for farmers to understand trends in climate and yield.")

# 🧹 Full Unicode Cleaner (Safe for FPDF)
def clean_for_pdf(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if ord(c) < 128 and not unicodedata.combining(c))

# 📝 Summary Text Generator
def generate_summary_text(df_year, df_prev, year, district):
    lines = []

    yield_val = df_year["yield"].values[0]
    lines.append(f"This year ({year}), the crop yield in {district} is {yield_val:.2f} tons per hectare.")

    monsoon_cols = [f"precip_flux_{m}" for m in ['6', '7', '8', '9']]
    post_cols = [f"precip_flux_{m}" for m in ['10', '11']]

    monsoon_curr = df_year[monsoon_cols].values[0].sum()
    post_curr = df_year[post_cols].values[0].sum()

    if df_prev is not None:
        monsoon_prev = df_prev[monsoon_cols].values[0].sum()
        post_prev = df_prev[post_cols].values[0].sum()
        change_monsoon = monsoon_curr - monsoon_prev
        change_post = post_curr - post_prev

        monsoon_msg = "increased" if change_monsoon > 0 else "decreased"
        post_msg = "increased" if change_post > 0 else "decreased"

        lines.append(f"Monsoon rainfall has {monsoon_msg} by {abs(change_monsoon):.1f} mm compared to last year.")
        lines.append(f"Post-monsoon rainfall has {post_msg} by {abs(change_post):.1f} mm.")
    else:
        lines.append("No previous year data available for rainfall comparison.")

    temp_cols = [f"temp_{m}" for m in ['6', '7', '8', '9', '10', '11', '12']]
    temp_avg = df_year[temp_cols].mean(axis=1).values[0]
    lines.append(f"The average temperature this season was around {temp_avg:.1f}°C.")

    if yield_val < 2:
        lines.append("Yield is low. Try consulting experts and check irrigation or fertilizer issues.")
    elif yield_val < 3:
        lines.append("Yield is average. Keep monitoring rainfall and temperature closely.")
    else:
        lines.append("Good yield! Weather conditions seem favorable this season.")

    lines.append("This is an automated summary to help you understand your farming season better.")
    return "\n\n".join(lines)

# 📄 PDF Generator
def generate_pdf_summary(df, df_year, year, district, selected_state):
    df_prev = df[df['year'] == year - 1] if year > df['year'].min() else None
    summary_text = generate_summary_text(df_year, df_prev, year, district)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=16)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.cell(0, 10, f"Farmer Summary Report – {district}, {selected_state} – {year}", ln=True)

    pdf.set_font("Arial", size=12)
    for line in summary_text.split("\n"):
        clean_line = clean_for_pdf(line)
        pdf.multi_cell(0, 10, clean_line)

    filename = f"{district}_{year}_summary.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button(
            label="📥 Download Summary PDF",
            data=f,
            file_name=filename,
            mime="application/pdf"
        )

    os.remove(filename)

# 🧭 Show Button
if st.button("📄 Generate PDF Summary"):
    generate_pdf_summary(df, df_year, year, district, selected_state)
