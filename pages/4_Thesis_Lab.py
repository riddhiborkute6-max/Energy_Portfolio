"""
pages/4_Thesis_Lab.py
--------------------------
Research Notes — Riddhi Borkute's Energy Portfolio

A working research workspace: literature notes, data-source documentation,
and a log of analytical decisions. Content lives in plain Python lists/dicts
below — edit those to add your own notes. Everything marked [EDIT] or left
as a short stub is yours to expand in your own words.

Structured so it doubles as: (1) your thesis literature workspace, and
(2) evidence of analytical depth for a hiring manager.
"""

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Notes | Energy Portfolio",
    page_icon="📓",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }

.note-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 1.3rem 1.5rem; margin-bottom: 1.1rem;
}
.note-card .citation {
    font-family: 'IBM Plex Mono', monospace; color: #58a6ff;
    font-size: 1rem; font-weight: 600; margin-bottom: 0.3rem;
}
.note-card .meta {
    font-size: 0.75rem; color: #6e7681; margin-bottom: 0.8rem;
    font-family: 'IBM Plex Mono', monospace;
}
.note-card .takeaway { color: #adbac7; line-height: 1.65; font-size: 0.92rem; }
.note-card .relevance {
    margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid #21262d;
    color: #8b949e; font-size: 0.85rem; line-height: 1.6;
}
.note-card .relevance strong { color: #3fb950; }

.tag {
    display: inline-block; background: #1c2333; border: 1px solid #30363d;
    border-radius: 20px; padding: 2px 10px; margin: 2px 4px 2px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #79c0ff;
}
.data-row {
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 0.9rem 1.2rem; margin-bottom: 0.7rem;
}
.data-row .name {
    font-family: 'IBM Plex Mono', monospace; color: #58a6ff; font-weight: 600;
}
.data-row .detail { color: #8b949e; font-size: 0.85rem; line-height: 1.55; }
.stub { color: #6e7681; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📓 Research Notes")
st.markdown("""
<div style='color:#8b949e; font-size:0.92rem; line-height:1.65; max-width:780px;'>
Working notes behind this portfolio and thesis — key literature, the data underpinning
every chart, and the analytical decisions made along the way. These are living notes,
written in my own words and expanded as the research develops.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_lit, tab_data, tab_decisions = st.tabs(
    ["📚 Literature", "🗄️ Data Sources", "🧭 Analytical Decisions"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LITERATURE
# ══════════════════════════════════════════════════════════════════════════════
# Edit this list to add/expand notes. 'takeaway' and 'relevance' are where you
# write in your own words. Keep them short here; expand as you read more.
literature = [
    {
        "citation": "Hirth (2013)",
        "meta": "The Market Value of Variable Renewables · Energy Economics",
        "tags": ["market value", "VRE", "foundational"],
        "takeaway": "[EDIT: your own summary] Establishes that the market value of "
                    "variable renewables falls as their share rises, because they "
                    "generate simultaneously and depress prices in their own production hours.",
        "relevance": "Defines the cannibalization mechanism my thesis builds on — but "
                     "I treat it as one input among several, not the sole anchor.",
    },
    {
        "citation": "López Prol & Schill (2021)",
        "meta": "[EDIT: full title & journal]",
        "tags": ["solar value", "empirical"],
        "takeaway": "[EDIT: your own summary — what did they find about how solar's "
                    "value declines with penetration, and over what range?]",
        "relevance": "[EDIT: how this informs your capture-ratio methodology.]",
    },
    {
        "citation": "Stiewe et al. (2025)",
        "meta": "[EDIT: full title & journal]",
        "tags": ["cross-border", "cannibalization"],
        "takeaway": "[EDIT: your own summary — the cross-border dimension of "
                    "cannibalization and why interconnection matters.]",
        "relevance": "[EDIT: connects to your DE/NL/DK multi-market comparison — "
                     "the markets aren't independent.]",
    },
    {
        "citation": "Peña et al. (2022)",
        "meta": "[EDIT: full title & journal]",
        "tags": ["flexibility", "storage value"],
        "takeaway": "[EDIT: your own summary — what they show about the value of "
                    "flexibility / storage under high renewables.]",
        "relevance": "[EDIT: underpins your Flexibility Simulator assumptions.]",
    },
]

with tab_lit:
    st.markdown("""
    <div style='color:#8b949e; font-size:0.85rem; margin-bottom:1rem;'>
    Core references for the thesis. Notes are mine, in my own words — summaries here
    are deliberately brief and expand in the full thesis document.
    </div>
    """, unsafe_allow_html=True)

    for note in literature:
        tags_html = "".join(f"<span class='tag'>{t}</span>" for t in note["tags"])
        st.markdown(f"""
        <div class="note-card">
            <div class="citation">{note['citation']}</div>
            <div class="meta">{note['meta']}</div>
            <div>{tags_html}</div>
            <div class="takeaway" style="margin-top:0.8rem;">{note['takeaway']}</div>
            <div class="relevance"><strong>Relevance to thesis:</strong> {note['relevance']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='color:#6e7681; font-size:0.8rem; font-style:italic; margin-top:0.5rem;'>
    To add a paper: edit the <code>literature</code> list near the top of this file.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA SOURCES
# ══════════════════════════════════════════════════════════════════════════════
data_sources = [
    {
        "name": "ENTSO-E Transparency Platform",
        "detail": "Primary data source. Hourly day-ahead prices (€/MWh) and actual "
                  "wind & solar generation for DE, NL, DK1, DK2, covering 2018–2024. "
                  "Accessed via the entsoe-py Python client and stored locally as "
                  "parquet files. ~54,800 hourly rows per market.",
    },
    {
        "name": "energy-charts.info (Fraunhofer ISE)",
        "detail": "Cross-reference for sanity-checking generation and price patterns. "
                  "[EDIT: note any specific checks you ran against it.]",
    },
    {
        "name": "Agora Energiewende reports",
        "detail": "Context for market structure and policy framing. "
                  "[EDIT: cite specific reports you drew on.]",
    },
]

with tab_data:
    st.markdown("""
    <div style='color:#8b949e; font-size:0.85rem; margin-bottom:1rem;'>
    Every chart in this portfolio traces back to these sources. Raw data is processed
    into hourly time series, de-duplicated (DST handling), and cached for performance.
    </div>
    """, unsafe_allow_html=True)

    for ds in data_sources:
        st.markdown(f"""
        <div class="data-row">
            <div class="name">{ds['name']}</div>
            <div class="detail">{ds['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Processing pipeline")
    st.markdown("""
    <div style='color:#adbac7; font-size:0.88rem; line-height:1.7;'>
    1. Pull hourly series per market via <code>entsoe-py</code><br>
    2. Store as parquet (<code>data/</code>, git-ignored to keep the repo light)<br>
    3. On load: parse timestamps → sort → drop duplicate hours (October DST fall-back)<br>
    4. Merge price + wind + solar on the time index<br>
    5. Cache with <code>@st.cache_data</code> so widgets re-run instantly
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYTICAL DECISIONS
# ══════════════════════════════════════════════════════════════════════════════
# A log of choices + rationale. This is what separates a portfolio from a demo —
# it shows you made deliberate, defensible methodological calls.
decisions = [
    {
        "q": "How is the capture price ratio defined?",
        "a": "Time-weighted average price during a technology's generation hours, "
             "divided by the overall average market price. A ratio below 1.0 confirms "
             "cannibalization. [EDIT: note any refinements, e.g. weighting by generation volume.]",
    },
    {
        "q": "Why a percentage (not count) for the negative-price heatmap?",
        "a": "Cells show the share of hours that went negative, not the raw count, so "
             "months of different lengths are comparable and the colour scale is honest.",
    },
    {
        "q": "Why a greedy heuristic for battery arbitrage instead of full optimisation?",
        "a": "A daily greedy pairing (cheapest-charge ↔ priciest-discharge, profitable spreads only) "
             "is transparent and slightly conservative — it understates the theoretical maximum "
             "an LP solver would find. For a portfolio tool, defensible and interpretable beats "
             "marginally higher but opaque. [EDIT: note if you later add an LP version.]",
    },
    {
        "q": "How are duplicate timestamps handled?",
        "a": "The October DST fall-back produces a repeated 02:00 hour in ENTSO-E data. "
             "I keep the first occurrence — a single hour per year has negligible effect "
             "on annual aggregates.",
    },
    {
        "q": "[EDIT: add your next decision here]",
        "a": "[EDIT: e.g. why you chose median-based penetration proxy, how you handle "
             "missing data, currency/unit conventions, etc.]",
    },
]

with tab_decisions:
    st.markdown("""
    <div style='color:#8b949e; font-size:0.85rem; margin-bottom:1rem;'>
    A running log of the methodological choices behind the analysis — what I decided,
    and why. These are the questions a supervisor (or interviewer) is most likely to ask.
    </div>
    """, unsafe_allow_html=True)

    for d in decisions:
        with st.expander(d["q"]):
            st.markdown(f"<div style='color:#adbac7; line-height:1.65;'>{d['a']}</div>",
                        unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Living research notes · expanded as the thesis develops · Riddhi Borkute
</div>
""", unsafe_allow_html=True)