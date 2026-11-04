"""Glue between Streamlit pages and the ML / logic modules."""
import streamlit as st

from .accessibility import init_settings, inject_css, sidebar_settings
from .config import ASSETS_DIR, DEFAULT_PROFILE, MODEL_PATH
from .progress_tracking import profile_update_from_history
from .recommendation import Recommender, train_and_save


@st.cache_resource(show_spinner="Loading recommendation model...")
def get_recommender() -> Recommender:
    if MODEL_PATH.exists():
        try:
            return Recommender.load()
        except Exception:
            pass  # model file from another sklearn version: retrain
    return train_and_save()


def retrain_after_feedback() -> None:
    get_recommender().refit_fast()


def init_state() -> None:
    st.session_state.setdefault("profile", dict(DEFAULT_PROFILE))
    st.session_state.setdefault("profile_saved", False)
    st.session_state.setdefault("quiz_history", [])
    st.session_state.setdefault("quiz", None)
    st.session_state.setdefault("feedback_given", set())
    st.session_state.setdefault("formats_viewed", set())
    st.session_state.setdefault("overrides", {})


def page_setup(title: str, icon: str | None = None) -> None:
    """Page config, session state, brand logo, sidebar settings and the global theme."""
    st.set_page_config(page_title=f"{title} · LearnAble AI",
                       page_icon=str(ASSETS_DIR / "favicon.png"), layout="wide")
    st.logo(str(ASSETS_DIR / "logo.svg"), icon_image=str(ASSETS_DIR / "logo.svg"))
    init_state()
    init_settings()
    sidebar_settings()
    inject_css()


def current_profile() -> dict:
    """Profile with quiz-derived numbers merged in once quizzes exist."""
    p = dict(st.session_state.profile)
    p.update(profile_update_from_history(st.session_state.quiz_history))
    return p


def sections_done() -> int:
    """How many lesson sections the learner ticked as understood."""
    from .content import SECTIONS
    return sum(bool(st.session_state.get(f"und_{s['id']}")) for s in SECTIONS)
