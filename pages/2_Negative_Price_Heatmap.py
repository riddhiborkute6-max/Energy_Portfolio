"""
pages/2_Negative_Price_Heatmap.py
----------------------------------
Negative Price Heatmap — Riddhi Borkute's Energy Portfolio

Visualises WHEN electricity prices go negative across the day and year.
Negative prices are a direct symptom of renewable over-supply and a core
driver of the value case for industrial flexibility assets.

Default view: Hour-of-day (y) × Month (x), colour = % of hours negative.
Comparison:   Small multiples (all years) OR single-year dropdown.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Negative Price Heatmap | Energy Portfolio",
    page_icon="🔴",
    layout="wide",
)

# ── Custom CSS (matches Cannibalization Explorer) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }

.concept-box {
    background: #161b22;
    border-left: 3px solid #ff6b6b;
    border-radius: 0 6px 6px 0;
    padding: 0.9rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.85rem;
    color: #8b949e;
    line-height: 1.6;
}
.concept-box strong { color: #e6edf3; }
.concept-box code {
    background: #0d1117; border: 1px solid #30363d; border-radius: 3px;
    padding: 1px 5px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; color: #ff7b72;
}

div[data-testid="stMetric"] {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem;
}
.stSelectbox > div, .stRadio > div { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Data loading (shared logic with Cannibalization Explorer) ──────────────────
DATA_DIR = Path("data")

PRICE_FILES = {
    "Germany (DE)":       "prices_DE.parquet",
    "Netherlands (NL)":   "prices_NL.parquet",
    "Denmark West (DK1)": "prices_DK1.parquet",
    "Denmark East (DK2)": "prices_DK2.parquet",
}

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data(show_spinner="Loading price data…")
def load_prices(market_key: str) -> pd.DataFrame:
    """Load a single price series, clean the time index, return tidy frame."""
    path = DATA_DIR / PRICE_FILES[market_key]
    if not path.exists():
        st.error(f"File not found: `{path}`. Make sure your `data/` folder is present.")
        st.stop()

    df = pd.read_parquet(path)

    # Normalise the time index
    if not isinstance(df.index, pd.DatetimeIndex):
        time_col = next((c for c in df.columns
                         if c.lower() in ("time", "datetime", "timestamp", "date")), None)
        if time_col:
            df = df.set_index(pd.to_datetime(df[time_col])).drop(columns=[time_col])
        else:
            df.index = pd.to_datetime(df.index)
    df.index.name = "time"

    # Clean: drop bad timestamps, sort, remove duplicate hours (DST fall-back)
    df = df[df.index.notna()].sort_index()
    df = df[~df.index.duplicated(keep="first")]

    # Identify the price column (first numeric)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.error(f"No numeric price column found in `{PRICE_FILES[market_key]}`.")
        st.stop()

    out = pd.DataFrame({"price": df[numeric_cols[0]].values}, index=df.index)
    out["year"]  = out.index.year
    out["month"] = out.index.month
    out["hour"]  = out.index.hour
    return out


def build_heatmap_matrix(df_year: pd.DataFrame) -> pd.DataFrame:
    """
    For one year: return a 24 (hour) × 12 (month) matrix of the
    percentage of hours with negative price in each hour/month cell.
    """
    # Count negative hours and total hours per (hour, month)
    grp = df_year.groupby(["hour", "month"])
    neg = grp["price"].apply(lambda s: 100 * (s < 0).mean())  # % negative
    mat = neg.unstack("month")  # rows = hour, cols = month

    # Ensure full 24×12 grid even if some cells are empty
    mat = mat.reindex(index=range(24), columns=range(1, 13))
    return mat


# ── Header ───────────────────────────────────────────────────────────────────
st.title("🔴 Negative Price Heatmap")
st.markdown("""
<div class="concept-box">
<strong>Why negative prices matter.</strong>
Prices fall below <code>€0/MWh</code> when inflexible generation (renewables that can't
easily switch off, plus must-run plants) exceeds demand. Producers literally pay to
offload power. The pattern of <em>when</em> this happens — midday solar peaks in summer,
windy nights — is exactly when a flexible industrial asset can get paid to consume.
This heatmap maps that opportunity across the day and year.
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Market")
    market = st.selectbox("Select market", list(PRICE_FILES.keys()), index=0)

    st.markdown("### 🖼️ View Mode")
    view_mode = st.radio(
        "Comparison layout",
        ["Small multiples (all years)", "Single year"],
        index=0,
        help="Small multiples show every year side by side. Single year zooms into one."
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#8b949e; font-family: IBM Plex Mono, monospace;'>
    Cell value = % of hours in that<br>
    hour-of-day & month with<br>
    price &lt; €0/MWh.<br><br>
    Data: ENTSO-E (2018–2024)
    </div>
    """, unsafe_allow_html=True)

# ── Load & prepare ──────────────────────────────────────────────────────────────
df = load_prices(market)
years = sorted(df["year"].unique())

if view_mode == "Single year":
    with st.sidebar:
        st.markdown("### 📅 Year")
        sel_year = st.select_slider("Choose year", options=years, value=years[-1])

# ── KPI strip ───────────────────────────────────────────────────────────────────
st.markdown("---")
total_neg_pct = 100 * (df["price"] < 0).mean()
worst_year_series = df.groupby("year")["price"].apply(lambda s: 100 * (s < 0).mean())
worst_year = worst_year_series.idxmax()
peak_hour_series = df[df["price"] < 0]["hour"].value_counts()
peak_hour = peak_hour_series.idxmax() if len(peak_hour_series) else None

k1, k2, k3, k4 = st.columns(4)
k1.metric("Negative hours (all years)", f"{total_neg_pct:.2f}%")
k2.metric("Worst year", f"{worst_year}", f"{worst_year_series.max():.2f}% of hours")
k3.metric("Most common hour", f"{peak_hour:02d}:00" if peak_hour is not None else "—",
          help="Hour of day when negative prices occur most often")
latest = worst_year_series.index.max()
earliest = worst_year_series.index.min()
growth = worst_year_series.loc[latest] - worst_year_series.loc[earliest]
k4.metric(f"Change {earliest}→{latest}", f"{growth:+.2f} pp",
          help="Percentage-point change in share of negative hours")

# ── Shared colour scale ─────────────────────────────────────────────────────────
# Compute a common max across all years so colours are comparable
all_mats = {yr: build_heatmap_matrix(df[df["year"] == yr]) for yr in years}
global_max = max((m.max().max() for m in all_mats.values() if m.notna().any().any()),
                 default=5.0)
global_max = max(global_max, 1.0)  # avoid zero-range colour bar

COLORSCALE = [
    [0.0, "#0d1117"],   # background-matching dark for zero
    [0.15, "#1c2b3a"],
    [0.35, "#8a5a44"],
    [0.6, "#d9534f"],
    [1.0, "#ff4d4d"],   # bright red = frequent negative prices
]


def make_heatmap(mat: pd.DataFrame, title: str, showscale: bool = True) -> go.Heatmap:
    return go.Heatmap(
        z=mat.values,
        x=MONTH_LABELS,
        y=[f"{h:02d}" for h in range(24)],
        zmin=0, zmax=global_max,
        colorscale=COLORSCALE,
        showscale=showscale,
        colorbar=dict(title="% neg", thickness=12, len=0.8) if showscale else None,
        hovertemplate="Month: %{x}<br>Hour: %{y}:00<br>Negative: %{z:.1f}%<extra>" + title + "</extra>",
    )


# ── Render ────────────────────────────────────────────────────────────────────
st.markdown("---")

if view_mode == "Single year":
    st.subheader(f"📅 {market} — {sel_year}")
    st.caption("Brighter red = more frequent negative prices in that hour & month")

    mat = all_mats[sel_year]
    fig = go.Figure(make_heatmap(mat, str(sel_year), showscale=True))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
        xaxis=dict(title="Month", side="bottom"),
        yaxis=dict(title="Hour of day", autorange="reversed"),
        margin=dict(l=60, r=20, t=20, b=50),
        height=520,
    )
    st.plotly_chart(fig, use_container_width=True)

else:  # Small multiples
    st.subheader(f"🖼️ {market} — All years")
    st.caption("Shared colour scale across all panels, so intensity is directly comparable year-to-year")

    n = len(years)
    cols = 4
    rows = int(np.ceil(n / cols))

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[str(y) for y in years],
        horizontal_spacing=0.04, vertical_spacing=0.10,
    )

    for i, yr in enumerate(years):
        r = i // cols + 1
        c = i % cols + 1
        showscale = (i == 0)  # one shared colour bar
        fig.add_trace(make_heatmap(all_mats[yr], str(yr), showscale=showscale), row=r, col=c)
        fig.update_yaxes(autorange="reversed", row=r, col=c,
                         tickvals=[0, 6, 12, 18], title_text="Hr" if c == 1 else None)
        fig.update_xaxes(row=r, col=c, tickangle=0,
                         tickvals=MONTH_LABELS[::2])

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(family="IBM Plex Mono, monospace", color="#8b949e", size=10),
        margin=dict(l=40, r=20, t=40, b=30),
        height=300 * rows,
    )
    # Style the per-panel year titles
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(family="IBM Plex Mono, monospace", color="#58a6ff", size=13)

    st.plotly_chart(fig, use_container_width=True)

# ── Yearly trend bar (context below heatmaps) ──────────────────────────────────
st.markdown("---")
st.subheader("📈 Annual Share of Negative-Price Hours")
trend = worst_year_series.reset_index()
trend.columns = ["year", "pct"]

bar = go.Figure(go.Bar(
    x=trend["year"], y=trend["pct"],
    marker_color="#ff6b6b", opacity=0.85,
    hovertemplate="Year: %{x}<br>Negative: %{y:.2f}%<extra></extra>",
))
bar.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="Year", dtick=1, gridcolor="#21262d"),
    yaxis=dict(title="% of hours negative", gridcolor="#21262d"),
    margin=dict(l=60, r=20, t=20, b=50),
    height=320,
)
st.plotly_chart(bar, use_container_width=True)

# ── Data table ──────────────────────────────────────────────────────────────────
with st.expander("📋 Negative hours by month & year"):
    pivot = df.assign(neg=df["price"] < 0).groupby(["year", "month"])["neg"].mean().mul(100)
    pivot = pivot.unstack("month").reindex(columns=range(1, 13))
    pivot.columns = MONTH_LABELS
    st.dataframe(
        pivot.style.format("{:.1f}").background_gradient(cmap="Reds", axis=None),
        use_container_width=True,
    )
    csv = pivot.to_csv().encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"negative_prices_{market}.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Each cell = share of hours (in that hour-of-day & month) with day-ahead price below €0/MWh.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)