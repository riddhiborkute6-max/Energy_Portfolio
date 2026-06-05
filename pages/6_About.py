"""
pages/6_About.py
-----------------
About — Riddhi Borkute's Energy Portfolio

The pitch page. Narrative bio up top (mechanical engineering -> energy
economics), structured details below (background, skills, what I'm targeting),
and a prominent contact / "what I'm looking for" call to action.

Everything marked [EDIT] is yours to fill in. The skills and targeting
content is pre-filled from your real profile - adjust as you like.
"""

import streamlit as st

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="About | Riddhi Borkute",
    page_icon="👤",
    layout="wide",
)

# -- Styling -------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }

.bio {
    font-size: 1.02rem; color: #adbac7; line-height: 1.75; max-width: 760px;
}
.bio strong { color: #e6edf3; }

.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: #6e7681;
    margin: 2.2rem 0 1rem 0;
}

.block {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 1.3rem 1.5rem; margin-bottom: 1rem; height: 100%;
}
.block h4 {
    font-family: 'IBM Plex Mono', monospace; color: #58a6ff;
    margin: 0 0 0.7rem 0; font-size: 0.95rem;
}
.block ul { margin: 0; padding-left: 1.1rem; }
.block li { color: #adbac7; font-size: 0.88rem; line-height: 1.7; margin-bottom: 0.3rem; }

.skill-tag {
    display: inline-block; background: #1c2333; border: 1px solid #30363d;
    border-radius: 6px; padding: 4px 12px; margin: 3px 5px 3px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #79c0ff;
}

.cta {
    background: linear-gradient(135deg, #16291f 0%, #14331f 100%);
    border: 1px solid #2a5a3a; border-radius: 12px;
    padding: 1.8rem 2rem; margin: 1.5rem 0;
}
.cta h3 { color: #56d364 !important; margin-top: 0; }
.cta p { color: #c8e6d0; line-height: 1.7; font-size: 0.96rem; }

.contact-links a {
    display: inline-block; margin-right: 0.8rem; margin-top: 0.6rem;
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 0.6rem 1.2rem; color: #58a6ff !important; text-decoration: none;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.88rem;
    transition: border-color 0.2s ease;
}
.contact-links a:hover { border-color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

# -- Sidebar -------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👤 About")
    st.markdown("""
    <div style='font-size:0.82rem; color:#8b949e; line-height:1.6;'>
    <strong style='color:#e6edf3;'>Riddhi Borkute</strong><br>
    MSc Energy Economics · Berlin
    </div>
    """, unsafe_allow_html=True)

# -- Header + narrative bio ----------------------------------------------------
st.title("👤 About")

st.markdown("""
<div class="bio">
I'm <strong>Riddhi Borkute</strong>, an MSc Energy Economics student in Berlin with a
background in <strong>mechanical engineering</strong>. I moved from building and
understanding physical systems to analysing the markets that will decide how the energy
transition actually plays out.
<br><br>
That shift is what drives my work. Engineering taught me how energy systems behave;
economics is teaching me <strong>what they're worth</strong> and how markets price
flexibility, risk, and renewable variability. My master's thesis sits right at that
intersection - quantifying the value of industrial flexibility as renewables reshape
European power prices.
<br><br>
<span style="color:#6e7681;">[EDIT: Add a personal sentence or two - why energy, what
got you into it, what you care about. This is where your voice comes through.]</span>
</div>
""", unsafe_allow_html=True)

# -- Structured details (3 columns) --------------------------------------------
st.markdown('<div class="section-label">At a glance</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="block">
        <h4>🎓 Background</h4>
        <ul>
            <li>MSc Energy Economics — Berlin</li>
            <li>BEng Mechanical Engineering</li>
            <li>Working student, energy sector</li>
            <li>[EDIT: add any other highlight]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="block">
        <h4>🔬 Thesis Focus</h4>
        <ul>
            <li>Industrial flexibility value</li>
            <li>Renewable cannibalization effect</li>
            <li>Battery storage & demand response</li>
            <li>Markets: DE, NL, DK</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="block">
        <h4>🎯 Targeting</h4>
        <ul>
            <li>Energy market analyst roles</li>
            <li>Flexibility & storage focus</li>
            <li>Quantitative / data-driven</li>
            <li>[EDIT: availability / start date]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -- Skills --------------------------------------------------------------------
st.markdown('<div class="section-label">Tools & skills</div>', unsafe_allow_html=True)

skills = ["Python", "Pandas", "Plotly", "Streamlit", "Time-series analysis",
          "ENTSO-E data", "Electricity markets", "Energy modelling",
          "Jupyter", "Git", "Data visualisation", "[EDIT: add more]"]
skills_html = "".join(f"<span class='skill-tag'>{s}</span>" for s in skills)
st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)

# -- CTA: what I'm looking for -------------------------------------------------
st.markdown('<div class="section-label">Get in touch</div>', unsafe_allow_html=True)

st.markdown("""
<div class="cta">
    <h3>What I'm looking for</h3>
    <p>
    I'm seeking <strong style="color:#e6edf3;">analyst roles in energy markets</strong> -
    especially work on flexibility, storage, and renewable integration - where I can apply
    market modelling, Python, and data analysis to real transition problems. This portfolio is
    my thesis work made interactive: real data, real methods, tools you can click through.
    <br><br>
    If your team works on these questions, I'd genuinely like to talk - whether that's a role,
    a working-student position, or just a conversation about the work.
    <br><br>
    <span style="color:#8aab95; font-size:0.88rem;">[EDIT: add a line on your current
    availability, notice period, or ideal start date.]</span>
    </p>
</div>
""", unsafe_allow_html=True)

# contact links (st.link_button works on modern Streamlit; HTML fallback below)
st.markdown("""
<div class="contact-links">
    <a href="[EDIT: LinkedIn URL]" target="_blank">🔗 LinkedIn</a>
    <a href="[EDIT: GitHub URL]" target="_blank">💻 GitHub</a>
    <a href="mailto:[EDIT: email]">✉️ Email</a>
    <a href="[EDIT: CV/resume link]" target="_blank">📄 CV</a>
</div>
""", unsafe_allow_html=True)

# -- Footer --------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Thanks for visiting · Riddhi Borkute · Energy Portfolio
</div>
""", unsafe_allow_html=True)