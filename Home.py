import streamlit as st

st.set_page_config(
    page_title="Riddhi Borkute | Energy Analyst",
    page_icon="⚡",
    layout="wide"
)

# Hero section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("# ⚡ Riddhi Borkute")
    st.markdown("### Energy Market Analyst | European Power Markets")
    st.markdown("""
    > *Analysing how renewable penetration reshapes industrial electricity 
    economics in European power markets — Germany, Netherlands, Denmark.*
    """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.link_button("🔗 LinkedIn", "https://www.linkedin.com/in/riddhi-borkute")
    with col_b:
        st.link_button("📄 Download CV", "xyz")

with col2:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; border-left: 4px solid #1D9E75;'>
    <h4 style='color: #1D9E75;'>📍 Based in Berlin</h4>
    <p>MSc Energy Economics</p>
    <p>Thesis: Renewable Cannibalization in European Power Markets</p>
    <p>Target: Aurora · Statkraft · Sympower</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Stats row
st.markdown("### 📊 What's being built here")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; border-top: 3px solid #1D9E75; text-align: center;'>
    <h2 style='color: #1D9E75;'>3</h2>
    <p>Markets analysed<br>DE · NL · DK</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; border-top: 3px solid #1D9E75; text-align: center;'>
    <h2 style='color: #1D9E75;'>7</h2>
    <p>Years of data<br>2018 – 2024</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; border-top: 3px solid #1D9E75; text-align: center;'>
    <h2 style='color: #1D9E75;'>5</h2>
    <p>Tools & dashboards<br>in progress</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Pages overview
st.markdown("### 🗂️ Explore")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; margin-bottom: 12px;'>
    <h4>📊 Cannibalization Explorer</h4>
    <p style='color: #aaa;'>How wind & solar erode their own market value as penetration grows. Interactive scatter by country and year.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; margin-bottom: 12px;'>
    <h4>⚙️ Flexibility Simulator</h4>
    <p style='color: #aaa;'>Calculate your factory's arbitrage potential, peak shaving savings, and avoided grid charges.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px;'>
    <h4>🔬 Thesis Lab</h4>
    <p style='color: #aaa;'>Research question, methodology, dataset, and early findings. Updated as the thesis progresses.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; margin-bottom: 12px;'>
    <h4>🗓️ Negative Price Heatmap</h4>
    <p style='color: #aaa;'>Calendar heatmap of negative price hours per country per year. When Germany pays you to consume.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; margin-bottom: 12px;'>
    <h4>📝 Research Notes</h4>
    <p style='color: #aaa;'>Weekly deep dives on European energy market mechanics — negative prices, cannibalization, flexibility.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #1E2130; padding: 20px; border-radius: 10px;'>
    <h4>👤 About</h4>
    <p style='color: #aaa;'>Nagpur → John Deere → Berlin → European energy markets. The full story.</p>
    </div>
    """, unsafe_allow_html=True)
