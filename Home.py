"""
Home.py
--------
Landing page — Riddhi Borkute's Energy Portfolio
"""

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Riddhi Borkute | Energy Portfolio",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme: warm charcoal + single copper accent ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0c0c0d; color: #e9e7e2; }

h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #f2f0eb !important; }

/* Hero */
.hero { padding: 2.5rem 0 1.5rem 0; border-bottom: 1px solid #232324; margin-bottom: 2rem; }
.hero .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #8b5cf6; margin-bottom: 0.6rem;
}
.hero h1 { font-size: 2.4rem !important; line-height: 1.15; margin: 0 0 0.9rem 0; }
.hero .lede { font-size: 1.05rem; color: #a7a49d; max-width: 760px; line-height: 1.7; }

/* Section labels */
.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.76rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: #6f6d68;
    margin: 2.2rem 0 0.9rem 0; border-left: 2px solid #8b5cf6; padding-left: 0.6rem;
}

/* Body copy */
.body-text { color: #b7b4ac; font-size: 0.98rem; line-height: 1.75; max-width: 780px; }
.body-text strong { color: #f2f0eb; }
.body-text .accent { color: #f0a860; font-weight: 600; }

/* Tags */
.tag {
    display: inline-block; background: #17171a; border: 1px solid #2a2a2c;
    border-radius: 20px; padding: 3px 12px; margin: 3px 6px 3px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #a7a49d;
}

/* Cards */
.card {
    background: #131314; border: 1px solid #232324; border-radius: 10px;
    padding: 1.3rem 1.4rem; height: 100%;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.card:hover { border-color: #8b5cf6; transform: translateY(-2px); }
.card .icon { font-size: 1.5rem; color: #8b5cf6; }
.card .title {
    font-family: 'IBM Plex Mono', monospace; color: #f2f0eb;
    font-size: 1.0rem; font-weight: 600; margin: 0.5rem 0 0.4rem 0;
}
.card .desc { color: #8f8c86; font-size: 0.85rem; line-height: 1.55; }

/* Streamlit's own page_link buttons, restyled to match */
[data-testid="stPageLink"] {
    border: 1px solid #232324; border-radius: 8px; background: #131314;
}
[data-testid="stPageLink"]:hover { border-color: #8b5cf6; }

hr { border-color: #232324; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Energy Portfolio")
    st.markdown("""
    <div style='font-size:0.82rem; color:#a7a49d; line-height:1.6;'>
    <strong style='color:#f2f0eb;'>Riddhi Borkute</strong><br>
    MSc Global Production Engineering · TU Berlin<br><br>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#8f8c86; line-height:1.8;'>
    📍 Berlin, Germany<br>
    🔗 <a href='https://linkedin.com/in/riddhi-borkute' style='color:#8b5cf6;' target='_blank'>LinkedIn</a><br>
    💻 <a href='https://github.com/riddhiborkute6-max' style='color:#8b5cf6;' target='_blank'>GitHub</a><br>
    ✉️ <a href='mailto:riddhiborkute6@gmail.com' style='color:#8b5cf6;'>Email</a>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="eyebrow">Energy Market & Asset Analyst · Berlin</div>
    <h1>About Me</h1>
</div>
""", unsafe_allow_html=True)

# ── About Me (background, from CV) ────────────────────────────────────────────
st.markdown("""
<div class="body-text">
I'm an MSc Global Production Engineering student at TU Berlin (GPA 1.3), moving from a
mechanical engineering background into quantitative energy-market analysis. I currently work
as a <span class="accent">Working Student in Energy Storage and Flexibility Analytics at neustrom GmbH</span>
in Berlin, where I size and configure battery storage systems for industrial and commercial
clients, build dispatch strategies for storage co-located with solar and wind, and develop
Python-based market models on day-ahead price and generation data — translating that analysis
into client-facing decision tools.
<br><br>
Before moving into energy, I spent two years as an engineer at John Deere in Pune, India,
running Value Engineering workshops and building Power BI / Tableau reporting that standardised
cost and performance tracking across plants in India, Europe and the US.
<br><br>
<span style="color:#8f8c86; font-size:0.9rem;">
Available from November 2026 &nbsp;·&nbsp; English (C1), German (A2), Hindi (C1)
</span>
</div>
""", unsafe_allow_html=True)

# ── The Research ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">The Research</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text">
As wind and solar grow, they depress electricity prices exactly when they generate most — the
<span class="accent">cannibalization effect</span>. This erosion creates a widening price
spread that flexible industrial assets, batteries and demand response, can capture. This
portfolio turns seven years of ENTSO-E market data across Germany, the Netherlands and Denmark
into interactive tools that measure exactly how much that flexibility is worth — independent
research built ahead of my Master's thesis, starting August 2026.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:1rem;">
    <span class="tag">ENTSO-E data</span>
    <span class="tag">2018–2024</span>
    <span class="tag">DE · NL · DK</span>
    <span class="tag">Python</span>
    <span class="tag">Pandas</span>
    <span class="tag">Plotly</span>
    <span class="tag">Streamlit</span>
    <span class="tag">Hourly day-ahead prices</span>
</div>
""", unsafe_allow_html=True)

# ── Navigation cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Explore the Analysis</div>', unsafe_allow_html=True)

cards = [
    ("📉", "Cannibalization Explorer",
     "How renewable penetration erodes the capture price of wind and solar, year by year, across three markets.",
     "pages/1_Cannibalization_Explorer.py"),
    ("🌡️", "Negative Price Heatmap",
     "When prices fall below zero — mapped across hour-of-day and month, revealing the rhythm of over-supply.",
     "pages/2_Negative_Price_Heatmap.py"),
    ("🔋", "Flexibility Simulator",
     "Turn price volatility into euros: simulate battery storage and demand-response revenue under two strategies.",
     "pages/3_Flexibility_Simulator.py"),
    ("📊", "Price Duration Curves",
     "Hourly prices sorted from highest to lowest, showing how much of the year sits in the extreme tails a flexible asset can arbitrage.",
     "pages/7_Price_Duration_Curves.py"),
]

cols = st.columns(4)
for col, (icon, title, desc, page_path) in zip(cols, cards):
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="icon">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            st.page_link(page_path, label=f"Open {title}", icon="→")
        except Exception:
            # Falls back silently if the path doesn't match a real page yet —
            # fix the path above once you confirm the filename.
            pass

st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.72rem; color:#4a4a48; font-family: IBM Plex Mono, monospace;
            text-align:center; padding-top:1.5rem; border-top:1px solid #232324; margin-top:2rem;'>
Built with Streamlit · Data from ENTSO-E Transparency Platform · © 2026 Riddhi Borkute
</div>
""", unsafe_allow_html=True)
