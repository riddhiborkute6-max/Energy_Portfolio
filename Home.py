import streamlit as st

st.set_page_config(page_title="Riddhi Borkute | Energy Analyst", page_icon="⚡")

st.title("Riddhi Borkute")
st.subheader("Energy Market Analyst | European Power Markets")

st.markdown("""
Analysing how renewable penetration reshapes industrial electricity economics 
in European power markets.
""")

st.divider()

st.markdown("### What you'll find here")
st.markdown("""
- 📊 **Renewable Cannibalization Explorer** — how wind & solar erode their own market value
- 🗓️ **Negative Price Heatmap** — when Germany pays you to consume electricity
- ⚙️ **Industrial Flexibility Simulator** — calculate your factory's arbitrage potential
- 📝 **Research Notes** — deep dives on European energy market mechanics
- 🔬 **Thesis Lab** — my MSc research in progress
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.link_button("LinkedIn", "https://www.linkedin.com/in/riddhi-borkute")
with col2:
    st.link_button("Download CV", "xyz")