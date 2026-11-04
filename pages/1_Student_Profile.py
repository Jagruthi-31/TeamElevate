import streamlit as st

from src.app_helpers import page_setup
from src.config import COMPLEXITY_LABELS, SPEED_LABELS
from src.theme import glyph, md, page_header

page_setup("Student Profile")
page_header("Your learning profile",
            "Tell us how you like to learn. You choose everything here, and you can change "
            "your answers at any time.", step=1)

p = st.session_state.profile


def way(fmt: str, label: str) -> None:
    """Heading for one preference slider, with the format's icon and colour."""
    k = {"Text explanation": "text", "Audio explanation": "audio", "Visual diagrams": "visual"}[fmt]
    md(f'<div class="la" style="display:flex;gap:.5rem;align-items:center;font-weight:700;'
       f'color:var(--f-{k});margin-bottom:.2rem">{glyph(fmt, 22)}<span style="color:var(--ink)">{label}</span></div>')


with st.form("profile_form"):
    name = st.text_input("Your name or nickname (optional)", value=p["name"], max_chars=30)

    st.markdown("### How much do you like each way of learning?")
    st.caption("1 = not much, 5 = a lot")
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        way("Text explanation", "Reading text")
        pref_text = st.slider("Reading text", 1, 5, int(p["pref_text"]), label_visibility="collapsed")
    with c2:
        way("Audio explanation", "Listening to audio")
        pref_audio = st.slider("Listening to audio", 1, 5, int(p["pref_audio"]), label_visibility="collapsed")
    with c3:
        way("Visual diagrams", "Pictures and diagrams")
        pref_visual = st.slider("Pictures and diagrams", 1, 5, int(p["pref_visual"]), label_visibility="collapsed")

    st.markdown("### How do you like to work?")
    c4, c5, c6 = st.columns(3, gap="large")
    reading_speed = c4.select_slider("Reading speed", [1, 2, 3], int(p["reading_speed"]),
                                     format_func=SPEED_LABELS.get)
    pace = c5.select_slider("Learning pace", [1, 2, 3], int(p["pace"]),
                            format_func=lambda v: {1: "Slower", 2: "Normal", 3: "Faster"}[v])
    complexity = c6.select_slider("Explanation detail", [1, 2, 3], int(p["complexity_pref"]),
                                  format_func=COMPLEXITY_LABELS.get)

    st.caption("Quiz score, attempts and time are measured automatically from your quizzes. "
               "Until you take a quiz, neutral starting values are used.")
    saved = st.form_submit_button("Save profile", type="primary")

if saved:
    p.update(name=name.strip(), pref_text=pref_text, pref_audio=pref_audio,
             pref_visual=pref_visual, reading_speed=reading_speed, pace=pace,
             complexity_pref=complexity)
    st.session_state.profile_saved = True
    st.success("Profile saved.")
    st.page_link("pages/2_AI_Recommendations.py", label="Next: see your AI recommendation",
                 icon=":material/arrow_forward:")

st.info("Text size, contrast, an easy-to-read font and read-aloud are in the sidebar on every page.")
