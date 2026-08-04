"""
pages/7_Price_Duration_Curves.py
----------------------------------
Price Duration Curves — Riddhi Borkute's Energy Portfolio

A standard energy-analysis tool: sort every hour of a year from highest to
lowest price and plot the curve. Overlaying years shows how the renewable
build-out reshapes the price distribution -- the curve flattens in the middle
and the right-hand tail sinks below zero as negative-price hours multiply.

Pairs with the Cannibalization Explorer and Negative Price Heatmap as the
third view of the same story: what rising renewables do to power prices.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="Price Duration Curves | Energy Portfolio",
    layout="wide",
)

# -- Theme: same system as Home.py — charcoal + teal (structure) + amber (value) -
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

hr { border-color: #232324; }
</style>
""", unsafe_allow_html=True)

# -- Data loading ----------------------------------------------------------------
DATA_DIR = Path("data")
PRICE_FILES = {
    "Germany (DE)":       "prices_DE.parquet",
    "Netherlands (NL)":   "prices_NL.parquet",
    "Denmark West (DK1)": "prices_DK1.parquet",
    "Denmark East (DK2)": "prices_DK2.parquet",
}

# Portfolio scope everywhere is 2018–2024 — enforced at load time so a stray
# year in the underlying parquet file (e.g. a partial 2025) can't appear
# in the year selector, the curves, or the stats table.
SCOPE_YEAR_MIN, SCOPE_YEAR_MAX = 2018, 2024


@st.cache_data(show_spinner="Loading price data…")
def load_prices(market_key: str) -> pd.DataFrame:
    path = DATA_DIR / PRICE_FILES[market_key]
    if not path.exists():
        st.error(f"File not found: `{path}`. Make sure your `data/` folder is present.")
        st.stop()
    df = pd.read_parquet(path)
    if not isinstance(df.index, pd.DatetimeIndex):
        time_col = next((c for c in df.columns
                         if c.lower() in ("time", "datetime", "timestamp", "date")), None)
        if time_col:
            df = df.set_index(pd.to_datetime(df[time_col])).drop(columns=[time_col])
        else:
            df.index = pd.to_datetime(df.index)
    df.index.name = "time"
    df = df[df.index.notna()].sort_index()
    df = df[~df.index.duplicated(keep="first")]
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.error(f"No numeric price column found in `{PRICE_FILES[market_key]}`.")
        st.stop()
    out = pd.DataFrame({"price": df[numeric_cols[0]].values}, index=df.index)
    out["year"] = out.index.year

    # Keep only 2018–2024, matching the rest of the portfolio
    out = out[(out["year"] >= SCOPE_YEAR_MIN) & (out["year"] <= SCOPE_YEAR_MAX)]
    return out


def duration_curve(prices: np.ndarray):
    """
    Sort prices high -> low and return (x_pct, y_sorted) where x_pct is the
    percentage of hours (0-100). This is the price duration curve.
    """
    s = np.sort(prices)[::-1]                 # descending
    x = np.linspace(0, 100, len(s))           # % of hours
    return x, s


# -- Header ------------------------------------------------------------------------
st.markdown('<div class="eyebrow">Independent Research · Tool 4 of 4</div>', unsafe_allow_html=True)
st.title("Price Duration Curves")

st.markdown("""
<div class="body-text">
A price duration curve takes every single hour of a year and lines them up from the most
expensive hour to the cheapest — no dates, no seasons, just the shape of the whole year's
prices in one line. It's a standard tool in energy analysis because it compresses 8,760 hourly
prices into one picture that's easy to compare year over year, without getting lost in the
noise of individual days.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<strong>How to read the curve.</strong><br>
The <strong>left side</strong> (0% of hours) is the single most expensive hour of the year —
scarcity pricing, a handful of extreme spikes. The <strong>flat middle</strong> is the "normal"
price level most hours actually sit at. The <strong>right side</strong> (approaching 100% of
hours) is the cheapest hours — and where this dips below <code>€0/MWh</code>, those are the
oversupply hours covered in more detail on the Negative Price Heatmap page.<br><br>
As renewable capacity grows year over year, two things tend to happen to this curve: it
<strong>flattens</strong> in the middle (less price variation on a typical day), and its
<strong>right tail sinks further below zero</strong> (oversupply happens more often and more
severely). Overlaying multiple years lets you see both shifts directly.
</div>
""", unsafe_allow_html=True)

# -- Sidebar -----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="section-label">Market</div>', unsafe_allow_html=True)
    market = st.selectbox("Market", list(PRICE_FILES.keys()), index=0)

    df = load_prices(market)
    years = sorted(df["year"].unique())

    if not years:
        st.error(f"No data in the 2018–2024 range was found for {market}.")
        st.stop()

    st.markdown('<div class="section-label">Years to Overlay</div>', unsafe_allow_html=True)
    sel_years = st.multiselect(
        "Compare years", options=years, default=[years[0], years[-1]],
        help="Overlay multiple years to see the distribution shift."
    )

    st.markdown('<div class="section-label">Options</div>', unsafe_allow_html=True)
    show_zero = st.checkbox("Highlight €0 line", value=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#8f8c86; font-family: "IBM Plex Mono", monospace; line-height:1.8;'>
    x-axis = % of hours in the year<br>
    y-axis = day-ahead price (€/MWh)<br>
    Data: ENTSO-E (2018–2024)
    </div>
    """, unsafe_allow_html=True)

if not sel_years:
    st.warning("Select at least one year from the sidebar.")
    st.stop()

# -- Build curves --------------------------------------------------------------------
# Colour gradient: older years cooler teal, recent years warmer amber —
# same visual language as the rest of the site (structure = teal, value/
# recency = amber), so the newest, most relevant year is also the most
# visually prominent line.
def year_color(yr, all_years):
    if len(all_years) == 1:
        return "#2dd4bf"
    pos = (yr - min(all_years)) / (max(all_years) - min(all_years))
    # interpolate teal (#2dd4bf -> 45,212,191) to amber (#f0a860 -> 240,168,96)
    r = int(45 + pos * (240 - 45))
    g = int(212 + pos * (168 - 212))
    b = int(191 + pos * (96 - 191))
    return f"rgb({r},{g},{b})"

fig = go.Figure()
for yr in sel_years:
    p = df[df["year"] == yr]["price"].values
    x, y = duration_curve(p)
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines", name=str(yr),
        line=dict(color=year_color(yr, sel_years), width=2),
        hovertemplate=f"<b>{yr}</b><br>%{{x:.0f}}%% of hours<br>€%{{y:.1f}}/MWh<extra></extra>",
    ))

if show_zero:
    fig.add_hline(y=0, line_dash="dot", line_color="#e05c5c",
                  annotation_text="€0/MWh", annotation_position="bottom right",
                  annotation_font_color="#e05c5c")

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131314", plot_bgcolor="#131314",
    font=dict(family="'IBM Plex Mono', monospace", color="#8f8c86"),
    xaxis=dict(title="% of hours in year", gridcolor="#232324", range=[0, 100]),
    yaxis=dict(title="Day-ahead price (€/MWh)", gridcolor="#232324"),
    legend=dict(bgcolor="#131314", bordercolor="#232324", borderwidth=1, title="Year"),
    margin=dict(l=70, r=20, t=30, b=50), height=480,
)
st.markdown(f'<div class="section-label">{market} — Price Duration Curve</div>', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# -- Comparison metrics ----------------------------------------------------------------
st.markdown('<div class="section-label">Distribution Shift</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
One card per selected year — the average price and two numbers that summarize how spread out
prices were that year: the share of hours below zero, and the P90–P10 spread (the gap between
a typically-expensive hour and a typically-cheap one).
</div>
""", unsafe_allow_html=True)

cols = st.columns(len(sel_years) if len(sel_years) <= 4 else 4)
stats = {}
for i, yr in enumerate(sel_years):
    p = df[df["year"] == yr]["price"].values
    stats[yr] = {
        "mean": np.mean(p),
        "median": np.median(p),
        "neg_pct": 100 * np.mean(p < 0),
        "p95": np.percentile(p, 95),
        "spread": np.percentile(p, 90) - np.percentile(p, 10),
    }
    with cols[i % 4]:
        st.metric(f"{yr} mean", f"€{stats[yr]['mean']:.0f}")
        st.caption(f"Neg hours: {stats[yr]['neg_pct']:.1f}%  ·  "
                   f"P90–P10 spread: €{stats[yr]['spread']:.0f}")

# narrative comparison between first and last selected year
if len(sel_years) >= 2:
    y0, y1 = min(sel_years), max(sel_years)
    d_neg = stats[y1]["neg_pct"] - stats[y0]["neg_pct"]
    d_spread = stats[y1]["spread"] - stats[y0]["spread"]
    st.markdown(f"""
    <div class="info-box">
    <strong>{y0} → {y1}:</strong> the share of negative-price hours changed by
    <strong>{d_neg:+.1f} percentage points</strong>, and the P90–P10 price spread changed by
    <strong>€{d_spread:+.0f}/MWh</strong>. A widening spread and a deeper negative tail are
    exactly the conditions that raise the value of flexibility — which is precisely what the
    Flexibility Simulator page quantifies in euros.
    </div>
    """, unsafe_allow_html=True)

# -- Data table -----------------------------------------------------------------------
with st.expander("Summary statistics by year"):
    tbl = pd.DataFrame(stats).T
    tbl.index.name = "Year"
    tbl = tbl.rename(columns={
        "mean": "Mean (€/MWh)", "median": "Median (€/MWh)",
        "neg_pct": "Neg hours (%)", "p95": "P95 (€/MWh)",
        "spread": "P90–P10 spread (€/MWh)",
    })
    st.dataframe(tbl.style.format("{:.1f}"), use_container_width=True)
    csv = tbl.to_csv().encode("utf-8")
    st.download_button("Download CSV", csv, f"duration_curve_stats_{market}.csv", "text/csv")

# -- Footer -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='font-size:0.75rem; color:#4a4a48; font-family: "IBM Plex Mono", monospace; text-align:center;'>
Price duration curve = all hourly prices in a year sorted high to low.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)
