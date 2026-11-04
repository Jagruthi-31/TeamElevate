import json

import streamlit as st

from src.app_helpers import get_recommender, page_setup
from src.config import EVAL_JSON
from src.theme import hero_pie, md, stat_strip

page_setup("Home")
get_recommender()  # warm up the model

# ---- hero: one lesson (a circle) cut into the four ways it can be taught ----
with st.container(key="hero"):
    left, right = st.columns([1.05, 1], gap="large", vertical_alignment="center")
    with left:
        md("""<div class="la la-hero"><h1>One lesson, taught the way you learn.</h1>
        <p class="lede">LearnAble AI turns each lesson into text, audio, diagrams or small steps, and sets
        the pace and quiz difficulty to match you. Teachers see the whole class at a glance.
        Learners choose what works. The system only suggests.</p></div>""")
        with st.container(key="cta"):
            st.page_link("pages/1_Student_Profile.py", label="Build your learning profile",
                         icon=":material/arrow_forward:")
        md("""<p class="la la-promise">It suggests learning adaptations. It never diagnoses or labels a student.</p>""")
    with right:
        md(f'<div class="la">{hero_pie()}</div>')

# ---- evidence strip: real numbers from models/evaluation_results.json ----
try:
    ev = json.loads(EVAL_JSON.read_text())
    stat_strip([
        (f"{ev['test_accuracy'] * 100:.0f}%", "format accuracy on held-out data, against 25% by chance"),
        (f"{ev['test_top2_accuracy'] * 100:.0f}%", "of the time the right format is in the top two suggestions"),
        (f"{ev['mean_response_ms']:.0f} ms", "to compute a recommendation"),
        ("1,500", "simulated learner interactions behind the model"),
    ])
except Exception:
    pass

if st.session_state.profile_saved:
    st.success("Your profile is saved. Next, see your AI recommendation.")

# ---- the path: a real sequence, so numbered ----
st.markdown("## Your path through LearnAble")
STEPS = [
    ("Profile", "Tell us how you like to learn: text, audio or pictures, and your pace.",
     "pages/1_Student_Profile.py", "Open profile"),
    ("Recommendation", "A model finds learners like you and suggests a format. Try the what-if tool.",
     "pages/2_AI_Recommendations.py", "See suggestion"),
    ("Lesson", "Read the same fractions lesson in any format you like.",
     "pages/3_Learning_Module.py", "Open lesson"),
    ("Quiz", "Questions get easier or harder as you answer. There is no timer.",
     "pages/4_Quiz.py", "Start quiz"),
    ("Progress", "Scores, badges, a study plan and a report you can download.",
     "pages/5_Progress.py", "View progress"),
]
with st.container(key="path"):
    for col, (i, (title, copy, page, label)) in zip(st.columns(5, gap="small"), enumerate(STEPS, 1)):
        with col, st.container(border=True):
            md(f'<div class="la"><span class="la-badge">{i}</span><div class="la-step-title">{title}</div>'
               f'<p class="la-step-copy">{copy}</p></div>')
            st.page_link(page, label=label)

# ---- who it is for ----
st.markdown("## Built for learners, teachers and reviewers")
a, b, c = st.columns(3, gap="large")
with a:
    st.markdown("#### Learners")
    st.write("Choose how you learn. Switch formats any time, track your progress, earn badges and "
             "download a study plan. Every setting is yours.")
    st.page_link("pages/3_Learning_Module.py", label="Open a lesson", icon=":material/menu_book:")
with b:
    st.markdown("#### Teachers")
    st.write("See class trends, who needs attention and why, the weakest skills, and set your own "
             "override on any suggestion. Export a PDF class report.")
    st.page_link("pages/6_Teacher_Dashboard.py", label="Open the dashboard", icon=":material/monitoring:")
with c:
    st.markdown("#### Schools and reviewers")
    st.write("Read how the model works, how accurate it is, what the data can and cannot show, and how "
             "the system avoids diagnosing or labelling students.")
    st.page_link("pages/7_Model_Card.py", label="Read the model card", icon=":material/fact_check:")

# ---- accessibility ----
st.markdown("## Every page adjusts to you")
st.write("Change these any time in the sidebar. They stay on as you move between pages.")
md('<div class="la la-chips">' + "".join(
    f'<span class="la-chip">{c}</span>' for c in [
        "Text size 80% to 200%", "High contrast", "Easy-to-read font", "Extra line spacing",
        "Read-aloud", "Captions for audio", "No time limits", "Full keyboard use"]) + "</div>")

# ---- call to action band (dark, image background) ----
with st.container(key="ctaband"):
    x, y = st.columns([2.2, 1], vertical_alignment="center", gap="large")
    with x:
        st.markdown("## Running a class? See every learner at a glance.")
        st.write("Explore a simulated cohort of 96 students across four classes: trends, skill gaps, "
                 "format mix and the learners who need support.")
    with y:
        st.page_link("pages/6_Teacher_Dashboard.py", label="Explore the teacher dashboard",
                     icon=":material/arrow_forward:")

st.write("")
with st.expander("About the data and its limits"):
    st.write(
        "The recommendation model is trained on a **simulated demonstration dataset** "
        "(1,500 synthetic learner interactions generated from documented rules), and the teacher "
        "dashboard uses a **simulated class of 96 students**. They show how the system works and are "
        "**not** evidence of real educational effectiveness. Real use would need real, consented data "
        "and evaluation with students, teachers and accessibility experts."
    )
