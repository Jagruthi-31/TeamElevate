import html

import streamlit as st

from src.accessibility import read_aloud
from src.app_helpers import (
    current_profile, get_recommender, page_setup, retrain_after_feedback, sections_done,
)
from src.config import FORMATS
from src.content import SECTIONS, text_for, visual_html
from src.recommendation import add_feedback
from src.theme import format_color_vars, glyph, md, page_header

page_setup("Learning Module")
page_header("Lesson: understanding fractions",
            "Pick how you want to learn it. The format the model suggests is marked, "
            "but every format is yours to choose.", step=3)

profile = current_profile()
rec = get_recommender().recommend(profile)
recommended = rec["top_format"]

OPTIONS = FORMATS + ["Standard text (original wording)"]
choice = st.radio(
    "How would you like to learn this lesson?",
    OPTIONS,
    index=OPTIONS.index(recommended),
    horizontal=True,
    help="The option marked as recommended comes from the AI. You can pick any option.",
    format_func=lambda f: f"{f} (recommended)" if f == recommended else f,
)
fmt = "Text explanation" if choice.startswith("Standard") else choice
standard = choice.startswith("Standard")
rate = {1: 0.8, 2: 1.0, 3: 1.15}[int(profile["pace"])]
md(format_color_vars(fmt))
st.session_state.formats_viewed.add(fmt)

done = sections_done()
st.progress(done / len(SECTIONS), text=f"{done} of {len(SECTIONS)} sections understood")

if rec["support_level"] == "high":
    md(f'<div class="la la-support">{glyph("steps", 22)}<span><b>Take your time.</b> There are no timers. '
       'Each idea is in its own short section.</span></div>')

for i, s in enumerate(SECTIONS, start=1):
    with st.container(border=True):
        md(f'<div class="la la-section-head"><span class="num">{i}</span>'
           f'<h3>{html.escape(s["title"])}</h3></div>')

        if fmt == "Text explanation":
            body = text_for(s, profile["complexity_pref"], force_standard=standard)
            st.write(body)
            read_aloud(body, key=f"t{s['id']}", rate=rate)

        elif fmt == "Audio explanation":
            read_aloud(s["audio"], label="Play audio explanation", key=f"a{s['id']}", rate=rate)
            with st.expander("Show captions / transcript", expanded=True):
                st.write(s["audio"])

        elif fmt == "Visual diagrams":
            st.markdown(visual_html(s), unsafe_allow_html=True)
            st.write(f"**Picture description:** {s['caption']}")
            read_aloud(s["caption"], key=f"v{s['id']}", rate=rate)

        else:  # Step-by-step
            for n, step in enumerate(s["steps"], start=1):
                st.markdown(f"**Step {n}.** {step}")
            read_aloud(" ".join(f"Step {n}. {t}" for n, t in enumerate(s["steps"], 1)),
                       key=f"p{s['id']}", rate=rate)

        st.checkbox("I understand this section", key=f"und_{s['id']}")

if done == len(SECTIONS):
    st.success("Lesson complete. Take the quiz to check what you learned.")

st.markdown("## Did this format help you?")
key = (choice, round(profile["quiz_score"]))
if key in st.session_state.feedback_given:
    st.success("Thanks. Your feedback was added and the recommendation model was updated.")
else:
    with st.container(border=True):
        rating = st.slider("Rating (1 = not helpful, 5 = very helpful)", 1, 5, 3)
        if st.button("Send feedback", type="primary"):
            add_feedback(profile, fmt, rating)
            retrain_after_feedback()
            st.session_state.feedback_given.add(key)
            st.toast("Thanks! +10 XP. The model has been updated.", icon=":material/check_circle:")
            st.rerun()

st.page_link("pages/4_Quiz.py", label="Next: take the adaptive quiz", icon=":material/arrow_forward:")
