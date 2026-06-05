"""
Home.py
--------
Landing page — Riddhi Borkute's Energy Portfolio

Balanced framing: leads with the project (thesis-driven flexibility analysis),
then a career pitch underneath. Static content — placeholders marked [EDIT]
are yours to fill in. Navigation cards link to the interactive pages.

This is the repo entry point. If your main file is named app.py or
streamlit_app.py instead, rename this to match.
"""

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Riddhi Borkute | Energy Portfolio",
    page_icon="⚡",
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
    st.markdown("### ⚡ Energy Portfolio")
    st.markdown("""
    <div style='font-size:0.82rem; color:#8b949e; line-height:1.6;'>
    <strong style='color:#e6edf3;'>Riddhi Borkute</strong><br>
    MSc Energy Economics · Berlin<br><br>
    Quantifying the value of industrial flexibility under rising renewable penetration.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#6e7681; line-height:1.7;'>
    📍 Berlin, Germany<br>
    🔗 <a href='[EDIT: LinkedIn URL]' style='color:#58a6ff;'>LinkedIn</a><br>
    💻 <a href='[EDIT: GitHub URL]' style='color:#58a6ff;'>GitHub</a><br>
    ✉️ <a href='mailto:[EDIT: email]' style='color:#58a6ff;'>Email</a>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="eyebrow">Master's Thesis · Interactive Research Portfolio</div>
    <h1>Quantifying the value of <span class="accent">industrial flexibility</span><br>
    under rising renewable penetration</h1>
    <p class="lede">
    As wind and solar grow, they depress electricity prices exactly when they generate most —
    the <strong style="color:#e6edf3;">cannibalization effect</strong>. This erosion creates a
    widening price spread that flexible industrial assets — batteries, demand response — can
    capture. This portfolio turns seven years of ENTSO-E market data across Germany, the
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

# ── Navigation cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Explore the analysis</div>', unsafe_allow_html=True)

cards = [
    ("📉", "Cannibalization Explorer",
     "How renewable penetration erodes the capture price of wind and solar, year by year, across three markets."),
    ("🔴", "Negative Price Heatmap",
     "When prices fall below zero — mapped across hour-of-day and month, revealing the rhythm of over-supply."),
    ("🔋", "Flexibility Simulator",
     "Turn price volatility into euros: simulate battery storage and demand-response revenue under two strategies."),
    ("🧪", "Thesis Lab",
     "The research question, methodology, and core literature underpinning this work."),
    ("📓", "Research Notes",
     "Working notes on key papers, data sources, and analytical decisions."),
    ("👤", "About",
     "Background, what I'm working toward, and how to get in touch."),
]

# render in rows of 3
for row_start in range(0, len(cards), 3):
    cols = st.columns(3)
    for col, (icon, title, desc) in zip(cols, cards[row_start:row_start + 3]):
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

# ── Pitch band (career, underneath the project) ────────────────────────────────
st.markdown("""
<div class="pitch">
    <h3>What I'm working toward</h3>
    <p>
    I'm an MSc Energy Economics student in Berlin with a background in mechanical
    engineering, moving into quantitative energy-market analysis. I'm looking for
    <strong style="color:#e6edf3;">analyst roles</strong> where I can apply market modelling,
    Python, and data analysis to the energy transition — flexibility, storage, and renewable
    integration in particular.
    <br><br>
    This portfolio is my thesis work made tangible: real market data, real methods, and tools
    you can interact with rather than a PDF you have to read. If your team works on these
    problems, I'd love to talk.
    <br><br>
    <span style="color:#6e7681; font-size:0.85rem;">[EDIT: Add a sentence about your current
    Werkstudent role / availability / target start date here.]</span>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace;
            text-align:center; padding-top:1.5rem; border-top:1px solid #21262d; margin-top:2rem;'>
Built with Streamlit · Data from ENTSO-E Transparency Platform · © 2025 Riddhi Borkute
</div>
""", unsafe_allow_html=True)