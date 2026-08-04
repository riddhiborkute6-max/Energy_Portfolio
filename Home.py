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

# ── Theme: charcoal + deep teal (structure) + amber (value) ───────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0c0c0d; color: #e9e7e2; }

/* Full-width main container so every section lines up at the same edges */
.block-container { max-width: 100% !important; padding-left: 3rem; padding-right: 3rem; }

h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #f2f0eb !important; font-weight: 600 !important; }

/* Hero */
.hero { padding: 2.5rem 0 0.5rem 0; margin-bottom: 0.5rem; }
.hero .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #2dd4bf; margin-bottom: 0.6rem;
}
.hero h1 { font-size: 2.6rem !important; line-height: 1.15; margin: 0 0 0.9rem 0; }

/* Section labels + matching sub-headings (same pattern as the hero) */
.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: #2dd4bf;
    margin: 2.6rem 0 0.6rem 0;
}
.section-heading {
    font-family: 'Fraunces', serif !important; color: #f2f0eb !important;
    font-weight: 600 !important; font-size: 1.9rem !important;
    margin: 0 0 1rem 0 !important;
}

/* Body copy — full width, justified */
.body-text {
    color: #b7b4ac; font-size: 1.02rem; line-height: 1.8;
    width: 100%; text-align: justify; text-justify: inter-word;
}
.body-text strong { color: #f2f0eb; }
.body-text .accent { color: #f0a860; font-weight: 600; }

/* Tags */
.tag {
    display: inline-block; background: #17171a; border: 1px solid #2a2a2c;
    border-radius: 20px; padding: 3px 12px; margin: 3px 6px 3px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #a7a49d;
}

/* Cards — the whole box is clickable */
[data-testid="stPageLink"] {
    display: flex !important; flex-direction: column; align-items: flex-start;
    justify-content: flex-start;
    background: #131314; border: 1px solid #232324; border-radius: 10px;
    padding: 1.4rem 1.5rem !important; min-height: 168px;
    transition: border-color 0.2s ease, transform 0.2s ease;
    text-decoration: none !important;
}
[data-testid="stPageLink"]:hover { border-color: #f0a860; transform: translateY(-2px); }
[data-testid="stPageLink"] p {
    font-family: 'Inter', sans-serif !important; color: #2dd4bf !important;
    font-size: 0.9rem !important; line-height: 1.6 !important;
    text-align: left !important; white-space: pre-line !important;
}
[data-testid="stPageLink"] p strong {
    font-family: 'Fraunces', serif !important; color: #8f8c86 !important;
    font-size: 1.15rem !important; font-weight: 600 !important;
    display: block; margin-bottom: 0.5rem;
}

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
    🔗 <a href='https://linkedin.com/in/riddhi-borkute' style='color:#2dd4bf;' target='_blank'>LinkedIn</a><br>
    💻 <a href='https://github.com/riddhiborkute6-max' style='color:#2dd4bf;' target='_blank'>GitHub</a><br>
    ✉️ <a href='mailto:riddhiborkute6@gmail.com' style='color:#2dd4bf;'>Email</a>
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
I'm an MSc Global Production Engineering student at TU Berlin, moving from a
mechanical engineering background into quantitative energy-market analysis. I currently work
as a <span class="accent">Working Student in Energy Market and Asset Analysis at neustrom GmbH</span>
in Berlin, where I size and configure battery storage systems for industrial and commercial
clients, build dispatch strategies for storage co-located with solar and wind, and develop
Python-based market models on day-ahead price and generation data, translating that analysis
into client-facing decision tools.
<br><br>
Before moving into energy, I spent two years as an engineer at John Deere in Pune, India,
running Value Engineering workshops and building Power BI / Tableau reporting that standardised
cost and performance tracking across plants in India, Europe and the US.
<br>
</span>
</div>
""", unsafe_allow_html=True)

# ── The Research ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">The Research</div>', unsafe_allow_html=True)
st.markdown('<h2 class="section-heading">Quantifying the Cannibalization Effect</h2>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text">
As wind and solar grow, they depress electricity prices exactly when they generate most —> the
<span class="accent">cannibalization effect</span>. This erosion creates a widening price
spread that flexible industrial assets, batteries and demand response, can capture. This
portfolio turns seven years (2018 to 2024) of ENTSO-E market data across Germany, the Netherlands and Denmark
into interactive tools that measure exactly how much that flexibility is worth.
</div>
""", unsafe_allow_html=True)

# ── Navigation cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Explore the Analysis</div>', unsafe_allow_html=True)
st.markdown('<h2 class="section-heading">Completed Analysis Tools</h2>', unsafe_allow_html=True)

# Real filenames confirmed from the repo. If any of these change, update the
# path string (not the label) so the link keeps working.
cards = [
    ("Cannibalization Explorer",
     "How renewable penetration erodes the capture price of wind and solar, year by year, across three markets.",
     "pages/1_Cannibalization_Explorer.py"),
    ("Negative Price Heatmap",
     "When prices fall below zero — mapped across hour-of-day and month, revealing the rhythm of over-supply.",
     "pages/2_Negative_Price_Heatmap.py"),
    ("Flexibility Simulator",
     "Turn price volatility into euros: simulate battery storage and demand-response revenue under two strategies.",
     "pages/3_Flexibility_Simulator.py"),
    ("Price Duration Curves",
     "Hourly prices sorted from highest to lowest, showing how much of the year sits in the extreme tails a flexible asset can arbitrage.",
     "pages/7_Price_Duration_Curves.py"),
]

cols = st.columns(4)
for col, (title, desc, page_path) in zip(cols, cards):
    with col:
        try:
            st.page_link(
                page_path,
                label=f"**{title}**  \n{desc}",
                use_container_width=True,
            )
        except Exception:
            st.markdown(f"""
            <div style="border:1px solid #232324; border-radius:10px; padding:1.4rem 1.5rem; min-height:168px;">
                <div style="font-family:'Fraunces',serif; color:#f2f0eb; font-size:1.05rem;">{title}</div>
                <div style="color:#8f8c86; font-size:0.85rem; margin-top:0.5rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.72rem; color:#4a4a48; font-family: IBM Plex Mono, monospace;
            text-align:center; padding-top:1.5rem; border-top:1px solid #232324; margin-top:2rem;'>
Built with Streamlit · Data from ENTSO-E Transparency Platform · © 2026 Riddhi Borkute
</div>
""", unsafe_allow_html=True)
