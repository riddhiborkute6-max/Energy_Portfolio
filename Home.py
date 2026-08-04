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

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }

/* Hero */
.hero {
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 2rem;
}
.hero .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #3fb950; margin-bottom: 0.6rem;
}
.hero h1 {
    font-size: 2.4rem !important; line-height: 1.15; margin: 0 0 0.8rem 0;
    color: #e6edf3 !important;
}
.hero h1 .accent { color: #58a6ff; }
.hero .lede {
    font-size: 1.05rem; color: #8b949e; max-width: 760px; line-height: 1.65;
}

/* Pitch band */
.pitch {
    background: linear-gradient(135deg, #161b22 0%, #1a2230 100%);
    border: 1px solid #30363d; border-radius: 10px;
    padding: 1.6rem 1.8rem; margin: 1.5rem 0;
}
.pitch h3 { margin-top: 0; }
.pitch p { color: #adbac7; line-height: 1.65; font-size: 0.95rem; }

/* Nav cards */
.card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 1.3rem 1.4rem; height: 100%;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.card:hover { border-color: #58a6ff; transform: translateY(-2px); }
.card .icon { font-size: 1.6rem; }
.card .title {
    font-family: 'IBM Plex Mono', monospace; color: #58a6ff;
    font-size: 1.05rem; font-weight: 600; margin: 0.5rem 0 0.4rem 0;
}
.card .desc { color: #8b949e; font-size: 0.85rem; line-height: 1.55; }

.tag {
    display: inline-block; background: #1c2333; border: 1px solid #30363d;
    border-radius: 20px; padding: 3px 12px; margin: 3px 4px 3px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #79c0ff;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: #6e7681;
    margin: 2rem 0 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Energy Portfolio")
    st.markdown("""
    <div style='font-size:0.82rem; color:#8b949e; line-height:1.6;'>
    <strong style='color:#e6edf3;'>Riddhi Borkute</strong><br>
    MSc Global Production Engineering · TU Berlin<br><br>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#6e7681; line-height:1.7;'>
    📍 Berlin, Germany<br>
    🔗 <a href='https://linkedin.com/in/riddhi-borkute' style='color:#58a6ff;' target='_blank'>LinkedIn</a><br>
    💻 <a href='https://github.com/riddhiborkute6-max' style='color:#58a6ff;' target='_blank'>GitHub</a><br>
    ✉️ <a href='mailto:riddhiborkute6@gmail.com' style='color:#58a6ff;'>Email</a>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="eyebrow">Independent Research · Ahead of My Master's Thesis (Aug 2026)</div>
    <h1>About</h1>
    <p class="lede">
    As wind and solar grow, they depress electricity prices exactly when they generate most which is called
    the <strong style="color:#e6edf3;">cannibalization effect</strong>. This erosion creates a
    widening price spread that flexible industrial assets like batteries and demand response can
    capture. This portfolio turns seven years (2018 to 2024) of ENTSO-E market data across Germany, the
    Netherlands and Denmark into interactive tools that measure exactly how much that
    flexibility is worth.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Tech / scope tags ─────────────────────────────────────────────────────────
st.markdown("""
<div>
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

# ── Background / who I am (formerly the separate "About" page) ───────────────
st.markdown("""
<div class="pitch">
    <h3>Who I am</h3>
    <p>
    I'm an MSc Global Production Engineering student at TU Berlin, moving from a
    mechanical engineering background into quantitative energy-market analysis. I currently
    work as a <strong style="color:#e6edf3;">Working Student in Energy Market and Asset Optimization
    at neustrom GmbH</strong> in Berlin, where I size and configure battery storage
    systems for industrial and commercial clients, build dispatch strategies for storage
    co-located with solar and wind, and develop Python-based market models on day-ahead price
    and generation data, translating that analysis into client-facing decision tools.
    <br><br>
    Before moving into energy, I spent two years as an engineer at John Deere in Pune, India,
    running Value Engineering workshops and building Power BI / Tableau reporting that
    standardised cost and performance tracking across plants in India, Europe and the US.
    <br><br>
    This portfolio is independent research I'm building ahead of my Master's thesis (starting
    August 2026), on the same underlying question: how much is industrial flexibility worth as
    renewable penetration rises. It's built on real ENTSO-E market data with real methods, and
    designed as tools you can interact with rather than a PDF you have to read.
    <br><br>
    <span style="color:#8b949e; font-size:0.9rem;">
    </span>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Navigation cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Explore the analysis</div>', unsafe_allow_html=True)

cards = [
    ("Cannibalization Explorer",
     "How renewable penetration erodes the capture price of wind and solar, year by year, across three markets."),
    ("Negative Price Heatmap",
     "When prices fall below zero — mapped across hour-of-day and month, revealing the rhythm of over-supply."),
    ("Flexibility Simulator",
     "Turn price volatility into euros: simulate battery storage and demand-response revenue under two strategies."),
    ("Price Duration Curves",
     "Hourly prices sorted from highest to lowest, showing how much of the year sits in the extreme tails a flexible asset can arbitrage."),
]

cols = st.columns(4)
for col, (icon, title, desc) in zip(cols, cards):
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="icon">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
st.caption("Use the sidebar to navigate between pages.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace;
            text-align:center; padding-top:1.5rem; border-top:1px solid #21262d; margin-top:2rem;'>
Built with Streamlit · Data from ENTSO-E Transparency Platform · © 2026 Riddhi Borkute
</div>
""", unsafe_allow_html=True)
