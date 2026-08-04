"""
pages/3_Flexibility_Simulator.py
---------------------------------
Flexibility Simulator — Riddhi Borkute's Energy Portfolio

Turns hourly price data into euros: simulates the revenue a flexible
industrial asset can earn by responding to price volatility.

Asset types:   Battery storage  |  Demand response
Strategies:    Threshold dispatch  |  Daily optimal arbitrage
Output:        Annual revenue, dispatch profile, sensitivity to parameters.

This is the direct quantification of the thesis argument: as renewable
penetration deepens price volatility (cannibalization + negative prices),
the value of flexibility rises.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flexibility Simulator | Energy Portfolio",
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

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
PRICE_FILES = {
    "Germany (DE)":       "prices_DE.parquet",
    "Netherlands (NL)":   "prices_NL.parquet",
    "Denmark West (DK1)": "prices_DK1.parquet",
    "Denmark East (DK2)": "prices_DK2.parquet",
}

# Portfolio scope everywhere is 2018–2024 — enforced here at load time so it
# can't be bypassed by a stray year in the underlying parquet file.
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
    out["date"] = out.index.date

    # Keep only 2018–2024, matching the rest of the portfolio
    out = out[(out["year"] >= SCOPE_YEAR_MIN) & (out["year"] <= SCOPE_YEAR_MAX)]
    return out


# ── Battery simulation ─────────────────────────────────────────────────────────
def simulate_battery_threshold(prices, capacity_mwh, power_mw, eff,
                               charge_below, discharge_above):
    """
    Threshold dispatch: charge when price < charge_below, discharge when
    price > discharge_above. One-hour steps. SoC bounded [0, capacity].
    Returns (cashflow array, soc array, action array).
    eff = round-trip efficiency (applied on discharge).
    """
    n = len(prices)
    soc = 0.0
    cash = np.zeros(n)
    soc_track = np.zeros(n)
    action = np.zeros(n)  # +1 charge, -1 discharge, 0 idle
    for i, p in enumerate(prices):
        if p < charge_below and soc < capacity_mwh:
            e = min(power_mw, capacity_mwh - soc)   # MWh charged this hour
            soc += e
            cash[i] = -p * e                        # pay to charge
            action[i] = 1
        elif p > discharge_above and soc > 0:
            e = min(power_mw, soc)                  # MWh discharged
            soc -= e
            cash[i] = p * e * eff                   # earn (after losses)
            action[i] = -1
        soc_track[i] = soc
    return cash, soc_track, action


def simulate_battery_arbitrage(df_day_prices, capacity_mwh, power_mw, eff):
    """
    Daily optimal arbitrage (greedy):
      - rank hours by price
      - charge during the cheapest hours up to capacity (power-limited)
      - discharge during the most expensive hours
      - only execute pairs where discharge_price*eff > charge_price
    Operates day by day; returns total daily cashflows.
    Approximation suitable for a portfolio-grade simulator (not an LP solver).
    """
    cash_total = np.zeros(len(df_day_prices))
    n_slots = int(np.ceil(capacity_mwh / power_mw))

    idx = np.arange(len(df_day_prices))
    for _, grp in pd.DataFrame({"price": df_day_prices, "i": idx}).groupby(
            df_day_prices.index.date):
        p = grp["price"].values
        ii = grp["i"].values
        order = np.argsort(p)
        cheap = order[:n_slots]
        expensive = order[::-1][:n_slots]
        energy_per_slot = min(power_mw, capacity_mwh / n_slots)
        for cj, dj in zip(cheap, expensive):
            buy_p, sell_p = p[cj], p[dj]
            if sell_p * eff > buy_p:
                cash_total[ii[cj]] += -buy_p * energy_per_slot
                cash_total[ii[dj]] += sell_p * energy_per_slot * eff
    return cash_total


# ── Demand response simulation ─────────────────────────────────────────────────
def simulate_dr_threshold(prices, baseline_mw, curtail_below_pct, shift_above):
    """
    Demand response (threshold): a process normally consuming baseline_mw.
    - When price > shift_above: curtail/shift load away (avoid buying high) → saving.
    - Baseline cost is always paid; we measure SAVINGS vs always-on baseline.
    Returns savings array (€ saved vs naive baseline) and an action array.
    """
    n = len(prices)
    savings = np.zeros(n)
    action = np.zeros(n)
    thresh = np.percentile(prices, 100 - curtail_below_pct)
    thresh = max(thresh, shift_above)
    for i, p in enumerate(prices):
        if p > thresh:
            savings[i] = baseline_mw * p
            action[i] = -1
    return savings, action


def simulate_dr_arbitrage(df_prices, baseline_mw, flex_hours_per_day):
    """
    Demand response (daily optimal): each day, shift `flex_hours_per_day`
    of consumption from the most expensive hours to the cheapest hours.
    Returns daily savings (€) vs running flat across the day.
    """
    savings = np.zeros(len(df_prices))
    idx = np.arange(len(df_prices))
    for _, grp in pd.DataFrame({"price": df_prices.values, "i": idx},
                               index=df_prices.index).groupby(df_prices.index.date):
        p = grp["price"].values
        ii = grp["i"].values
        k = min(flex_hours_per_day, len(p) // 2)
        if k < 1:
            continue
        order = np.argsort(p)
        cheap = order[:k]
        expensive = order[::-1][:k]
        saving = baseline_mw * (p[expensive].sum() - p[cheap].sum())
        for ej in expensive:
            savings[ii[ej]] += baseline_mw * (p[ej] - p[cheap].mean())
    return savings


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow">Independent Research · Tool 3 of 4</div>', unsafe_allow_html=True)
st.title("Flexibility Simulator")

st.markdown("""
<div class="body-text">
The previous two tools show <em>why</em> price volatility exists — solar and wind cannibalizing
their own value, oversupply pushing prices negative. This tool turns that volatility directly
into euros: how much can a flexible asset actually earn by responding to it? Pick an asset,
pick a strategy, and the simulation runs against real historical hourly prices.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<strong>How the two asset types earn money.</strong><br>
<code>Battery storage</code> — buys (charges) power when it's cheap and sells (discharges) it
when it's expensive, earning the price spread minus round-trip losses.<br>
<code>Demand response</code> — doesn't store anything; it just avoids buying power during
expensive hours, or shifts consumption from expensive hours to cheap ones. The "revenue" here
is really <em>savings</em> versus a business that always runs on a flat schedule.<br><br>
Both strategy options do the same underlying thing at different levels of sophistication:
<strong>Threshold dispatch</strong> reacts to fixed price levels you set (simple, realistic for
an actual control system). <strong>Daily optimal arbitrage</strong> assumes perfect foresight
within each day and picks the best possible hours (an upper-bound estimate, not what a
real system would achieve).
</div>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Market & Year</div>', unsafe_allow_html=True)
    market = st.selectbox("Market", list(PRICE_FILES.keys()), index=0)

    df_all = load_prices(market)
    years = sorted(df_all["year"].unique())
    if not years:
        st.error(f"No data in the 2018–2024 range was found for {market}.")
        st.stop()
    sel_year = st.select_slider("Year", options=years, value=years[-1])

    st.markdown('<div class="section-label">Asset Type</div>', unsafe_allow_html=True)
    asset = st.radio("Asset Type", ["Battery storage", "Demand response"], label_visibility="collapsed")

    st.markdown('<div class="section-label">Strategy</div>', unsafe_allow_html=True)
    strategy = st.radio("Strategy", ["Threshold dispatch", "Daily optimal arbitrage"],
                        label_visibility="collapsed")

    st.markdown("---")
    if asset == "Battery storage":
        st.markdown('<div class="section-label">Battery Parameters</div>', unsafe_allow_html=True)
        capacity = st.slider("Capacity (MWh)", 1, 100, 10)
        power    = st.slider("Power rating (MW)", 1, 50, 5)
        eff      = st.slider("Round-trip efficiency (%)", 50, 100, 90) / 100
        if strategy == "Threshold dispatch":
            charge_below    = st.slider("Charge when price below (€/MWh)", -50, 100, 20)
            discharge_above = st.slider("Discharge when price above (€/MWh)", 0, 300, 80)
    else:
        st.markdown('<div class="section-label">Demand Response Parameters</div>', unsafe_allow_html=True)
        baseline = st.slider("Flexible load (MW)", 1, 50, 5)
        if strategy == "Threshold dispatch":
            curtail_pct = st.slider("Curtail top % of hours", 1, 30, 10)
            shift_above = st.slider("Only curtail above (€/MWh)", 0, 300, 60)
        else:
            flex_hours = st.slider("Flexible hours per day", 1, 12, 4)

# ── Run the selected simulation ──────────────────────────────────────────────────
df = df_all[df_all["year"] == sel_year].copy()
prices = df["price"]

if asset == "Battery storage":
    if strategy == "Threshold dispatch":
        cash, soc, action = simulate_battery_threshold(
            prices.values, capacity, power, eff, charge_below, discharge_above)
        df["cashflow"] = cash
        df["soc"] = soc
        df["action"] = action
        cycles = np.sum(np.abs(np.diff(soc, prepend=0)) > 0) / 2 / max(capacity, 1)
    else:
        cash = simulate_battery_arbitrage(prices, capacity, power, eff)
        df["cashflow"] = cash
        df["action"] = np.sign(cash)
        df["soc"] = np.nan
    unit = "Revenue"
else:
    if strategy == "Threshold dispatch":
        sav, action = simulate_dr_threshold(prices.values, baseline, curtail_pct, shift_above)
        df["cashflow"] = sav
        df["action"] = action
    else:
        sav = simulate_dr_arbitrage(prices, baseline, flex_hours)
        df["cashflow"] = sav
        df["action"] = np.sign(sav)
    unit = "Savings"

total_value = df["cashflow"].sum()
active_hours = int((df["action"] != 0).sum())

# ── Headline metrics ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-label">{sel_year} Results — {market}</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Annual {unit.lower()}", f"€{total_value:,.0f}")
m2.metric("Active hours", f"{active_hours:,}", f"{100*active_hours/len(df):.1f}% of year")
if asset == "Battery storage":
    energy_label = f"€{total_value/capacity:,.0f}/MWh"
    m3.metric("Value per MWh capacity", energy_label,
              help="Annual revenue divided by battery capacity")
else:
    m3.metric("Value per MW", f"€{total_value/baseline:,.0f}/MW",
              help="Annual savings divided by flexible load")
price_spread = prices.quantile(0.9) - prices.quantile(0.1)
m4.metric("Price spread (P90–P10)", f"€{price_spread:,.0f}/MWh",
          help="Wider spread = more flexibility value available")

st.markdown("""
<div class="info-box" style="font-size:0.85rem;">
<strong>What these four numbers mean together:</strong> the total euro figure is the headline,
but <em>active hours</em> tells you how often the asset actually had to act to earn it — fewer
hours for the same money means a more efficient strategy. The per-MWh / per-MW figures let you
compare markets or years on equal footing regardless of how big the asset is. The price spread
is the underlying opportunity: if it's small, no strategy will earn much, no matter how it's
tuned.
</div>
""", unsafe_allow_html=True)

# ── Chart 1: cumulative value over the year ────────────────────────────────────
st.markdown(f'<div class="section-label">Cumulative {unit} Through the Year</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
Running total of euros earned or saved, hour by hour across the year. The steepness of the
climb shows when the asset was doing the most work — flat stretches mean the price spread that
day wasn't wide enough to act on.
</div>
""", unsafe_allow_html=True)

df_sorted = df.sort_index()
df_sorted["cumulative"] = df_sorted["cashflow"].cumsum()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_sorted.index, y=df_sorted["cumulative"],
    mode="lines", line=dict(color="#f0a860", width=2),
    fill="tozeroy", fillcolor="rgba(240,168,96,0.12)",
    hovertemplate="%{x|%b %d}<br>Cumulative: €%{y:,.0f}<extra></extra>",
))
fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131314", plot_bgcolor="#131314",
    font=dict(family="'IBM Plex Mono', monospace", color="#8f8c86"),
    xaxis=dict(title="Date", gridcolor="#232324"),
    yaxis=dict(title=f"Cumulative {unit} (€)", gridcolor="#232324"),
    margin=dict(l=70, r=20, t=20, b=50), height=380,
)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: a representative dispatch week ─────────────────────────────────────
st.markdown('<div class="section-label">Dispatch Detail — Sample Week</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
The single busiest week of the year for this asset and strategy, zoomed in hour by hour. The
teal line is the market price; the markers show exactly when the asset chose to act —
<span class="accent">amber triangles</span> mark charging/consuming during cheap hours, and
the downward markers mark discharging/curtailing during expensive ones.
</div>
""", unsafe_allow_html=True)

df_sorted["week"] = df_sorted.index.isocalendar().week
week_activity = df_sorted.groupby("week")["cashflow"].apply(lambda s: s.abs().sum())
best_week = week_activity.idxmax()
wk = df_sorted[df_sorted["week"] == best_week]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=wk.index, y=wk["price"], name="Price (€/MWh)",
    line=dict(color="#2dd4bf", width=1.8), yaxis="y",
))
charge = wk[wk["action"] > 0]
discharge = wk[wk["action"] < 0]
fig2.add_trace(go.Scatter(
    x=charge.index, y=charge["price"], mode="markers", name="Charge / consume",
    marker=dict(color="#f0a860", size=8, symbol="triangle-down"),
))
fig2.add_trace(go.Scatter(
    x=discharge.index, y=discharge["price"], mode="markers", name="Discharge / curtail",
    marker=dict(color="#e05c5c", size=8, symbol="triangle-up"),
))
fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131314", plot_bgcolor="#131314",
    font=dict(family="'IBM Plex Mono', monospace", color="#8f8c86"),
    xaxis=dict(title="", gridcolor="#232324"),
    yaxis=dict(title="Price (€/MWh)", gridcolor="#232324"),
    legend=dict(bgcolor="#131314", bordercolor="#232324", borderwidth=1,
                orientation="h", y=1.12),
    margin=dict(l=60, r=20, t=40, b=40), height=380,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: value across ALL years (the thesis money-shot) ────────────────────
st.markdown('<div class="section-label">Flexibility Value Over Time — All Years</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text" style="font-size:0.92rem;">
Re-runs the current asset and strategy, unchanged, against every year of data (2018–2024).
This is the central argument of the whole portfolio made concrete: if this bar chart trends
upward, it means the same fixed asset earns more money every year — not because the asset
changed, but because rising renewable penetration is widening the price spread it profits from.
</div>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Simulating all years…")
def value_by_year(market_key, asset_type, strat, params):
    """Run the chosen simulation across every year, return €/year."""
    data = load_prices(market_key)
    results = {}
    for yr in sorted(data["year"].unique()):
        d = data[data["year"] == yr]
        p = d["price"]
        if asset_type == "Battery storage":
            if strat == "Threshold dispatch":
                c, _, _ = simulate_battery_threshold(
                    p.values, params["capacity"], params["power"], params["eff"],
                    params["charge_below"], params["discharge_above"])
            else:
                c = simulate_battery_arbitrage(p, params["capacity"], params["power"], params["eff"])
        else:
            if strat == "Threshold dispatch":
                c, _ = simulate_dr_threshold(p.values, params["baseline"],
                                             params["curtail_pct"], params["shift_above"])
            else:
                c = simulate_dr_arbitrage(p, params["baseline"], params["flex_hours"])
        results[yr] = float(np.sum(c))
    return results

if asset == "Battery storage":
    params = dict(capacity=capacity, power=power, eff=eff,
                  charge_below=charge_below if strategy == "Threshold dispatch" else 0,
                  discharge_above=discharge_above if strategy == "Threshold dispatch" else 0)
else:
    params = dict(baseline=baseline,
                  curtail_pct=curtail_pct if strategy == "Threshold dispatch" else 0,
                  shift_above=shift_above if strategy == "Threshold dispatch" else 0,
                  flex_hours=flex_hours if strategy == "Daily optimal arbitrage" else 0)

yearly = value_by_year(market, asset, strategy, params)
yr_df = pd.DataFrame({"year": list(yearly.keys()), "value": list(yearly.values())})

fig3 = go.Figure(go.Bar(
    x=yr_df["year"], y=yr_df["value"],
    marker_color="#f0a860", opacity=0.85,
    hovertemplate="Year: %{x}<br>" + unit + ": €%{y:,.0f}<extra></extra>",
))
fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131314", plot_bgcolor="#131314",
    font=dict(family="'IBM Plex Mono', monospace", color="#8f8c86"),
    xaxis=dict(title="Year", dtick=1, gridcolor="#232324"),
    yaxis=dict(title=f"Annual {unit} (€)", gridcolor="#232324"),
    margin=dict(l=70, r=20, t=20, b=50), height=360,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.75rem; color:#4a4a48; font-family: "IBM Plex Mono", monospace; text-align:center;'>
Simplified dispatch model for illustration — battery arbitrage uses a greedy daily heuristic,
not a full optimisation. Revenue is gross of capital, degradation, grid fees & taxes.
Source: ENTSO-E Transparency Platform day-ahead prices (2018–2024).
</div>
""", unsafe_allow_html=True)
