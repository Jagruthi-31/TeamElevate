import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.app_helpers import current_profile, get_recommender, page_setup, sections_done
from src.gamification import badges, level_info, study_plan, xp_total
from src.progress_tracking import (
    ATTENTION_THRESHOLD, history_frame, improvement, next_steps, skill_accuracy,
)
from src.reports import student_report_pdf
from src.theme import badge_grid, bullet_list, md, page_header, panel, style_fig, xp_ring

page_setup("Progress")
page_header("Your progress",
            "See how your scores change, what you have earned, and what to practise next.", step=5)

history = st.session_state.quiz_history
if not history:
    with st.container(border=True):
        md('<div class="la"><p class="la-panel-title">No quizzes yet</p>'
           '<p>Take your first quiz and your score trend, badges, study plan and report will appear here.</p></div>')
        st.page_link("pages/4_Quiz.py", label="Take your first quiz", icon=":material/arrow_forward:")
    st.stop()

df = history_frame(history)
imp = improvement(history)
skills = skill_accuracy(history)
profile = current_profile()
rec = get_recommender().recommend(profile)
steps = next_steps(history)

done = sections_done()
fb_n = len(st.session_state.feedback_given)
xp = xp_total(history, st.session_state.formats_viewed, st.session_state.profile_saved, fb_n, done)
lvl = level_info(xp)
all_badges = badges(history, st.session_state.formats_viewed, st.session_state.profile_saved, fb_n, done)
plan = study_plan(history, rec["top_format"], profile["pace"])

tab_over, tab_ach, tab_plan, tab_rep = st.tabs(["Overview", "Achievements", "Study plan", "Report"])

# ------------------------------------------------------------------ overview
with tab_over:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quizzes taken", len(history))
    c2.metric("Latest score", f"{history[-1]['score_pct']:.0f}%")
    c3.metric("Best score", f"{df['score_pct'].max():.0f}%")
    c4.metric("Change since first quiz", "n/a" if imp is None else f"{imp:+.0f} pts")

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            panel("Quiz score over time", "")
            fig = go.Figure(go.Scatter(x=df["quiz_no"], y=df["score_pct"], mode="lines+markers",
                                       line=dict(color="#3A3FD8", width=4), marker=dict(size=12)))
            fig.update_layout(xaxis=dict(title="Quiz #", dtick=1), yaxis=dict(title="Score (%)", range=[0, 105]))
            st.plotly_chart(style_fig(fig, 320, top=10), width="stretch")
    with right:
        with st.container(border=True):
            panel("Accuracy by skill", "")
            sk = skills.copy()
            sk["status"] = sk["accuracy"].apply(lambda a: "Needs attention" if a < ATTENTION_THRESHOLD else "On track")
            fig2 = px.bar(sk, x="accuracy", y="skill", orientation="h", color="status",
                          color_discrete_map={"Needs attention": "#A85A00", "On track": "#0A7C74"},
                          text="accuracy", range_x=[0, 110])
            fig2.update_layout(xaxis_title="Accuracy (%)", yaxis_title="", legend_title_text="")
            st.plotly_chart(style_fig(fig2, 320, top=40), width="stretch")

    with st.container(border=True):
        panel("Recommended next steps", bullet_list(steps))

    weak = skills[skills["accuracy"] < ATTENTION_THRESHOLD]
    if len(weak):
        st.markdown("## Topics that need attention")
        st.table(weak[["skill", "accuracy", "answered"]].astype({"accuracy": int}).rename(
            columns={"skill": "Skill", "accuracy": "Accuracy (%)", "answered": "Questions answered"}))

    with st.expander("Quiz history"):
        show = df[["quiz_no", "time", "correct", "questions", "score_pct", "final_difficulty", "total_minutes"]]
        st.dataframe(show, width="stretch", hide_index=True)
        st.download_button("Download my progress (CSV)", show.to_csv(index=False),
                           file_name="my_progress.csv", mime="text/csv")

# ------------------------------------------------------------------ achievements
with tab_ach:
    with st.container(border=True):
        md(f'<div class="la la-level">{xp_ring(lvl["level"], lvl["pct"])}<div class="info">'
           f'<div class="big">{xp} XP</div><p>{lvl["need"]} XP to reach level {lvl["level"] + 1}.</p>'
           f'<p class="la-note">Earn XP by finishing quizzes (25 XP plus 10 for each correct answer), trying lesson '
           f'formats (15), ticking off lesson sections (5), saving your profile (20) and rating a format (10).</p>'
           f'</div></div>')
    earned = sum(b["earned"] for b in all_badges)
    st.markdown(f"## Badges: {earned} of {len(all_badges)} earned")
    badge_grid(all_badges)

# ------------------------------------------------------------------ study plan
with tab_plan:
    st.write(f"A five-day plan built from your weakest skills, in your suggested format "
             f"(**{rec['top_format']}**), at a **{ {1: 'slower', 2: 'normal', 3: 'faster'}[int(profile['pace'])] }** pace. "
             "Tick each day when you finish it.")
    table = plan.assign(Done=False)
    edited = st.data_editor(
        table, hide_index=True, width="stretch", key="plan_editor",
        disabled=["Day", "What to do", "Format", "Minutes"],
        column_config={"Done": st.column_config.CheckboxColumn("Done", default=False),
                       "What to do": st.column_config.TextColumn(width="large")})
    n_done = int(edited["Done"].sum())
    st.progress(n_done / len(edited), text=f"{n_done} of {len(edited)} days done")
    if n_done == len(edited):
        st.success("Plan complete. Take a new quiz to see how far you have come.")
    st.download_button("Download plan (CSV)", plan.to_csv(index=False), file_name="study_plan.csv",
                       mime="text/csv", icon=":material/download:")

# ------------------------------------------------------------------ report
with tab_rep:
    with st.container(border=True):
        panel("Progress report (PDF)", "")
        st.write("A one-page summary to share with a teacher or keep for yourself: score trend, skills, "
                 "your suggested format, next steps and the study plan.")
        if st.button("Prepare PDF report", icon=":material/description:"):
            with st.spinner("Building your report..."):
                st.session_state.student_pdf = student_report_pdf(
                    profile.get("name", ""), history, rec, skills, steps, plan, lvl["level"], xp)
        if st.session_state.get("student_pdf"):
            st.download_button("Download PDF report", st.session_state.student_pdf,
                               file_name="my_learning_report.pdf", mime="application/pdf",
                               type="primary", icon=":material/download:")
