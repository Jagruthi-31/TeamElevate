import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_helpers import get_recommender, page_setup
from src.cohort import CLASSES, STATUSES, WEEKS, build_cohort, insights, kpis
from src.config import FORMATS
from src.reports import class_report_pdf
from src.theme import (
    FORMAT_HEX, band_header, insight_list, kpi_cards, md, panel, status_pill, style_fig,
)

page_setup("Teacher Dashboard")
band_header("Teacher dashboard",
            "See how a class is learning: trends, skill gaps, who needs support and why. "
            "You stay in charge: any suggestion can be overridden.",
            tag="Simulated class of 96 students. Not real student data.")

CLASS_COLORS = {"Grade 6A": "#3A3FD8", "Grade 6B": "#0A7C74", "Grade 7A": "#A85A00", "Grade 7B": "#B8175F"}
STATUS_COLORS = {"On track": "#0B7A4B", "Watch": "#A85A00", "Needs attention": "#B3261E"}
SEVERITY = {"Needs attention": 0, "Watch": 1, "On track": 2}
KEEP = "Keep the model's suggestion"


@st.cache_data(show_spinner="Building the simulated class...")
def load_cohort() -> dict:
    return build_cohort(get_recommender())


cohort = load_cohort()
st.session_state.setdefault("overrides", {})
overrides: dict = st.session_state.overrides

students = cohort["students"].copy()
students["final_format"] = students.apply(
    lambda r: overrides.get(r["id"], {}).get("format") or r["suggested_format"], axis=1)

# ------------------------------------------------------------------ filters
with st.container(border=True):
    r1a, r1b = st.columns([1.15, 1], gap="large")
    sel_classes = r1a.pills("Class", CLASSES, selection_mode="multi", default=CLASSES) or []
    sel_status = r1b.pills("Status", STATUSES, selection_mode="multi", default=STATUSES) or []
    r2a, r2b = st.columns([1.6, 1], gap="large")
    sel_formats = r2a.multiselect("Suggested format", FORMATS, default=FORMATS)
    query = r2b.text_input("Find a student", placeholder="Name or ID").strip().lower()

df = students[students["class_name"].isin(sel_classes) & students["status"].isin(sel_status)
              & students["final_format"].isin(sel_formats)]
if query:
    df = df[df["name"].str.lower().str.contains(query) | df["id"].str.lower().str.contains(query)]
df = df.assign(_sev=df["status"].map(SEVERITY)).sort_values(["_sev", "latest_score"]).drop(columns="_sev")

if df.empty:
    st.info("No students match these filters. Widen a filter to see results.")
    st.stop()

scope = ", ".join(sel_classes) if len(sel_classes) < len(CLASSES) else "All classes"
k = kpis(df, cohort["weekly"])
kpi_cards([
    dict(label="Average score", value=f"{k['avg_score']:.0f}%", delta=k["score_delta"], unit_d=" pts",
         spark=k["score_trend"], sub="Change since the first 2 weeks"),
    dict(label="On track", value=f"{k['on_track_pct']:.0f}%", sub=f"{k['watch']} more on watch"),
    dict(label="Need attention", value=str(k["attention"]), sub="Open the Students tab to see why"),
    dict(label="Active learners", value=f"{k['active_pct']:.0f}%", spark=k["sessions_trend"],
         sub="Did 2 or more sessions last week"),
    dict(label="Time on task", value=f"{k['minutes_wk']:.0f} min", spark=k["minutes_trend"],
         sub="Per learner per week"),
])

tab_over, tab_students, tab_skills, tab_export = st.tabs(["Overview", "Students", "Skills", "Export"])

# ------------------------------------------------------------------ overview
with tab_over:
    weekly = cohort["weekly"][cohort["weekly"]["id"].isin(df["id"])]
    c1, c2 = st.columns([1.6, 1], gap="large")
    with c1:
        with st.container(border=True):
            panel("Average score by week", "")
            wk = weekly.groupby(["class_name", "week"], as_index=False)["score"].mean()
            fig = px.line(wk, x="week", y="score", color="class_name", color_discrete_map=CLASS_COLORS,
                          markers=True, labels={"week": "Week", "score": "Average score (%)", "class_name": ""})
            fig.update_traces(line=dict(width=3), marker=dict(size=7))
            fig.update_xaxes(dtick=1)
            fig.update_yaxes(range=[30, 100])
            st.plotly_chart(style_fig(fig, 330, top=50), width="stretch")
    with c2:
        with st.container(border=True):
            panel("What to act on this week", "")
            md(f'<div class="la">{insight_list(insights(df, cohort["skills"]))}</div>')

    c3, c4 = st.columns(2, gap="large")
    with c3:
        with st.container(border=True):
            panel("Suggested format mix", "")
            mix = df["final_format"].value_counts().reindex(FORMATS).fillna(0).reset_index()
            mix.columns = ["Format", "Students"]
            fig = px.bar(mix, x="Students", y="Format", orientation="h", color="Format",
                         color_discrete_map=FORMAT_HEX, text="Students")
            fig.update_layout(showlegend=False, yaxis_title="", yaxis_autorange="reversed")
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(style_fig(fig, 280, top=10), width="stretch")
    with c4:
        with st.container(border=True):
            panel("Status by class", "")
            stc = df.groupby(["class_name", "status"]).size().reset_index(name="Students")
            fig = px.bar(stc, x="class_name", y="Students", color="status", color_discrete_map=STATUS_COLORS,
                         category_orders={"status": STATUSES}, labels={"class_name": "", "status": ""})
            st.plotly_chart(style_fig(fig, 280, top=40), width="stretch")

# ------------------------------------------------------------------ students
def student_row(r) -> dict:
    ov = overrides.get(r["id"], {})
    return {
        "Student": r["name"], "ID": r["id"], "Class": r["class_name"], "Score": r["latest_score"],
        "8-week trend": r["trend"], "Status": r["status"],
        "Format": (ov["format"] + " (teacher)") if ov.get("format") else r["suggested_format"],
        "Weakest skill": r["weakest_skill"], "Sessions/wk": r["sessions_wk"],
    }


@st.dialog("Student detail", width="large")
def student_dialog(r: dict) -> None:
    ov = overrides.get(r["id"], {})
    md(f'<div class="la"><div class="la-panel-title" style="margin-bottom:.2rem">{r["name"]} '
       f'<span style="color:var(--muted);font-weight:500">({r["id"]}, {r["class_name"]})</span></div>'
       f'{status_pill(r["status"])}</div>')
    st.write(r["reason"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Latest score", f"{r['latest_score']:.0f}%")
    m2.metric("Since week 1", f"{r['change']:+.0f} pts")
    m3.metric("Sessions a week", f"{r['sessions_wk']:.1f}")
    m4.metric("Quizzes", r["quizzes"])

    left, right = st.columns([1.3, 1], gap="large")
    with left:
        fig = px.line(x=list(range(1, WEEKS + 1)), y=r["trend"], markers=True,
                      labels={"x": "Week", "y": "Score (%)"}, color_discrete_sequence=["#3A3FD8"])
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_yaxes(range=[0, 105])
        fig.update_xaxes(dtick=1)
        st.plotly_chart(style_fig(fig, 250, top=10), width="stretch")
    with right:
        st.markdown("**How this learner likes to learn**")
        st.progress(r["pref_text"] / 5, text=f"Reading text: {r['pref_text']}/5")
        st.progress(r["pref_audio"] / 5, text=f"Listening: {r['pref_audio']}/5")
        st.progress(r["pref_visual"] / 5, text=f"Diagrams: {r['pref_visual']}/5")

    st.markdown(f"**Model suggestion:** {r['suggested_format']}"
                + (f", then {r['second_format']}" if r["second_format"] else "")
                + f" &nbsp;|&nbsp; **Support level:** {r['support_level']}")
    st.caption("A suggestion about how to teach, not a label for the student.")
    options = [KEEP] + FORMATS
    choice = st.selectbox("Teacher override", options, index=options.index(ov["format"]) if ov.get("format") in FORMATS else 0)
    note = st.text_area("Note (optional)", value=ov.get("note", ""), max_chars=200,
                        placeholder="For example: responds well to short audio clips.")
    if st.button("Save override", type="primary"):
        if choice == KEEP:
            overrides.pop(r["id"], None)
        else:
            overrides[r["id"]] = {"format": choice, "note": note.strip()}
        st.toast("Override saved." if choice != KEEP else "Back to the model's suggestion.")
        st.rerun()


with tab_students:
    st.caption(f"{len(df)} students shown, with the most urgent first. Select a row, then open the details. "
               "Click a column header to sort.")
    view = pd.DataFrame([student_row(r) for _, r in df.iterrows()])
    event = st.dataframe(
        view, hide_index=True, width="stretch", height=430, on_select="rerun",
        selection_mode="single-row", key="students_table",
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d%%"),
            "8-week trend": st.column_config.LineChartColumn("8-week trend", y_min=0, y_max=100),
            "Sessions/wk": st.column_config.NumberColumn("Sessions/wk", format="%.1f"),
        })
    rows = event.selection.rows if event and event.selection else []
    if rows:
        chosen = df.iloc[rows[0]] if rows[0] < len(df) else None
        if chosen is not None and st.button(f"Open details for {chosen['name']}", type="primary", icon=":material/open_in_new:"):
            student_dialog(chosen.to_dict())
    else:
        st.info("Select a row in the table to open a student's details and set an override.")

# ------------------------------------------------------------------ skills
with tab_skills:
    sk = cohort["skills"][cohort["skills"]["id"].isin(df["id"])]
    s1, s2 = st.columns([1.3, 1], gap="large")
    with s1:
        with st.container(border=True):
            panel("Average accuracy by class and skill", "")
            heat = sk.groupby(["skill", "class_name"])["accuracy"].mean().unstack().round(0)
            fig = px.imshow(heat, text_auto=".0f", aspect="auto", zmin=30, zmax=90,
                            color_continuous_scale=[[0, "#A85A00"], [0.5, "#F4F5FB"], [1, "#0A7C74"]],
                            labels={"color": "%"})
            fig.update_layout(xaxis_title="", yaxis_title="", coloraxis_showscale=False)
            fig.update_xaxes(side="top")
            st.plotly_chart(style_fig(fig, 340, top=40), width="stretch")
    with s2:
        with st.container(border=True):
            panel("Share of students below 60%", "")
            low = sk.groupby("skill")["accuracy"].apply(lambda s: (s < 60).mean() * 100).sort_values().reset_index()
            low.columns = ["Skill", "Below 60 (%)"]
            fig = px.bar(low, x="Below 60 (%)", y="Skill", orientation="h", text=low["Below 60 (%)"].round(0),
                         color_discrete_sequence=["#A85A00"])
            fig.update_layout(yaxis_title="", xaxis_range=[0, 100])
            fig.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
            st.plotly_chart(style_fig(fig, 330, top=10), width="stretch")

    with st.container(border=True):
        panel("Suggested focus for small-group sessions", "")
        rows_ = []
        for skill, pct in low.sort_values("Below 60 (%)", ascending=False).head(3).itertuples(index=False):
            grp = df[df["weakest_skill"] == skill]
            fmt = grp["final_format"].mode().iat[0] if len(grp) else "Step-by-step"
            rows_.append({"Skill": skill, "Students below 60%": f"{pct:.0f}%",
                          "Students whose weakest skill this is": len(grp),
                          "Try this format first": fmt})
        st.dataframe(pd.DataFrame(rows_), hide_index=True, width="stretch")

# ------------------------------------------------------------------ export
with tab_export:
    e1, e2 = st.columns(2, gap="large")
    with e1:
        with st.container(border=True):
            panel("Class data (CSV)", "")
            st.write("The table of students currently shown, including any overrides.")
            out = pd.DataFrame([student_row(r) for _, r in df.iterrows()]).drop(columns=["8-week trend"])
            st.download_button("Download CSV", out.to_csv(index=False), file_name="class_overview.csv",
                               mime="text/csv", icon=":material/download:")
    with e2:
        with st.container(border=True):
            panel("Class report (PDF)", "")
            st.write("A two-page summary with charts, the weekly actions and the students who need attention.")
            if st.button("Prepare PDF report", icon=":material/description:"):
                with st.spinner("Building the report..."):
                    st.session_state.class_pdf = class_report_pdf(
                        scope, df, cohort["weekly"], cohort["skills"], k,
                        insights(df, cohort["skills"]), overrides)
            if st.session_state.get("class_pdf"):
                st.download_button("Download PDF report", st.session_state.class_pdf,
                                   file_name="class_report.pdf", mime="application/pdf",
                                   type="primary", icon=":material/download:")
    if overrides:
        with st.container(border=True):
            panel("Your overrides", "")
            names = students.set_index("id")["name"]
            st.dataframe(pd.DataFrame([{"Student": names[i], "ID": i, "Format": o["format"], "Note": o["note"]}
                                       for i, o in overrides.items()]), hide_index=True, width="stretch")
