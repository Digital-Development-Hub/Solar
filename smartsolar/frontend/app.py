"""
Solar Energy Forecasting — Streamlit Frontend
==============================================
Connects to FastAPI backend at http://localhost:8000/predict
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solar Energy Forecaster",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --sun: #F5A623;
    --amber: #E8820C;
    --deep: #0D1117;
    --card: #161B22;
    --border: #30363D;
    --text: #E6EDF3;
    --muted: #8B949E;
    --green: #3FB950;
    --blue: #58A6FF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--deep);
    color: var(--text);
}

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #F5A623 0%, #FF6B35 50%, #F5A623 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.1;
}

.subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: var(--muted);
    margin-top: 0.3rem;
    margin-bottom: 2rem;
    font-weight: 300;
}

.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #F5A623, #FF6B35);
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #F5A623;
    margin: 0.3rem 0;
}

.metric-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

.metric-unit {
    font-size: 0.85rem;
    color: var(--muted);
}

.forecast-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.hour-badge {
    background: linear-gradient(135deg, #F5A623, #FF6B35);
    color: #0D1117;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 0.9rem;
    padding: 0.4rem 0.9rem;
    border-radius: 8px;
    white-space: nowrap;
    min-width: 50px;
    text-align: center;
}

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
    border-left: 3px solid #F5A623;
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

.info-box {
    background: rgba(245, 166, 35, 0.08);
    border: 1px solid rgba(245, 166, 35, 0.25);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: var(--muted);
    margin-bottom: 1rem;
}

.stButton > button {
    background: linear-gradient(135deg, #F5A623 0%, #E8820C 100%);
    color: #0D1117;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.7rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.03em;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(245, 166, 35, 0.35);
}

.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] {
    background: var(--card);
    border-right: 1px solid var(--border);
}

.total-energy-box {
    background: linear-gradient(135deg, rgba(245,166,35,0.15), rgba(232,130,12,0.08));
    border: 1px solid rgba(245,166,35,0.4);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin: 1.5rem 0;
}

.total-value {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #F5A623;
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

forecast_type = st.radio(
    "Section",
    ["Solar 3h forecast", "Energy consumption 24h"],
    horizontal=True,
    label_visibility="collapsed"
)

# ── Header (dynamic by section) ───────────────────────────────────────────────
if forecast_type == "Energy consumption 24h":
    st.markdown('<div class="main-title">⚡ Energy Consumption Forecaster</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">24-Hour Ahead Consumption Forecast  ·  Recursive hybrid (XGB + LSTM)  ·  Upload CSV</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="main-title">☀️ Solar Energy Forecaster</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">3-Hour Ahead GHI Prediction → Energy Generation  ·  XGBoost Meta-Model  ·  Window (12,3)</div>', unsafe_allow_html=True)

if forecast_type == "Energy consumption 24h":
    # ── Energy consumption 24h section ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Energy Forecast Settings")
        st.markdown('<div class="info-box">Configure input for the 24h consumption model. Use manual entry or upload a CSV.</div>', unsafe_allow_html=True)
        energy_max_rows = st.number_input(
            "Max rows from CSV to use",
            min_value=1, max_value=10000, value=500, step=100,
            help="Only the last N rows are sent to the API (last row = forecast start)."
        )
        st.markdown("---")
        st.markdown("### 🔗 API Status")
        try:
            re = requests.get(f"{API_URL}/energy-status", timeout=3)
            if re.status_code == 200:
                data = re.json()
                if data.get("hybrid_ready"):
                    st.success("Hybrid (XGB + LSTM) ready ✓")
                else:
                    st.warning(data.get("message", "LSTM not loaded — add lstm_consumption.pt"))
            else:
                r = requests.get(f"{API_URL}/health", timeout=3)
                if r.status_code == 200:
                    st.warning("Backend up but energy-status failed")
                else:
                    st.error("Backend offline — start FastAPI server")
        except Exception:
            st.error("Backend offline — start FastAPI server")
        st.markdown("---")
        st.caption("24h consumption · Hybrid (XGB + LSTM) required")

    st.markdown('<div class="section-header">📥 Upload historical data for 24h consumption forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">CSV must have <b>datetime</b> or <b>dt</b> and <b>Global_active_power</b> (hourly). Need at least 24 rows; last row = forecast start. Recursive hybrid (XGB + LSTM) uses these to produce 24 varied hourly predictions.</div>', unsafe_allow_html=True)

    energy_data = None
    energy_uploaded = st.file_uploader("CSV for energy consumption", type=["csv"], key="energy_csv")
    if energy_uploaded:
        try:
            df_energy = pd.read_csv(energy_uploaded)
            if "datetime" not in df_energy.columns and "dt" not in df_energy.columns:
                st.error("CSV must include a 'datetime' or 'dt' column.")
            elif "Global_active_power" not in df_energy.columns and "global_active_power" not in df_energy.columns:
                st.error("CSV must include 'Global_active_power' (or 'global_active_power').")
            elif len(df_energy) < 24:
                st.error("Need at least 24 rows of hourly data.")
            else:
                n_use = min(int(energy_max_rows), len(df_energy))
                energy_data = df_energy.tail(n_use).to_dict(orient="records")
                st.success(f"✓ Using last **{n_use}** rows (of {len(df_energy)}).")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    energy_clicked = st.button("⚡ Generate 24h consumption forecast", key="energy_btn")
    if energy_clicked:
        if energy_data is None or len(energy_data) == 0:
            st.warning("Upload a CSV with datetime and Global_active_power (at least 24 rows) first.")
        else:
            with st.spinner("Running energy consumption model..."):
                try:
                    payload = {"historical_data": energy_data}
                    r = requests.post(f"{API_URL}/predict-energy", json=payload, timeout=60)
                    if r.status_code == 200:
                        data = r.json()
                        forecasts = data["forecasts"]
                        total = data["total_consumption_kwh"]
                        st.markdown('<div class="section-header">📊 24h consumption forecast</div>', unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="total-energy-box">
                            <div class="metric-label">Total predicted consumption (24h)</div>
                            <div class="total-value">{total:.4f} kWh</div>
                        </div>""", unsafe_allow_html=True)
                        chart_df = pd.DataFrame({
                            "Hour": [f["hour_label"] for f in forecasts],
                            "Consumption (kWh)": [f["consumption_kwh"] for f in forecasts],
                        })
                        st.bar_chart(chart_df.set_index("Hour"), color="#58A6FF", height=300)
                        with st.expander("View hourly table"):
                            st.dataframe(pd.DataFrame(forecasts), use_container_width=True)
                        with st.expander("Raw response"):
                            st.json(data)
                    else:
                        st.error(f"API error {r.status_code}: " + (r.json().get("detail", r.text) if r.text else ""))
                except requests.exceptions.ConnectionError:
                    st.error("Backend offline. Start the FastAPI server.")
                except Exception as e:
                    st.error(str(e))

else:
    # ── Existing Solar 3h forecast (unchanged logic) ──────────────────────────
    # ── Sidebar — Panel Settings ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Panel Settings")
        st.markdown('<div class="info-box">Configure your solar panel parameters to calculate actual energy output.</div>', unsafe_allow_html=True)
    
        panel_area = st.number_input(
            "Panel Area (m²)",
            min_value=0.1, max_value=10000.0,
            value=10.0, step=0.5,
            help="Total solar panel surface area"
        )
        panel_efficiency = st.slider(
            "Panel Efficiency (%)",
            min_value=5, max_value=35,
            value=20, step=1,
            help="Typical monocrystalline: 20–22%, polycrystalline: 15–17%"
        ) / 100.0
    
        st.markdown("---")
        st.markdown("### 🔗 API Status")
        try:
            r = requests.get(f"{API_URL}/health", timeout=3)
            if r.status_code == 200 and r.json().get("models_loaded"):
                st.success("Backend connected ✓")
            else:
                st.warning("Backend reachable but models not loaded")
        except Exception:
            st.error("Backend offline — start FastAPI server")
    
        st.markdown("---")
        st.caption("Model: XGBoost Enhanced · Window (12,3) · Predicts t+1h, t+2h, t+3h")
    
    # ── Input Mode ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📥 Input Historical Sensor Data</div>', unsafe_allow_html=True)
    
    input_mode = st.radio(
        "Input method",
        ["Manual Entry (last row + auto-fill context)", "Upload CSV"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="info-box">⚠️ The model needs at least <b>30 hourly rows</b> of context. Upload a CSV with full history, or use manual entry which auto-generates realistic context rows around your input.</div>', unsafe_allow_html=True)
    
    
    def generate_context(row: dict, n: int = 35) -> list[dict]:
        """Generate n synthetic historical rows ending at the given row."""
        base_dt = pd.to_datetime(row["datetime"]) - pd.Timedelta(hours=n)
        rows = []
        for i in range(n):
            dt   = base_dt + pd.Timedelta(hours=i)
            hour = dt.hour
            elev = max(0, 90 - abs(hour - 12) * 7.5)
            ghi  = max(0, elev * 10 + np.random.normal(0, 20))
            rows.append({
                "datetime" : dt.strftime("%Y-%m-%d %H:%M"),
                "GHI"      : round(ghi, 2),
                "DNI"      : round(max(0, ghi * 0.7  + np.random.normal(0, 15)), 2),
                "DHI"      : round(max(0, ghi * 0.25 + np.random.normal(0, 8)),  2),
                "T_amb"    : round(row["T_amb"] + np.random.normal(0, 1.5), 2),
                "RH"       : round(np.clip(row["RH"]   + np.random.normal(0, 3), 10, 100), 2),
                "WS"       : round(max(0, row["WS"]    + np.random.normal(0, 0.5)), 2),
                "WS_gust"  : round(max(0, row["WS_gust"] + np.random.normal(0, 0.8)), 2),
                "WD"       : round(row["WD"] % 360, 2),
                "WD_std"   : round(abs(row["WD_std"] + np.random.normal(0, 2)), 2),
                "BP"       : round(row["BP"] + np.random.normal(0, 1), 2),
            })
        rows.append(row)
        return rows
    
    
    historical_data = None
    
    if input_mode == "Manual Entry (last row + auto-fill context)":
        st.markdown('<div class="section-header">🌡️ Current Sensor Readings</div>', unsafe_allow_html=True)
    
        col1, col2, col3 = st.columns(3)
        with col1:
            dt_input = st.text_input("Datetime", value=datetime.now().strftime("%Y-%m-%d %H:00"),
                                      help="Format: YYYY-MM-DD HH:MM")
            GHI      = st.number_input("GHI — Global Horizontal Irradiance (W/m²)",
                                        min_value=0.0, max_value=1500.0, value=450.0, step=10.0)
            DNI      = st.number_input("DNI — Direct Normal Irradiance (W/m²)",
                                        min_value=0.0, max_value=1200.0, value=320.0, step=10.0)
            DHI      = st.number_input("DHI — Diffuse Horizontal Irradiance (W/m²)",
                                        min_value=0.0, max_value=600.0,  value=130.0, step=5.0)
    
        with col2:
            T_amb    = st.number_input("T_amb — Ambient Temperature (°C)",
                                        min_value=-20.0, max_value=60.0, value=28.0, step=0.5)
            RH       = st.number_input("RH — Relative Humidity (%)",
                                        min_value=0.0, max_value=100.0, value=55.0, step=1.0)
            WS       = st.number_input("WS — Wind Speed (m/s)",
                                        min_value=0.0, max_value=50.0, value=3.5, step=0.1)
    
        with col3:
            WS_gust  = st.number_input("WS_gust — Wind Gust (m/s)",
                                        min_value=0.0, max_value=80.0, value=5.2, step=0.1)
            WD       = st.number_input("WD — Wind Direction (°)",
                                        min_value=0.0, max_value=360.0, value=180.0, step=5.0)
            WD_std   = st.number_input("WD_std — Wind Direction Std Dev (°)",
                                        min_value=0.0, max_value=180.0, value=15.0, step=1.0)
            BP       = st.number_input("BP — Barometric Pressure (hPa)",
                                        min_value=800.0, max_value=1100.0, value=1013.0, step=0.5)
    
        current_row = {
            "datetime": dt_input, "GHI": GHI, "DNI": DNI, "DHI": DHI,
            "T_amb": T_amb, "RH": RH, "WS": WS, "WS_gust": WS_gust,
            "WD": WD, "WD_std": WD_std, "BP": BP,
        }
        historical_data = generate_context(current_row, n=35)
    
    else:
        uploaded = st.file_uploader(
            "Upload CSV (columns: datetime, GHI, DNI, DHI, T_amb, RH, WS, WS_gust, WD, WD_std, BP)",
            type=["csv"]
        )
        if uploaded:
            df_up = pd.read_csv(uploaded)
            required = ["datetime","GHI","DNI","DHI","T_amb","RH","WS","WS_gust","WD","WD_std","BP"]
            missing  = [c for c in required if c not in df_up.columns]
            if missing:
                st.error(f"Missing columns: {missing}")
            elif len(df_up) < 30:
                st.error(f"Need at least 30 rows, file has {len(df_up)}.")
            else:
                historical_data = df_up[required].to_dict(orient="records")
                st.success(f"✓ {len(historical_data)} rows loaded")
    
    # ── Predict Button ────────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    predict_clicked = st.button("⚡ Generate 3-Hour Solar Forecast")
    
    if predict_clicked:
        if historical_data is None:
            st.warning("Please provide input data first.")
        else:
            with st.spinner("Running XGBoost meta-model pipeline..."):
                payload = {
                    "historical_data"  : historical_data,
                    "panel_area_m2"    : panel_area,
                    "panel_efficiency" : panel_efficiency,
                }
                try:
                    resp = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
    
                    if resp.status_code == 200:
                        data      = resp.json()
                        forecasts = data["forecasts"]
    
                        # ── Summary metrics ───────────────────────────────────────
                        st.markdown('<div class="section-header">📊 Forecast Summary</div>',
                                    unsafe_allow_html=True)
    
                        c1, c2, c3, c4 = st.columns(4)
                        avg_ghi    = np.mean([f["ghi_wm2"]    for f in forecasts])
                        max_ghi    = np.max( [f["ghi_wm2"]    for f in forecasts])
                        total_kwh  = data["total_energy_kwh"]
                        avg_kwh    = np.mean([f["energy_kwh"] for f in forecasts])
    
                        with c1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Avg GHI</div>
                                <div class="metric-value">{avg_ghi:.0f}</div>
                                <div class="metric-unit">W/m²</div>
                            </div>""", unsafe_allow_html=True)
    
                        with c2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Peak GHI</div>
                                <div class="metric-value">{max_ghi:.0f}</div>
                                <div class="metric-unit">W/m²</div>
                            </div>""", unsafe_allow_html=True)
    
                        with c3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Total Energy</div>
                                <div class="metric-value">{total_kwh:.3f}</div>
                                <div class="metric-unit">kWh (3 hrs)</div>
                            </div>""", unsafe_allow_html=True)
    
                        with c4:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Avg / Hour</div>
                                <div class="metric-value">{avg_kwh:.3f}</div>
                                <div class="metric-unit">kWh</div>
                            </div>""", unsafe_allow_html=True)
    
                        # ── Total energy highlight ────────────────────────────────
                        st.markdown(f"""
                        <div class="total-energy-box">
                            <div class="metric-label">⚡ Total Solar Energy Generated (next 3 hours)</div>
                            <div class="total-value">{total_kwh:.4f} kWh</div>
                            <div class="metric-unit">
                                {panel_area} m² panel  ·  {panel_efficiency*100:.0f}% efficiency
                            </div>
                        </div>""", unsafe_allow_html=True)
    
                        # ── Per-hour forecasts ────────────────────────────────────
                        st.markdown('<div class="section-header">🕐 Hourly Breakdown</div>',
                                    unsafe_allow_html=True)
    
                        col_a, col_b = st.columns([3, 2])
    
                        with col_a:
                            for f in forecasts:
                                st.markdown(f"""
                                <div class="forecast-card">
                                    <div class="hour-badge">t+{f['step']}h</div>
                                    <div style="flex:1">
                                        <div style="font-family:'Syne',sans-serif;font-weight:600;font-size:0.95rem;">
                                            {f['hour_label']}
                                        </div>
                                        <div style="color:#8B949E;font-size:0.82rem;margin-top:2px;">
                                            {f['irradiance_category']}
                                        </div>
                                    </div>
                                    <div style="text-align:right">
                                        <div style="font-family:'Syne',sans-serif;font-weight:700;
                                                    color:#F5A623;font-size:1.1rem;">
                                            {f['ghi_wm2']:.1f} W/m²
                                        </div>
                                        <div style="color:#3FB950;font-weight:500;font-size:0.9rem;">
                                            {f['energy_kwh']:.4f} kWh
                                        </div>
                                    </div>
                                </div>""", unsafe_allow_html=True)
    
                        with col_b:
                            # Bar chart using streamlit native
                            chart_df = pd.DataFrame({
                                "Hour"       : [f["hour_label"].split(" ")[1] for f in forecasts],
                                "GHI (W/m²)" : [f["ghi_wm2"]    for f in forecasts],
                                "Energy (kWh)": [f["energy_kwh"] for f in forecasts],
                            }).set_index("Hour")
    
                            st.markdown("**GHI Forecast (W/m²)**")
                            st.bar_chart(chart_df[["GHI (W/m²)"]], color="#F5A623", height=180)
    
                            st.markdown("**Energy Output (kWh)**")
                            st.bar_chart(chart_df[["Energy (kWh)"]], color="#3FB950", height=180)
    
                        # ── Raw data expander ─────────────────────────────────────
                        with st.expander("📋 View Raw Forecast Data"):
                            st.json(data)
    
                    else:
                        err = resp.json().get("detail", resp.text)
                        st.error(f"API Error {resp.status_code}: {err}")
    
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Run: `uvicorn main:app --reload`")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    
    # ── Footer info ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#8B949E;font-size:0.8rem;">
        XGBoost Meta-Model · VMD Decomposition · Hybrid Feature Selection · Window (12,3)
        <br>Energy = GHI × Area × Efficiency / 1000
    </div>
    """, unsafe_allow_html=True)