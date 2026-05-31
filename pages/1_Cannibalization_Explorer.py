"""
pages/1_Cannibalization_Explorer.py
------------------------------------
Cannibalization Explorer — Riddhi Borkute's Energy Portfolio
Quantifies the solar/wind cannibalization effect by comparing
capture price ratios against renewable penetration per market & year.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cannibalization Explorer | Energy Portfolio",
    page_icon="⚡",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Dark analytical theme */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #58a6ff;
}

.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.5rem;
}

.metric-card .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.metric-card .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #58a6ff;
}

.metric-card .delta {
    font-size: 0.75rem;
    color: #3fb950;
}

.concept-box {
    background: #161b22;
    border-left: 3px solid #58a6ff;
    border-radius: 0 6px 6px 0;
    padding: 0.9rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.85rem;
    color: #8b949e;
    line-height: 1.6;
}

.concept-box strong { color: #e6edf3; }
.concept-box code {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 3px;
    padding: 1px 5px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: #79c0ff;
}

.stSelectbox > div, .stMultiSelect > div {
    background: #161b22 !important;
    border-color: #30363d !important;
}

div[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.8rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Data loading helpers ──────────────────────────────────────────────────────
DATA_DIR = Path("data")

MARKET_FILES = {
    "Germany (DE)":     {"prices": "prices_DE.parquet",  "wind": "wind_DE.parquet",  "solar": "solar_DE.parquet"},
    "Netherlands (NL)": {"prices": "prices_NL.parquet",  "wind": "wind_NL.parquet",  "solar": "solar_NL.parquet"},
    "Denmark West (DK1)": {"prices": "prices_DK1.parquet","wind": "wind_DK1.parquet","solar": "solar_DK1.parquet"},
    "Denmark East (DK2)": {"prices": "prices_DK2.parquet","wind": "wind_DK2.parquet","solar": "solar_DK2.parquet"},
}

@st.cache_data(show_spinner="Loading market data…")
def load_market(market_key: str) -> pd.DataFrame:
    """Load and merge prices + wind + solar for a given market."""
    files = MARKET_FILES[market_key]
    dfs = {}
    for kind, fname in files.items():
        path = DATA_DIR / fname
        if not path.exists():
            st.error(f"File not found: `{path}`. Make sure your `data/` folder is present.")
            st.stop()
        df = pd.read_parquet(path)
        # Normalise: expect a datetime index or a column named 'time'/'datetime'/'timestamp'
        if not isinstance(df.index, pd.DatetimeIndex):
            time_col = next((c for c in df.columns if c.lower() in ("time", "datetime", "timestamp", "date")), None)
            if time_col:
                df = df.set_index(pd.to_datetime(df[time_col])).drop(columns=[time_col])
            else:
                df.index = pd.to_datetime(df.index)
        df.index.name = "time"
        # Keep first numeric column
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if not numeric_cols:
            st.error(f"No numeric column found in `{fname}`.")
            st.stop()
        dfs[kind] = df[numeric_cols[0]].rename(kind)

    merged = pd.concat(dfs.values(), axis=1)
    merged.dropna(inplace=True)
    merged["year"] = merged.index.year
    return merged


def compute_cannibalization(df: pd.DataFrame, tech: str) -> pd.DataFrame:
    """
    Annual cannibalization metrics for a given technology (wind / solar).

    Returns DataFrame with columns:
        year, avg_price, capture_price, capture_ratio,
        ren_penetration_pct, hours_negative_pct
    """
    rows = []
    for year, grp in df.groupby("year"):
        avg_price       = grp["prices"].mean()
        # Capture price = average market price in hours when tech > 0
        active          = grp[grp[tech] > 0]
        capture_price   = active["prices"].mean() if len(active) else np.nan
        capture_ratio   = (capture_price / avg_price) if avg_price != 0 else np.nan

        total_gen       = grp[["wind", "solar"]].sum(axis=1) if all(c in grp.columns for c in ["wind","solar"]) else grp[tech]
        # Penetration: hours where tech > median(tech) as share of year
        ren_hours       = (grp[tech] > grp[tech].median()).sum()
        ren_pen_pct     = 100 * ren_hours / len(grp)

        neg_price_hrs   = (grp["prices"] < 0).sum()
        neg_pct         = 100 * neg_price_hrs / len(grp)

        rows.append({
            "year": year,
            "avg_price": avg_price,
            "capture_price": capture_price,
            "capture_ratio": capture_ratio,
            "ren_penetration_pct": ren_pen_pct,
            "neg_price_pct": neg_pct,
            "n_hours": len(grp),
        })
    return pd.DataFrame(rows)


# ── Header ───────────────────────────────────────────────────────────────────
st.title("⚡ Cannibalization Explorer")
st.markdown("""
<div class="concept-box">
<strong>What is the cannibalization effect?</strong><br>
As renewable generation increases, it preferentially produces during high-generation periods — 
pushing prices down exactly when it generates most. The <code>capture price ratio</code> 
(generator's time-weighted average price ÷ market average price) quantifies this self-erosion. 
A ratio &lt; 1 confirms cannibalization; the steeper the decline over years, the stronger the effect.
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Market Selection")
    selected_markets = st.multiselect(
        "Markets",
        options=list(MARKET_FILES.keys()),
        default=["Germany (DE)"],
        help="Compare cannibalization across multiple markets"
    )

    st.markdown("### ⚙️ Technology")
    tech_choice = st.radio("Renewable technology", ["Solar", "Wind", "Both"], index=0)

    st.markdown("### 📅 Year Range")
    year_min, year_max = st.slider("Filter years", 2018, 2024, (2018, 2024))

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#8b949e; font-family: IBM Plex Mono, monospace;'>
    Data: ENTSO-E Transparency Platform<br>
    Resolution: Hourly<br>
    Period: 2018 – 2024
    </div>
    """, unsafe_allow_html=True)

if not selected_markets:
    st.warning("Please select at least one market from the sidebar.")
    st.stop()

# ── Load & compute ────────────────────────────────────────────────────────────
techs = []
if tech_choice in ("Solar", "Both"):
    techs.append("solar")
if tech_choice in ("Wind", "Both"):
    techs.append("wind")

all_results = {}  # (market, tech) -> annual metrics df
raw_data    = {}  # market -> hourly merged df

for market in selected_markets:
    df_raw = load_market(market)
    # Rename columns to standard names
    col_map = {}
    for c in df_raw.columns:
        cl = c.lower()
        if cl == "prices" or "price" in cl:
            col_map[c] = "prices"
        elif "wind" in cl:
            col_map[c] = "wind"
        elif "solar" in cl:
            col_map[c] = "solar"
    df_raw = df_raw.rename(columns=col_map)
    df_raw = df_raw[(df_raw["year"] >= year_min) & (df_raw["year"] <= year_max)]
    raw_data[market] = df_raw

    for tech in techs:
        if tech not in df_raw.columns:
            st.warning(f"`{tech}` column not found for {market}. Skipping.")
            continue
        metrics = compute_cannibalization(df_raw, tech)
        all_results[(market, tech)] = metrics

if not all_results:
    st.error("No data could be computed. Check your column names and file paths.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Key Statistics")

kpi_cols = st.columns(len(all_results) if len(all_results) <= 4 else 4)
for i, ((market, tech), metrics) in enumerate(all_results.items()):
    with kpi_cols[i % 4]:
        latest = metrics.iloc[-1]
        first  = metrics.iloc[0]
        delta_ratio = latest["capture_ratio"] - first["capture_ratio"]
        st.metric(
            label=f"{market} · {tech.title()}",
            value=f"{latest['capture_ratio']:.3f}",
            delta=f"{delta_ratio:+.3f} vs {first['year']:.0f}",
            delta_color="inverse",
            help="Capture price ratio (latest year). Below 1.0 = cannibalized."
        )

# ── Plot 1: Capture Ratio over time ──────────────────────────────────────────
st.markdown("---")
st.subheader("📉 Capture Price Ratio — Annual Trend")
st.caption("Values < 1.0 indicate the generator earns less than the average market price → cannibalization confirmed")

COLOR_MAP = {
    ("Germany (DE)", "solar"):      "#f0a500",
    ("Germany (DE)", "wind"):       "#58a6ff",
    ("Netherlands (NL)", "solar"):  "#ff7b54",
    ("Netherlands (NL)", "wind"):   "#79c0ff",
    ("Denmark West (DK1)", "solar"):"#ffd700",
    ("Denmark West (DK1)", "wind"): "#3fb950",
    ("Denmark East (DK2)", "solar"):"#e3b341",
    ("Denmark East (DK2)", "wind"): "#bc8cff",
}

fig1 = go.Figure()

for (market, tech), metrics in all_results.items():
    color = COLOR_MAP.get((market, tech), "#8b949e")
    dash  = "solid" if tech == "solar" else "dash"
    short = market.split("(")[1].replace(")", "")
    fig1.add_trace(go.Scatter(
        x=metrics["year"], y=metrics["capture_ratio"],
        mode="lines+markers",
        name=f"{short} {tech.title()}",
        line=dict(color=color, width=2.5, dash=dash),
        marker=dict(size=8, symbol="circle"),
        hovertemplate=(
            f"<b>{market} · {tech.title()}</b><br>"
            "Year: %{x}<br>"
            "Capture Ratio: %{y:.4f}<br>"
            "<extra></extra>"
        )
    ))

fig1.add_hline(y=1.0, line_dash="dot", line_color="#ff6b6b",
               annotation_text="Parity (ratio = 1.0)", annotation_position="bottom right",
               annotation_font_color="#ff6b6b")

fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="Year", dtick=1, gridcolor="#21262d"),
    yaxis=dict(title="Capture Price Ratio", gridcolor="#21262d"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=420,
)
st.plotly_chart(fig1, use_container_width=True)

# ── Plot 2: Penetration vs Capture Ratio scatter ──────────────────────────────
st.markdown("---")
st.subheader("🔵 Renewable Penetration vs. Capture Ratio")
st.caption("Downward slope = cannibalization effect — higher penetration erodes capture price")

fig2 = go.Figure()

for (market, tech), metrics in all_results.items():
    color = COLOR_MAP.get((market, tech), "#8b949e")
    short = market.split("(")[1].replace(")", "")
    fig2.add_trace(go.Scatter(
        x=metrics["ren_penetration_pct"],
        y=metrics["capture_ratio"],
        mode="markers+text",
        name=f"{short} {tech.title()}",
        text=metrics["year"].astype(int).astype(str),
        textposition="top center",
        textfont=dict(size=9, color=color),
        marker=dict(color=color, size=12, opacity=0.85,
                    line=dict(width=1, color="#0d1117")),
        hovertemplate=(
            f"<b>{market} · {tech.title()}</b><br>"
            "Penetration: %{x:.1f}%<br>"
            "Capture Ratio: %{y:.4f}<br>"
            "<extra></extra>"
        )
    ))

fig2.add_hline(y=1.0, line_dash="dot", line_color="#ff6b6b")
fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="Renewable Penetration (% high-generation hours)", gridcolor="#21262d"),
    yaxis=dict(title="Capture Price Ratio", gridcolor="#21262d"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=420,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Plot 3: Negative price hours ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🔴 Negative Price Hours (% of year)")
st.caption("Hours with price < €0/MWh — a structural signal of over-supply driven by non-dispatchable renewables")

fig3 = go.Figure()
for (market, tech), metrics in all_results.items():
    # Use only per-market data (avoid duplicate bars if both techs selected)
    pass  # handled below per market

done_markets = set()
for (market, tech), metrics in all_results.items():
    if market in done_markets:
        continue
    done_markets.add(market)
    df_mkt = raw_data[market]
    annual_neg = df_mkt.groupby("year").apply(
        lambda g: 100 * (g["prices"] < 0).sum() / len(g)
    ).reset_index(name="neg_pct")
    short = market.split("(")[1].replace(")", "")
    color = list(COLOR_MAP.values())[list(MARKET_FILES.keys()).index(market) * 2 % len(COLOR_MAP)]
    fig3.add_trace(go.Bar(
        x=annual_neg["year"], y=annual_neg["neg_pct"],
        name=short,
        marker_color=color,
        opacity=0.85,
        hovertemplate=f"<b>{market}</b><br>Year: %{{x}}<br>Negative hrs: %{{y:.2f}}%<extra></extra>"
    ))

fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    barmode="group",
    xaxis=dict(title="Year", dtick=1, gridcolor="#21262d"),
    yaxis=dict(title="% Hours with Negative Price", gridcolor="#21262d"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=380,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Data table ────────────────────────────────────────────────────────────────
with st.expander("📋 Annual Metrics Table"):
    frames = []
    for (market, tech), metrics in all_results.items():
        df_show = metrics.copy()
        df_show.insert(0, "Market", market)
        df_show.insert(1, "Technology", tech.title())
        frames.append(df_show)
    df_all = pd.concat(frames, ignore_index=True)
    df_all["year"] = df_all["year"].astype(int)
    df_all = df_all.rename(columns={
        "year": "Year",
        "avg_price": "Avg Price (€/MWh)",
        "capture_price": "Capture Price (€/MWh)",
        "capture_ratio": "Capture Ratio",
        "ren_penetration_pct": "Penetration (%)",
        "neg_price_pct": "Neg. Price Hrs (%)",
        "n_hours": "Hours",
    })
    st.dataframe(
        df_all.style.format({
            "Avg Price (€/MWh)": "{:.2f}",
            "Capture Price (€/MWh)": "{:.2f}",
            "Capture Ratio": "{:.4f}",
            "Penetration (%)": "{:.1f}",
            "Neg. Price Hrs (%)": "{:.2f}",
        }).background_gradient(subset=["Capture Ratio"], cmap="RdYlGn", vmin=0.7, vmax=1.1),
        use_container_width=True,
    )
    csv = df_all.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "cannibalization_metrics.csv", "text/csv")

# ── Footer note ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Capture ratio = time-weighted average price during generation hours ÷ market average price.
Penetration proxy = share of hours above median generation level.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)