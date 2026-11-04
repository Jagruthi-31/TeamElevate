import html
import random
import time

import streamlit as st

from src.adaptive_quiz import (
    DIFFICULTY_NAMES, QUIZ_LENGTH, initial_difficulty, next_difficulty, pick_question,
    shuffled_options,
)
from src.app_helpers import current_profile, page_setup
from src.progress_tracking import make_quiz_record
from src.theme import md, page_header, verdict

page_setup("Quiz")
page_header("Adaptive quiz: fractions",
            "Questions get easier or harder depending on how you are doing. There is no time limit.",
            step=4)


def new_quiz():
    prior = current_profile()["quiz_score"]
    d = initial_difficulty(prior)
    st.session_state.quiz = {
        "difficulty": d, "answers": [], "used": set(), "current": None,
        "submitted": False, "message": "Starting level", "start": time.time(),
    }


def load_question(qz):
    q = pick_question(qz["difficulty"], qz["used"])
    options, correct = shuffled_options(q)
    qz["current"] = {"q": q, "options": options, "correct": correct, "shown_at": time.time()}
    qz["used"].add(q["id"])
    qz["submitted"] = False


qz = st.session_state.quiz

if qz is None:
    rec_last = st.session_state.get("last_record")
    if rec_last and st.session_state.pop("just_finished", False):
        st.toast(f"Quiz complete! +{10 * rec_last['correct'] + 25} XP", icon=":material/emoji_events:")
        if rec_last["score_pct"] >= 100:
            st.balloons()
    if rec_last:
        with st.container(border=True):
            md(f'<div class="la"><p class="la-panel-title">Quiz complete</p>'
               f'<div class="la-score">{rec_last["correct"]}/{rec_last["questions"]}</div></div>')
            st.write(f"That is **{rec_last['score_pct']:.0f}%**, finishing at the "
                     f"**{DIFFICULTY_NAMES[rec_last['final_difficulty']]}** level. "
                     "Your recommendation and progress have been updated.")
            c1, c2 = st.columns(2)
            with c1:
                st.page_link("pages/5_Progress.py", label="See my progress", icon=":material/monitoring:")
            with c2:
                st.page_link("pages/2_AI_Recommendations.py", label="See my updated recommendation",
                             icon=":material/auto_awesome:")
    with st.container(border=True):
        md(f'<div class="la"><p class="la-panel-title">{"Take it again" if rec_last else "Ready when you are"}</p></div>')
        st.write(f"The quiz has {QUIZ_LENGTH} questions on fractions. Every answer comes with an explanation.")
        if st.button("Start quiz", type="primary"):
            new_quiz()
            load_question(st.session_state.quiz)
            st.rerun()
    st.stop()

answers = qz["answers"]

# ---- finished ----
if len(answers) >= QUIZ_LENGTH and qz["current"] is None:
    record = make_quiz_record(len(st.session_state.quiz_history) + 1, answers)
    st.session_state.quiz_history.append(record)
    st.session_state.quiz = None
    st.session_state.last_record = record
    st.session_state.just_finished = True
    st.rerun()

# ---- in progress ----
cur = qz["current"]
q = cur["q"]
with st.container(border=True):
    st.progress(len(answers) / QUIZ_LENGTH, text=f"Question {len(answers) + 1} of {QUIZ_LENGTH}")
    streak = 0
    for a_ in reversed(answers):
        if not a_["correct"]:
            break
        streak += 1
    streak_pill = f'<span class="la-pill">{streak} correct in a row</span>' if streak >= 2 else ""
    md(f'<div class="la"><div class="la-qmeta"><span class="la-pill">Level: {DIFFICULTY_NAMES[q["d"]]}</span>'
       f'{streak_pill}<span>{qz["message"]}</span></div><h2 class="la-question">{html.escape(q["q"])}</h2></div>')
    choice = st.radio("Choose an answer", cur["options"], index=None,
                      key=f"ans_{len(answers)}", disabled=qz["submitted"])

    with st.expander("Need a hint?"):
        st.write(q["hint"])

    if not qz["submitted"]:
        if st.button("Check answer", type="primary", disabled=choice is None):
            is_correct = cur["options"].index(choice) == cur["correct"]
            seconds = round(time.time() - cur["shown_at"], 1)
            answers.append({"id": q["id"], "d": q["d"], "skill": q["skill"],
                            "correct": is_correct, "seconds": seconds})
            qz["submitted"] = True
            qz["difficulty"], qz["message"] = next_difficulty(
                qz["difficulty"], [a["correct"] for a in answers])
            st.rerun()
    else:
        last = answers[-1]
        if last["correct"]:
            verdict(True, "Correct!")
        else:
            verdict(False, f"Not quite. The answer is {html.escape(cur['options'][cur['correct']])}")
        st.write(q["explain"])
        st.caption(qz["message"])
        label = "See my results" if len(answers) >= QUIZ_LENGTH else "Next question"
        if st.button(label, type="primary"):
            if len(answers) >= QUIZ_LENGTH:
                qz["current"] = None
            else:
                load_question(qz)
            st.rerun()
