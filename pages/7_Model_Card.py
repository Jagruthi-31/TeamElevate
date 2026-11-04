import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_helpers import page_setup
from src.config import ASSETS_DIR, EVAL_JSON, FORMATS
from src.theme import FORMAT_HEX, band_header, bullet_list, kpi_cards, panel, style_fig

page_setup("Model Card")
band_header("Model card",
            "How the recommendation works, how well it performs, and where it should not be trusted.",
            tag="Transparent by design")

ev = json.loads(EVAL_JSON.read_text())

kpi_cards([
    dict(label="Test accuracy", value=f"{ev['test_accuracy'] * 100:.0f}%",
         sub=f"4 formats. Chance is 25%, always-pick-the-commonest is {ev['majority_class_baseline_accuracy'] * 100:.0f}%"),
    dict(label="Top-2 accuracy", value=f"{ev['test_top2_accuracy'] * 100:.0f}%",
         sub="Right format is among the two suggested"),
    dict(label="Macro F1", value=f"{ev['test_macro_f1']:.2f}", sub="Balanced across all four formats"),
    dict(label="Response time", value=f"{ev['mean_response_ms']:.0f} ms", sub=f"95th percentile {ev['p95_response_ms']:.0f} ms"),
])
st.caption(f"Measured on {ev['n_test_examples']} held-out examples from a simulated dataset "
           f"({ev['n_training_examples']} training examples). Reproduce with `python -m src.evaluate`.")

tab_how, tab_perf, tab_resp, tab_next = st.tabs(["How it works", "Performance", "Responsible use", "Limits and roadmap"])

with tab_how:
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(border=True):
            panel("Model A: format recommender", bullet_list([
                "Inputs: preference for text, audio and diagrams, reading speed, pace, explanation detail, "
                "latest quiz score, attempts and time spent.",
                "Method: scale the inputs, then K-Nearest Neighbours. It finds the learners most like you "
                f"(k = {ev['best_params']['n_neighbors']}, {ev['best_params']['metric']} distance).",
                "Training data: past interactions where the format worked well (rated 4 or 5 and the quiz "
                "score rose by 10 points or more).",
                "Feedback loop: when a learner rates a format 4 or 5, it joins the data and the model refits.",
            ]))
    with b:
        with st.container(border=True):
            panel("Model B: adaptive difficulty", bullet_list([
                "A readable rule, not a black box, so a teacher can understand and override it.",
                "Looks at the last 3 answers: below 40% gives easier questions, 40 to 70% keeps the level, "
                "above 70% gives harder questions.",
                "The 18-question bank has 3 levels and every question is tagged with a skill.",
            ]))

with tab_perf:
    p1, p2 = st.columns([1.2, 1], gap="large")
    with p1:
        with st.container(border=True):
            panel("Precision, recall and F1 by format", "")
            rows = [{"Format": f, "Metric": m.title() if m != "f1-score" else "F1", "Score": ev["per_class_report"][f][m]}
                    for f in FORMATS if f in ev["per_class_report"] for m in ("precision", "recall", "f1-score")]
            fig = px.bar(pd.DataFrame(rows), x="Format", y="Score", color="Metric", barmode="group",
                         color_discrete_sequence=["#3A3FD8", "#0A7C74", "#A85A00"])
            fig.update_layout(xaxis_title="", yaxis_range=[0, 1])
            st.plotly_chart(style_fig(fig, 330, top=50), width="stretch")
    with p2:
        with st.container(border=True):
            panel("Confusion matrix", "")
            cm = ASSETS_DIR / "confusion_matrix.png"
            if cm.exists():
                st.image(str(cm), width="stretch")
    with st.container(border=True):
        panel("Does it match common sense? Five reference personas", "")
        st.dataframe(pd.DataFrame(ev["personas"]).rename(columns={
            "persona": "Persona", "expected": "Expected", "recommended": "Model said", "agree": "Agrees"}),
            hide_index=True, width="stretch")
        st.caption(f"Agreement: {ev['persona_agreement'] * 100:.0f}%. The one miss (a fast visual learner) is why the "
                   "app shows the top two options and lets the learner choose.")

with tab_resp:
    r1, r2 = st.columns(2, gap="large")
    with r1:
        with st.container(border=True):
            panel("What the system will not do", bullet_list([
                "It never diagnoses a disability or labels a student. It only suggests how to teach.",
                "Learners choose their own preferences and accessibility settings.",
                "A teacher can override any suggestion, and the override is recorded.",
                "The quiz has no time limit, and difficulty only changes by a readable rule.",
            ]))
    with r2:
        with st.container(border=True):
            panel("Data and privacy", bullet_list([
                "The names and results in the teacher dashboard are simulated.",
                "Feedback stored for retraining holds the learning features and the rating only, never a name.",
                "Everything runs in the app. No student data is sent to a third party.",
                "Fonts are hosted with the app, so no external font service is contacted.",
            ]))

with tab_next:
    n1, n2 = st.columns(2, gap="large")
    with n1:
        with st.container(border=True):
            panel("Honest limitations", bullet_list([
                "The training data is simulated, so the accuracy shows how the system works, not real classroom impact.",
                "One topic (fractions) and four formats so far.",
                "Self-reported preferences can differ from what actually helps a learner.",
                "Not yet audited with screen readers or against WCAG.",
            ]))
    with n2:
        with st.container(border=True):
            panel("Roadmap to a pilot", bullet_list([
                "Run a consented pilot with real classes and measure learning gain, not just accuracy.",
                "Add more subjects and lesson formats, with teacher-authored content.",
                "Single sign-on and a school-wide teacher view with permissions.",
                "Accessibility audit with disabled learners and experts, then fix what they find.",
                "Add explanations written by an LLM, behind safety checks and teacher review.",
            ]))
