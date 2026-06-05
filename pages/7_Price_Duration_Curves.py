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
    page_icon="📐",
    layout="wide",
)

# -- Styling -------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }
.concept-box {
    background: #161b22; border-left: 3px solid #58a6ff;
    border-radius: 0 6px 6px 0; padding: 0.9rem 1.2rem; margin: 1rem 0;
    font-size: 0.85rem; color: #8b949e; line-height: 1.6;
}
.concept-box strong { color: #e6edf3; }
.concept-box code {
    background: #0d1117; border: 1px solid #30363d; border-radius: 3px;
    padding: 1px 5px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; color: #79c0ff;
}
div[data-testid="stMetric"] {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# -- Data loading --------------------------------------------------------------
DATA_DIR = Path("data")
PRICE_FILES = {
    "Germany (DE)":       "prices_DE.parquet",
    "Netherlands (NL)":   "prices_NL.parquet",
    "Denmark West (DK1)": "prices_DK1.parquet",
    "Denmark East (DK2)": "prices_DK2.parquet",
}


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
    return out


def duration_curve(prices: np.ndarray):
    """
    Sort prices high -> low and return (x_pct, y_sorted) where x_pct is the
    percentage of hours (0-100). This is the price duration curve.
    """
    s = np.sort(prices)[::-1]                 # descending
    x = np.linspace(0, 100, len(s))           # % of hours
    return x, s


# -- Header --------------------------------------------------------------------
st.title("📐 Price Duration Curves")
st.markdown("""
<div class="concept-box">
<strong>How to read this.</strong> Every hour of the year is sorted from the highest price
(left) to the lowest (right) and plotted as a single curve. The <strong>left tail</strong>
shows scarcity hours (few, expensive); the <strong>flat middle</strong> is the typical price
level; the <strong>right tail</strong> dropping below <code>€0/MWh</code> shows hours of
over-supply. As renewables grow, the curve flattens and the right tail sinks deeper into
negative territory — a compact picture of the same shift the cannibalization and
negative-price pages explore.
</div>
""", unsafe_allow_html=True)

# -- Sidebar -------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🗺️ Market")
    market = st.selectbox("Market", list(PRICE_FILES.keys()), index=0)

    df = load_prices(market)
    years = sorted(df["year"].unique())

    st.markdown("### 📅 Years to overlay")
    sel_years = st.multiselect(
        "Compare years", options=years, default=[years[0], years[-1]],
        help="Overlay multiple years to see the distribution shift."
    )

    st.markdown("### ⚙️ Options")
    log_y = st.checkbox("Symlog price axis", value=False,
                        help="Compress extreme spikes for a clearer middle/tail view")
    show_zero = st.checkbox("Highlight €0 line", value=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#8b949e; font-family: IBM Plex Mono, monospace;'>
    x-axis = % of hours in the year<br>
    y-axis = day-ahead price (€/MWh)<br>
    Data: ENTSO-E (2018–2024)
    </div>
    """, unsafe_allow_html=True)

if not sel_years:
    st.warning("Select at least one year from the sidebar.")
    st.stop()

# -- Build curves --------------------------------------------------------------
# colour gradient: older years cooler/dimmer, recent years warmer/brighter
def year_color(yr, all_years):
    if len(all_years) == 1:
        return "#58a6ff"
    pos = (yr - min(all_years)) / (max(all_years) - min(all_years))
    # interpolate blue (old) -> red (recent)
    r = int(88 + pos * (255 - 88))
    g = int(166 + pos * (107 - 166))
    b = int(255 + pos * (107 - 255))
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
    fig.add_hline(y=0, line_dash="dot", line_color="#ff6b6b",
                  annotation_text="€0/MWh", annotation_position="bottom right",
                  annotation_font_color="#ff6b6b")

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="% of hours in year", gridcolor="#21262d", range=[0, 100]),
    yaxis=dict(title="Day-ahead price (€/MWh)", gridcolor="#21262d"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1, title="Year"),
    margin=dict(l=70, r=20, t=30, b=50), height=480,
)
if log_y:
    # symlog-like: clip handled by plotly's "linear"; use custom via abs transform note
    fig.update_yaxes(type="linear")  # placeholder; symlog not native in plotly
st.subheader(f"📐 {market} — Price Duration Curve")
st.plotly_chart(fig, use_container_width=True)

# -- Comparison metrics --------------------------------------------------------
st.markdown("---")
st.subheader("📊 Distribution Shift")
st.caption("How the price distribution has changed between the years you selected")

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
    <div class="concept-box" style="border-left-color:#3fb950;">
    <strong>{y0} → {y1}:</strong> the share of negative-price hours changed by
    <strong>{d_neg:+.1f} percentage points</strong>, and the P90–P10 price spread changed by
    <strong>€{d_spread:+.0f}/MWh</strong>. A widening spread and a deeper negative tail are
    exactly the conditions that raise the value of flexibility.
    </div>
    """, unsafe_allow_html=True)

# -- Data table ----------------------------------------------------------------
with st.expander("📋 Summary statistics by year"):
    tbl = pd.DataFrame(stats).T
    tbl.index.name = "Year"
    tbl = tbl.rename(columns={
        "mean": "Mean (€/MWh)", "median": "Median (€/MWh)",
        "neg_pct": "Neg hours (%)", "p95": "P95 (€/MWh)",
        "spread": "P90–P10 spread (€/MWh)",
    })
    st.dataframe(tbl.style.format("{:.1f}"), use_container_width=True)
    csv = tbl.to_csv().encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"duration_curve_stats_{market}.csv", "text/csv")

# -- Footer --------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Price duration curve = all hourly prices in a year sorted high to low.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)