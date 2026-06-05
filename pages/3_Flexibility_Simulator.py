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
    page_icon="🔋",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }
.concept-box {
    background: #161b22; border-left: 3px solid #3fb950;
    border-radius: 0 6px 6px 0; padding: 0.9rem 1.2rem; margin: 1rem 0;
    font-size: 0.85rem; color: #8b949e; line-height: 1.6;
}
.concept-box strong { color: #e6edf3; }
.concept-box code {
    background: #0d1117; border: 1px solid #30363d; border-radius: 3px;
    padding: 1px 5px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; color: #56d364;
}
div[data-testid="stMetric"] {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem;
}
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
    # number of hours of charging/discharging capacity available per day
    n_slots = int(np.ceil(capacity_mwh / power_mw))

    # group indices by day
    idx = np.arange(len(df_day_prices))
    for _, grp in pd.DataFrame({"price": df_day_prices, "i": idx}).groupby(
            df_day_prices.index.date):
        p = grp["price"].values
        ii = grp["i"].values
        order = np.argsort(p)                 # cheapest first
        cheap = order[:n_slots]               # charge hours
        expensive = order[::-1][:n_slots]     # discharge hours
        energy_per_slot = min(power_mw, capacity_mwh / n_slots)
        for cj, dj in zip(cheap, expensive):
            buy_p, sell_p = p[cj], p[dj]
            if sell_p * eff > buy_p:           # profitable spread only
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
    action = np.zeros(n)  # -1 = curtailed
    # threshold: curtail the most expensive X% of hours
    thresh = np.percentile(prices, 100 - curtail_below_pct)
    thresh = max(thresh, shift_above)
    for i, p in enumerate(prices):
        if p > thresh:
            savings[i] = baseline_mw * p   # avoided buying at high price
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
        # saving = moving baseline_mw of load from expensive to cheap hours
        saving = baseline_mw * (p[expensive].sum() - p[cheap].sum())
        # attribute to the expensive hours that were avoided
        for ej in expensive:
            savings[ii[ej]] += baseline_mw * (p[ej] - p[cheap].mean())
    return savings


# ── Header ───────────────────────────────────────────────────────────────────
st.title("🔋 Flexibility Simulator")
st.markdown("""
<div class="concept-box">
<strong>From price data to euros.</strong>
A flexible asset earns money from <em>price spread</em> — buying (or avoiding) power when
it's cheap and selling (or shifting to) when it's expensive. As renewables deepen
volatility, that spread widens. This simulator quantifies the annual value for two asset
classes under two dispatch strategies. Adjust the parameters and watch the revenue update.
<br><br>
<code>Battery</code> = arbitrage on the price spread, limited by capacity & efficiency.
<code>Demand response</code> = savings from shifting industrial load away from peak prices.
</div>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Market & Year")
    market = st.selectbox("Market", list(PRICE_FILES.keys()), index=0)

    df_all = load_prices(market)
    years = sorted(df_all["year"].unique())
    sel_year = st.select_slider("Year", options=years, value=years[-1])

    st.markdown("### ⚙️ Asset Type")
    asset = st.radio("", ["Battery storage", "Demand response"], label_visibility="collapsed")

    st.markdown("### 🎯 Strategy")
    strategy = st.radio("", ["Threshold dispatch", "Daily optimal arbitrage"],
                        label_visibility="collapsed")

    st.markdown("---")
    if asset == "Battery storage":
        st.markdown("### 🔋 Battery Parameters")
        capacity = st.slider("Capacity (MWh)", 1, 100, 10)
        power    = st.slider("Power rating (MW)", 1, 50, 5)
        eff      = st.slider("Round-trip efficiency (%)", 50, 100, 90) / 100
        if strategy == "Threshold dispatch":
            charge_below    = st.slider("Charge when price below (€/MWh)", -50, 100, 20)
            discharge_above = st.slider("Discharge when price above (€/MWh)", 0, 300, 80)
    else:
        st.markdown("### 🏭 Demand Response Parameters")
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
st.markdown("---")
st.subheader(f"📊 {sel_year} Results — {market}")

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

# ── Chart 1: cumulative value over the year ────────────────────────────────────
st.markdown("---")
st.subheader(f"💶 Cumulative {unit} Through the Year")

df_sorted = df.sort_index()
df_sorted["cumulative"] = df_sorted["cashflow"].cumsum()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_sorted.index, y=df_sorted["cumulative"],
    mode="lines", line=dict(color="#3fb950", width=2),
    fill="tozeroy", fillcolor="rgba(63,185,80,0.1)",
    hovertemplate="%{x|%b %d}<br>Cumulative: €%{y:,.0f}<extra></extra>",
))
fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="Date", gridcolor="#21262d"),
    yaxis=dict(title=f"Cumulative {unit} (€)", gridcolor="#21262d"),
    margin=dict(l=70, r=20, t=20, b=50), height=380,
)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: a representative dispatch week ─────────────────────────────────────
st.markdown("---")
st.subheader("🔍 Dispatch Detail — Sample Week")
st.caption("A representative week showing how the asset responds to price signals")

# pick the week with the highest activity
df_sorted["week"] = df_sorted.index.isocalendar().week
week_activity = df_sorted.groupby("week")["cashflow"].apply(lambda s: s.abs().sum())
best_week = week_activity.idxmax()
wk = df_sorted[df_sorted["week"] == best_week]

fig2 = go.Figure()
# price line
fig2.add_trace(go.Scatter(
    x=wk.index, y=wk["price"], name="Price (€/MWh)",
    line=dict(color="#58a6ff", width=1.8), yaxis="y",
))
# charge / discharge markers
charge = wk[wk["action"] > 0]
discharge = wk[wk["action"] < 0]
fig2.add_trace(go.Scatter(
    x=charge.index, y=charge["price"], mode="markers", name="Charge / consume",
    marker=dict(color="#3fb950", size=8, symbol="triangle-down"),
))
fig2.add_trace(go.Scatter(
    x=discharge.index, y=discharge["price"], mode="markers", name="Discharge / curtail",
    marker=dict(color="#ff6b6b", size=8, symbol="triangle-up"),
))
fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="", gridcolor="#21262d"),
    yaxis=dict(title="Price (€/MWh)", gridcolor="#21262d"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1,
                orientation="h", y=1.12),
    margin=dict(l=60, r=20, t=40, b=40), height=380,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: value across ALL years (the thesis money-shot) ────────────────────
st.markdown("---")
st.subheader("📈 Flexibility Value Over Time — All Years")
st.caption("Re-runs the current asset & strategy for every year. Rising value = the thesis argument in euros.")

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

# assemble params for caching
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
    marker_color="#3fb950", opacity=0.85,
    hovertemplate="Year: %{x}<br>" + unit + ": €%{y:,.0f}<extra></extra>",
))
fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e"),
    xaxis=dict(title="Year", dtick=1, gridcolor="#21262d"),
    yaxis=dict(title=f"Annual {unit} (€)", gridcolor="#21262d"),
    margin=dict(l=70, r=20, t=20, b=50), height=360,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Simplified dispatch model for illustration — battery arbitrage uses a greedy daily heuristic,
not a full optimisation. Revenue is gross of capital, degradation, grid fees & taxes.
Source: ENTSO-E Transparency Platform day-ahead prices (2018–2024).
</div>
""", unsafe_allow_html=True)