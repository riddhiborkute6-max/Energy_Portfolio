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

/* Explanation boxes — red left border here specifically, since this page's
   subject (negative prices) is itself a "warning" signal */
.info-box {
    background: #131314; border-left: 3px solid #e05c5c;
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

.stSelectbox > div, .stRadio > div { background: transparent !important; }
hr { border-color: #232324; }
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

# Portfolio scope everywhere else is 2018–2024. Cap here too, in case a
# data file has extra rows (e.g. a partial 2025) that would otherwise
# silently sneak into the year list.
SCOPE_YEAR_MIN, SCOPE_YEAR_MAX = 2018, 2024


@st.cache_data(show_spinner="Loading price data…")
def load_prices(market_key: str) -> pd.DataFrame:
    """Load a single price series, clean the time index, return tidy frame."""
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
    out["year"]  = out.index.year
    out["month"] = out.index.month
    out["hour"]  = out.index.hour

    # Keep only the years this portfolio covers (2018–2024)
    out = out[(out["year"] >= SCOPE_YEAR_MIN) & (out["year"] <= SCOPE_YEAR_MAX)]
    return out


def build_heatmap_matrix(df_year: pd.DataFrame) -> pd.DataFrame:
    """
    For one year: return a 24 (hour) × 12 (month) matrix of the
    percentage of hours with negative price in each hour/month cell.
    """
    grp = df_year.groupby(["hour", "month"])
    neg = grp["price"].apply(lambda s: 100 * (s < 0).mean())
    mat = neg.unstack("month")
    mat = mat.reindex(index=range(24), columns=range(1, 13))
    return mat


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow">Independent Research · Tool 2 of 4</div>', unsafe_allow_html=True)
st.title("Negative Price Heatmap")

st.markdown("""
<div class="body-text">
Sometimes electricity prices go below zero — generators effectively pay the grid to take
their power. This happens when inflexible supply (renewables that can't easily switch off,
plus baseload plants that are slow or costly to shut down) exceeds demand. This page maps
exactly <em>when</em> that happens across the day and year — and those same windows are
precisely when a flexible industrial asset (a battery, a factory that can shift load) can get
paid to consume power instead of paying for it.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<strong>How to read the grid.</strong><br>
Each cell is one hour-of-day (rows, 00–23) × one month (columns, Jan–Dec). The color in each
cell is <code>% of hours in that slot, across the whole year, where price fell below €0/MWh</code>.
A dark cell means that hour/month combination almost never sees negative prices. A bright red
cell means it happens often — usually midday hours in sunny months (solar oversupply) or
overnight in windy months (wind oversupply with low demand).
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Market</div>', unsafe_allow_html=True)
    market = st.selectbox("Select market", list(PRICE_FILES.keys()), index=0)

    st.markdown('<div class="section-label">View Mode</div>', unsafe_allow_html=True)
    view_mode = st.radio(
        "Comparison layout",
        ["Small multiples (all years)", "Single year"],
        index=0,
        help="Small multiples show every year side by side. Single year zooms into one."
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#8f8c86; font-family: "IBM Plex Mono", monospace; line-height:1.8;'>
    Cell value = % of hours in that<br>
    hour-of-day & month with<br>
    price &lt; €0/MWh.<br><br>
    Data: ENTSO-E (2018–2024)
    </div>
    """, unsafe_allow_html=True)

# ── Load & prepare ──────────────────────────────────────────────────────────────
df = load_prices(market)
years = sorted(df["year"].unique())

if not years:
    st.error(
        f"No data in the 2018–2024 range was found for {market}. "
        "Check that the parquet file actually contains rows in this period."
    )
    st.stop()

if view_mode == "Single year":
    with st.sidebar:
        st.markdown('<div class="section-label">Year</div>', unsafe_allow_html=True)
        sel_year = st.select_slider("Choose year", options=years, value=years[-1])

# ── KPI strip ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Key Statistics</div>', unsafe_allow_html=True)
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
all_mats = {yr: build_heatmap_matrix(df[df["year"] == yr]) for yr in years}

# Flag years with essentially no data, instead of silently rendering a blank panel
empty_years = [yr for yr, m in all_mats.items() if not m.notna().any().any()]
if empty_years:
    st.warning(
        f"No price data found for: {', '.join(str(y) for y in empty_years)} in {market}. "
        "These panels will render empty below — this reflects a gap in the underlying "
        "parquet file for that year, not a charting issue."
    )

global_max = max((m.max().max() for m in all_mats.values() if m.notna().any().any()),
                 default=5.0)
global_max = max(global_max, 1.0)

# Dark charcoal → teal (mild) → amber (moderate) → red (severe): ties the
# heatmap into the same palette as the rest of the site while keeping red
# as the universally-understood "this is bad" signal at the high end.
COLORSCALE = [
    [0.0, "#131314"],
    [0.2, "#1c4b46"],
    [0.45, "#2dd4bf"],
    [0.7, "#f0a860"],
    [1.0, "#e05c5c"],
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


PLOT_FONT = dict(family="'IBM Plex Mono', monospace", color="#8f8c86")
PLOT_BG   = "#131314"

# ── Render ────────────────────────────────────────────────────────────────────
if view_mode == "Single year":
    st.markdown(f'<div class="section-label">{market} — {sel_year}</div>', unsafe_allow_html=True)
    st.caption("Brighter red = more frequent negative prices in that hour & month")

    mat = all_mats[sel_year]
    fig = go.Figure(make_heatmap(mat, str(sel_year), showscale=True))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=PLOT_FONT,
        xaxis=dict(title="Month", side="bottom"),
        yaxis=dict(title="Hour of day", autorange="reversed"),
        margin=dict(l=60, r=20, t=20, b=50),
        height=520,
    )
    st.plotly_chart(fig, use_container_width=True)

else:  # Small multiples
    st.markdown(f'<div class="section-label">{market} — All Years</div>', unsafe_allow_html=True)
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
        showscale = (i == 0)
        fig.add_trace(make_heatmap(all_mats[yr], str(yr), showscale=showscale), row=r, col=c)
        fig.update_yaxes(autorange="reversed", row=r, col=c,
                         tickvals=[0, 6, 12, 18], title_text="Hr" if c == 1 else None)
        fig.update_xaxes(row=r, col=c, tickangle=0,
                         tickvals=MONTH_LABELS[::2])

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="'IBM Plex Mono', monospace", color="#8f8c86", size=10),
        margin=dict(l=40, r=20, t=40, b=30),
        height=300 * rows,
    )
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(family="'IBM Plex Mono', monospace", color="#2dd4bf", size=13)

    st.plotly_chart(fig, use_container_width=True)

# ── Yearly trend bar (context below heatmaps) ──────────────────────────────────
st.markdown('<div class="section-label">Annual Share of Negative-Price Hours</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
One bar per year — the share of all hours that year with a negative price. A rising trend
means oversupply is becoming more frequent, which directly strengthens the case for
flexible assets that can consume during exactly those hours.
</div>
""", unsafe_allow_html=True)

trend = worst_year_series.reset_index()
trend.columns = ["year", "pct"]

bar = go.Figure(go.Bar(
    x=trend["year"], y=trend["pct"],
    marker_color="#e05c5c", opacity=0.85,
    hovertemplate="Year: %{x}<br>Negative: %{y:.2f}%<extra></extra>",
))
bar.update_layout(
    template="plotly_dark",
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=PLOT_FONT,
    xaxis=dict(title="Year", dtick=1, gridcolor="#232324"),
    yaxis=dict(title="% of hours negative", gridcolor="#232324"),
    margin=dict(l=60, r=20, t=20, b=50),
    height=320,
)
st.plotly_chart(bar, use_container_width=True)

# ── Data table ──────────────────────────────────────────────────────────────────
with st.expander("Negative hours by month & year"):
    pivot = df.assign(neg=df["price"] < 0).groupby(["year", "month"])["neg"].mean().mul(100)
    pivot = pivot.unstack("month").reindex(columns=range(1, 13))
    pivot.columns = MONTH_LABELS
    st.dataframe(
        pivot.style.format("{:.1f}").background_gradient(cmap="Reds", axis=None),
        use_container_width=True,
    )
    csv = pivot.to_csv().encode("utf-8")
    st.download_button("Download CSV", csv, f"negative_prices_{market}.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.75rem; color:#4a4a48; font-family: "IBM Plex Mono", monospace; text-align:center;'>
Each cell = share of hours (in that hour-of-day & month) with day-ahead price below €0/MWh.
Source: ENTSO-E Transparency Platform (2018–2024).
</div>
""", unsafe_allow_html=True)
