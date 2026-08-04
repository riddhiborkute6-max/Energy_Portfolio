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
    layout="wide",
)

# ── Theme: same system as Home.py — charcoal + teal (structure) + amber (value) ─
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0c0c0d; color: #e9e7e2; }
.block-container { max-width: 100% !important; padding-left: 3rem; padding-right: 3rem; }

h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #f2f0eb !important; font-weight: 600 !important; }

.eyebrow {
    font-family: 'IBM Plex Mono', monospace; font-size: 15px;
    letter-spacing: 0.12em; text-transform: uppercase; color: #2dd4bf;
    margin-bottom: 0.6rem;
}
.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 15px;
    letter-spacing: 0.12em; text-transform: uppercase; color: #2dd4bf;
    margin: 2.4rem 0 0.6rem 0;
}
.body-text {
    color: #b7b4ac; font-size: 1.0rem; line-height: 1.8;
    width: 100%; text-align: justify; text-justify: inter-word;
}
.body-text strong { color: #f2f0eb; }
.body-text .accent { color: #f0a860; font-weight: 600; }

/* Explanation boxes — teal left border marks "here's how to read this" content */
.info-box {
    background: #131314; border-left: 3px solid #2dd4bf;
    border-radius: 0 8px 8px 0; padding: 1.1rem 1.4rem; margin: 1.2rem 0;
    font-size: 0.92rem; color: #b7b4ac; line-height: 1.7;
}
.info-box strong { color: #f2f0eb; }
.info-box code {
    background: #0c0c0d; border: 1px solid #232324; border-radius: 4px;
    padding: 1px 6px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem; color: #f0a860;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: #131314; border: 1px solid #232324; border-radius: 10px;
    padding: 0.9rem 1.1rem;
}
div[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important; color: #8f8c86 !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important; color: #f0a860 !important;
}

.stSelectbox > div, .stMultiSelect > div {
    background: #131314 !important; border-color: #232324 !important;
}

hr { border-color: #232324; }
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
        if not isinstance(df.index, pd.DatetimeIndex):
            time_col = next((c for c in df.columns if c.lower() in ("time", "datetime", "timestamp", "date")), None)
            if time_col:
                df = df.set_index(pd.to_datetime(df[time_col])).drop(columns=[time_col])
            else:
                df.index = pd.to_datetime(df.index)
        df.index.name = "time"

        df = df[df.index.notna()]
        df = df.sort_index()
        df = df[~df.index.duplicated(keep="first")]

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
        active          = grp[grp[tech] > 0]
        capture_price   = active["prices"].mean() if len(active) else np.nan
        capture_ratio   = (capture_price / avg_price) if avg_price != 0 else np.nan

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
st.markdown('<div class="eyebrow">Independent Research · Tool 1 of 4</div>', unsafe_allow_html=True)
st.title("Cannibalization Explorer")

st.markdown("""
<div class="body-text">
This tool measures how much money solar and wind generators are losing simply by producing
electricity at the same time as everyone else. As more solar panels come online, they all
generate at midday — flooding the market and pushing the price down exactly when solar is
selling. The more solar there is, the worse this gets for solar itself. That's the
<span class="accent">cannibalization effect</span>: renewables competing against their own
future growth.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<strong>The core number: Capture Price Ratio</strong><br>
This compares the average price a generator actually receives against the average price
everyone else received that year.<br><br>
<code>Capture Ratio = (average price during generation hours) ÷ (average market price)</code><br><br>
A worked example: if the year's average electricity price was €80/MWh, but solar only ran
during hours averaging €68/MWh (because everyone's solar was flooding the market at the same
time), the capture ratio is 68 ÷ 80 = <strong>0.85</strong>. Solar earned 15% less than an
"average" hour of electricity was worth — that gap is the cannibalization effect, in euros.<br><br>
A ratio of <strong>1.0</strong> means no penalty at all. A ratio <strong>below 1.0</strong>
means the technology is undercutting itself; the lower the number (or the faster it falls
over the years below), the stronger the effect.
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Market Selection</div>', unsafe_allow_html=True)
    selected_markets = st.multiselect(
        "Markets",
        options=list(MARKET_FILES.keys()),
        default=["Germany (DE)"],
        help="Compare cannibalization across multiple markets"
    )

    st.markdown('<div class="section-label">Technology</div>', unsafe_allow_html=True)
    tech_choice = st.radio("Renewable technology", ["Solar", "Wind", "Both"], index=0)

    st.markdown('<div class="section-label">Year Range</div>', unsafe_allow_html=True)
    year_min, year_max = st.slider("Filter years", 2018, 2024, (2018, 2024))

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#8f8c86; font-family: "IBM Plex Mono", monospace; line-height:1.8;'>
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

all_results = {}
raw_data    = {}

for market in selected_markets:
    df_raw = load_market(market)
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
st.markdown('<div class="section-label">Key Statistics</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
Each card below is the most recent year's capture ratio for one market/technology combination,
with the change since the first year in your selected range shown underneath.
</div>
""", unsafe_allow_html=True)

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
st.markdown("""
<div class="info-box" style="font-size:0.85rem; margin-top: 0.8rem;">
Reading the delta: a <strong>negative</strong> number (shown highlighted, since lower is worse
here) means the capture ratio has fallen since the start of your selected range — the
cannibalization effect is getting stronger for that market and technology.
</div>
""", unsafe_allow_html=True)

# ── Plot 1: Capture Ratio over time ──────────────────────────────────────────
st.markdown('<div class="section-label">Capture Price Ratio — Annual Trend</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
Solar lines are shown in warm amber tones, wind lines in cool teal tones. The dotted red line
marks parity (ratio = 1.0) — a generator earning exactly the market average. Any line trending
downward, moving further below that dotted line year over year, is a technology cannibalizing
itself more each year as more of it gets built.
</div>
""", unsafe_allow_html=True)

# Warm (amber) family for solar, cool (teal) family for wind — color says what it is
SOLAR_COLORS = ["#f0a860", "#e8935c", "#d9752e", "#c85f1f"]
WIND_COLORS  = ["#2dd4bf", "#22b8a3", "#1a9186", "#147268"]

def trace_color(market, tech):
    market_idx = list(MARKET_FILES.keys()).index(market) % 4
    palette = SOLAR_COLORS if tech == "solar" else WIND_COLORS
    return palette[market_idx]

PLOT_FONT = dict(family="'IBM Plex Mono', monospace", color="#8f8c86")
PLOT_BG   = "#131314"

fig1 = go.Figure()
for (market, tech), metrics in all_results.items():
    color = trace_color(market, tech)
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

fig1.add_hline(y=1.0, line_dash="dot", line_color="#e05c5c",
               annotation_text="Parity (ratio = 1.0)", annotation_position="bottom right",
               annotation_font_color="#e05c5c")

fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=PLOT_FONT,
    xaxis=dict(title="Year", dtick=1, gridcolor="#232324"),
    yaxis=dict(title="Capture Price Ratio", gridcolor="#232324"),
    legend=dict(bgcolor=PLOT_BG, bordercolor="#232324", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=420,
)
st.plotly_chart(fig1, use_container_width=True)

# ── Plot 2: Penetration vs Capture Ratio scatter ──────────────────────────────
st.markdown('<div class="section-label">Renewable Penetration vs. Capture Ratio</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
Each point is one year. Moving left to right along the x-axis, points show what happened to the
capture ratio as that technology's share of high-generation hours grew. A downward-sloping
cluster of points is the cannibalization effect made visible: as penetration rises, the ratio
falls.
</div>
""", unsafe_allow_html=True)

fig2 = go.Figure()
for (market, tech), metrics in all_results.items():
    color = trace_color(market, tech)
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
                    line=dict(width=1, color=PLOT_BG)),
        hovertemplate=(
            f"<b>{market} · {tech.title()}</b><br>"
            "Penetration: %{x:.1f}%<br>"
            "Capture Ratio: %{y:.4f}<br>"
            "<extra></extra>"
        )
    ))

fig2.add_hline(y=1.0, line_dash="dot", line_color="#e05c5c")
fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=PLOT_FONT,
    xaxis=dict(title="Renewable Penetration (% high-generation hours)", gridcolor="#232324"),
    yaxis=dict(title="Capture Price Ratio", gridcolor="#232324"),
    legend=dict(bgcolor=PLOT_BG, bordercolor="#232324", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=420,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Plot 3: Negative price hours ─────────────────────────────────────────────
st.markdown('<div class="section-label">Negative Price Hours (% of Year)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
This counts how often the market price fell below €0/MWh that year — meaning generators were
effectively paying to keep producing. It's the most extreme, visible symptom of the same
oversupply problem driving the capture ratio down: taller bars mean more hours of structural
oversupply from non-dispatchable renewables.
</div>
""", unsafe_allow_html=True)

fig3 = go.Figure()
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
    market_idx = list(MARKET_FILES.keys()).index(market) % 4
    color = SOLAR_COLORS[market_idx]
    fig3.add_trace(go.Bar(
        x=annual_neg["year"], y=annual_neg["neg_pct"],
        name=short,
        marker_color=color,
        opacity=0.85,
        hovertemplate=f"<b>{market}</b><br>Year: %{{x}}<br>Negative hrs: %{{y:.2f}}%<extra></extra>"
    ))

fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=PLOT_FONT,
    barmode="group",
    xaxis=dict(title="Year", dtick=1, gridcolor="#232324"),
    yaxis=dict(title="% Hours with Negative Price", gridcolor="#232324"),
    legend=dict(bgcolor=PLOT_BG, bordercolor="#232324", borderwidth=1),
    margin=dict(l=60, r=20, t=30, b=50),
    height=380,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Data table ────────────────────────────────────────────────────────────────
with st.expander("Annual Metrics Table"):
    st.markdown("""
    <div class="body-text" style="font-size:0.88rem; margin-bottom: 0.8rem;">
    The raw numbers behind every chart above, one row per market/technology/year. The
    background shading on Capture Ratio follows the same logic as the charts — greener is
    closer to or above parity, redder is further below it.
    </div>
    """, unsafe_allow_html=True)
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
    st.download_button("Download CSV", csv, "cannibalization_metrics.csv", "text/csv")

# ── Footer note ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.75rem; color:#4a4a48; font-family: "IBM Plex Mono", monospace; text-align:center;'>
Capture ratio = time-weighted average price during generation hours ÷ market average price.
Penetration proxy = share of hours above median generation level.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)
