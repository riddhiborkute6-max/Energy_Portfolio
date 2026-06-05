"""
pages/5_Research_Notes.py
--------------------------
Research Notes — Riddhi Borkute's Energy Portfolio

A personal running feed of short observations about the energy industry:
snippets, things noticed in the news, quick thoughts. Tagged and filterable.

HOW NOTES WORK (important):
  - The permanent feed lives in the `NOTES` list below (in Git -> never lost).
  - The "Compose" box lets you write a new note live and preview it, then
    generates a paste-ready code block to add to the NOTES list and push.
  - This avoids Streamlit Cloud's ephemeral filesystem wiping live-typed notes.

To add a note permanently: write it in the Compose box, copy the generated
snippet, paste it at the TOP of the NOTES list, commit & push.
"""

import streamlit as st
from datetime import date

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="Research Notes | Energy Portfolio",
    page_icon="📓",
    layout="wide",
)

# -- Styling -------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #58a6ff; }

.note {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    border-left: 3px solid #3fb950;
    padding: 1.1rem 1.4rem; margin-bottom: 1rem;
}
.note .date {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
    color: #6e7681; letter-spacing: 0.05em;
}
.note .title {
    font-family: 'IBM Plex Mono', monospace; color: #e6edf3;
    font-size: 1.02rem; font-weight: 600; margin: 0.25rem 0 0.5rem 0;
}
.note .body { color: #adbac7; line-height: 1.65; font-size: 0.92rem; }
.note .tags { margin-top: 0.7rem; }

.tag {
    display: inline-block; background: #1c2333; border: 1px solid #30363d;
    border-radius: 20px; padding: 2px 11px; margin: 2px 4px 2px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #79c0ff;
}
.tag.policy   { color: #ffa657; border-color: #5a3a1a; }
.tag.markets  { color: #56d364; border-color: #1a4a2a; }
.tag.tech     { color: #79c0ff; border-color: #1a3a5a; }
.tag.flex     { color: #d2a8ff; border-color: #3a2a5a; }

.preview-box {
    background: #0d1117; border: 1px dashed #30363d; border-radius: 8px;
    padding: 1rem 1.2rem; margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# THE NOTES FEED  -- edit this list to add permanent notes (newest at the top)
# Each note: date (YYYY-MM-DD), title, body, tags (list).
# Known tag styles: "markets", "policy", "tech", "flex". Others render plain.
# =============================================================================
NOTES = [
    {
        "date": "2025-01-15",
        "title": "Negative prices are becoming structural, not exceptional",
        "body": "[EDIT - example note] Spent today looking at 2024 DE data: negative-price "
                "hours are clustering in spring midday windows when solar floods the market. "
                "What struck me is how predictable the pattern has become - it's no longer a "
                "rare event but a recurring daily feature. That predictability is exactly what "
                "makes it bankable for flexible assets.",
        "tags": ["markets", "flex"],
    },
    {
        "date": "2025-01-10",
        "title": "Why cross-border coupling matters for my thesis",
        "body": "[EDIT - example note] Reading on interconnection: DK1 and DE prices move "
                "together far more than I expected. Cannibalization in one market leaks into "
                "its neighbours through the cables. Makes me think the single-market view "
                "understates the effect - worth a paragraph in the methodology.",
        "tags": ["markets", "tech"],
    },
    {
        "date": "2025-01-05",
        "title": "Battery revenue stacking",
        "body": "[EDIT - example note] Note to self: real batteries don't just do energy "
                "arbitrage - they stack frequency response, capacity market, and arbitrage "
                "revenues. My simulator only models arbitrage, so it's a lower bound on total "
                "value. Worth stating explicitly.",
        "tags": ["flex", "markets"],
    },
]

# -- Header --------------------------------------------------------------------
st.title("📓 Research Notes")
st.markdown("""
<div style='color:#8b949e; font-size:0.92rem; line-height:1.65; max-width:760px;'>
Short, running observations on the energy industry - things I notice in the data, the news,
and the markets. Quick thoughts, not polished essays. Filter by tag to browse.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- Tag filter ----------------------------------------------------------------
all_tags = sorted({t for note in NOTES for t in note["tags"]})

col_filter, col_count = st.columns([3, 1])
with col_filter:
    selected_tags = st.multiselect(
        "Filter by tag", options=all_tags, default=[],
        help="Show only notes with these tags. Leave empty to show all.",
        placeholder="All notes",
    )

if selected_tags:
    shown = [n for n in NOTES if any(t in selected_tags for t in n["tags"])]
else:
    shown = NOTES

with col_count:
    st.markdown(f"""
    <div style='text-align:right; padding-top:1.9rem; color:#6e7681;
                font-family: IBM Plex Mono, monospace; font-size:0.85rem;'>
    {len(shown)} / {len(NOTES)} notes
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -- Render the feed (already newest-first by list order) ----------------------
def render_tags(tags):
    html = ""
    for t in tags:
        cls = t if t in ("policy", "markets", "tech", "flex") else ""
        html += f"<span class='tag {cls}'>{t}</span>"
    return html

if not shown:
    st.info("No notes match that filter.")
else:
    for n in shown:
        st.markdown(f"""
        <div class="note">
            <div class="date">{n['date']}</div>
            <div class="title">{n['title']}</div>
            <div class="body">{n['body']}</div>
            <div class="tags">{render_tags(n['tags'])}</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# COMPOSE BOX -- write a new note, preview it, get paste-ready code
# =============================================================================
st.markdown("---")
with st.expander("✍️ Compose a new note"):
    st.markdown("""
    <div style='color:#8b949e; font-size:0.83rem; line-height:1.6; margin-bottom:0.8rem;'>
    Write your note below and preview it live. When you're happy, copy the generated
    snippet at the bottom and paste it at the <strong>top</strong> of the <code>NOTES</code>
    list in this file, then commit &amp; push. (Live-typed notes aren't saved on the server -
    Streamlit Cloud wipes its filesystem on restart - so Git is the permanent home.)
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        new_title = st.text_input("Title", placeholder="A short headline for the note")
        new_body  = st.text_area("Note", placeholder="Your observation...", height=140)
    with c2:
        new_date = st.date_input("Date", value=date.today())
        picked_tags = st.multiselect(
            "Tags",
            options=["markets", "policy", "tech", "flex"],
            help="Pick existing tags. Add new ones in the box below.",
        )
        custom_tags_raw = st.text_input(
            "New tags (comma-separated)",
            placeholder="e.g. hydrogen, grid",
            help="Type any new tags here, separated by commas",
        )
        custom_tags = [t.strip() for t in custom_tags_raw.split(",") if t.strip()]
        # combine, preserving order and removing duplicates
        new_tags = list(dict.fromkeys(picked_tags + custom_tags))

    if new_title or new_body:
        st.markdown("**Live preview:**")
        st.markdown(f"""
        <div class="preview-box">
            <div class="note" style="margin-bottom:0;">
                <div class="date">{new_date.isoformat()}</div>
                <div class="title">{new_title or '(untitled)'}</div>
                <div class="body">{new_body or '...'}</div>
                <div class="tags">{render_tags(new_tags)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tags_repr = ", ".join(f'"{t}"' for t in new_tags)
        safe_title = (new_title or "").replace('"', '\\"')
        safe_body  = (new_body or "").replace('"', '\\"')
        snippet = (
            "    {\n"
            f'        "date": "{new_date.isoformat()}",\n'
            f'        "title": "{safe_title}",\n'
            f'        "body": "{safe_body}",\n'
            f'        "tags": [{tags_repr}],\n'
            "    },"
        )
        st.markdown("**Paste this at the top of the `NOTES` list:**")
        st.code(snippet, language="python")

# -- Footer --------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='font-size:0.72rem; color:#484f58; font-family: IBM Plex Mono, monospace; text-align:center;'>
Running field notes on the energy transition · Riddhi Borkute
</div>
""", unsafe_allow_html=True)