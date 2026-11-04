import streamlit as st

from src.app_helpers import current_profile, get_recommender, page_setup
from src.config import FEATURE_LABELS, FEATURES
from src.theme import bullet_list, md, page_header, panel, ranking_bars, result_card
from src.config import COMPLEXITY_LABELS, SPEED_LABELS

page_setup("AI Recommendations")
page_header("Your AI recommendation",
            "The model compares you with similar learners and suggests the format that worked "
            "best for them. It is only a suggestion.", step=2)

if not st.session_state.profile_saved:
    st.warning("Save your learning profile first for a personal result. "
               "This page shows a result for neutral default values.")
    st.page_link("pages/1_Student_Profile.py", label="Go to your learning profile",
                 icon=":material/arrow_back:")

profile = current_profile()
rec = get_recommender().recommend(profile)
st.session_state.last_rec = rec

tab_res, tab_what = st.tabs(["Your result", "What-if explorer"])

with tab_res:
    result_card(rec["top_format"], rec["second_format"])
    st.caption("You can always choose any format on the Learning Module page.")

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        with st.container(border=True):
            panel("Why this suggestion?", bullet_list(rec["reasons"]))
        with st.container(border=True):
            panel(f"Your support plan ({rec['support_level']} support)", bullet_list(rec["adaptations"]))

    with right:
        with st.container(border=True):
            panel("Share of similar learners it worked for", ranking_bars(rec["ranking"]))
            st.caption(f"Based on the {rec['similar_learners']} most similar learners. "
                       f"Computed in {rec['response_ms']:.1f} ms.")

    with st.expander("See the similar learners the model used"):
        tbl = rec["neighbour_table"].rename(columns=FEATURE_LABELS)
        st.dataframe(tbl.round(2), width="stretch", hide_index=True)
        st.caption("The 5 closest learners are shown. A smaller distance means a learner is more "
                   "similar to you. These learners are simulated.")

    with st.expander("Your current inputs to the model"):
        st.table({FEATURE_LABELS[f]: [round(profile[f], 1)] for f in FEATURES})

    st.page_link("pages/3_Learning_Module.py", label="Next: open the lesson", icon=":material/arrow_forward:")

with tab_what:
    st.write("Change the sliders to see how the suggestion would move. This is for exploring only: "
             "your saved profile does not change.")

    BASE = {"wi_text": int(profile["pref_text"]), "wi_audio": int(profile["pref_audio"]),
            "wi_visual": int(profile["pref_visual"]), "wi_speed": int(profile["reading_speed"]),
            "wi_pace": int(profile["pace"]), "wi_detail": int(profile["complexity_pref"]),
            "wi_score": int(round(profile["quiz_score"]))}

    def reset_whatif():
        for k_, v_ in BASE.items():
            st.session_state[k_] = v_

    @st.fragment
    def whatif():
        for k_, v_ in BASE.items():
            st.session_state.setdefault(k_, v_)
        ctl, out = st.columns([1, 1.2], gap="large")
        with ctl:
            with st.container(border=True):
                panel("Try different answers", "")
                st.slider("Likes reading text", 1, 5, key="wi_text")
                st.slider("Likes listening", 1, 5, key="wi_audio")
                st.slider("Likes diagrams", 1, 5, key="wi_visual")
                st.select_slider("Reading speed", [1, 2, 3], key="wi_speed", format_func=SPEED_LABELS.get)
                st.select_slider("Learning pace", [1, 2, 3], key="wi_pace",
                                 format_func={1: "Slower", 2: "Normal", 3: "Faster"}.get)
                st.select_slider("Explanation detail", [1, 2, 3], key="wi_detail", format_func=COMPLEXITY_LABELS.get)
                st.slider("Latest quiz score (%)", 0, 100, key="wi_score")
                st.button("Reset to my profile", on_click=reset_whatif, icon=":material/restart_alt:")
        trial = {**profile, "pref_text": st.session_state.wi_text, "pref_audio": st.session_state.wi_audio,
                 "pref_visual": st.session_state.wi_visual, "reading_speed": st.session_state.wi_speed,
                 "pace": st.session_state.wi_pace, "complexity_pref": st.session_state.wi_detail,
                 "quiz_score": float(st.session_state.wi_score)}
        r2 = get_recommender().recommend(trial)
        with out:
            result_card(r2["top_format"], r2["second_format"])
            if r2["top_format"] != rec["top_format"]:
                st.warning(f"This change would move your suggestion from **{rec['top_format']}** to "
                           f"**{r2['top_format']}**.")
            else:
                st.success(f"Same suggestion as your profile: **{r2['top_format']}**.")
            with st.container(border=True):
                panel("Share of similar learners it worked for", ranking_bars(r2["ranking"]))
                st.caption(f"Support level: {r2['support_level']}. Computed in {r2['response_ms']:.1f} ms.")

    whatif()
