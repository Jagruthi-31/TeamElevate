"""Smoke tests: every page renders without exceptions; core flows work."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["Home.py"] + [f"pages/{p.name}" for p in sorted((ROOT / "pages").glob("*.py"))]


def run(path):
    """Load via the main script so st.page_link resolves like in the real app."""
    at = AppTest.from_file(str(ROOT / "Home.py"), default_timeout=60).run()
    if path != "Home.py":
        at = at.switch_page(path).run()
    assert not at.exception, f"{path}: {[e.value for e in at.exception]}"
    return at


def test_all_pages_render():
    for p in PAGES:
        run(p)


def test_quiz_full_flow():
    at = run("pages/4_Quiz.py")
    at.button[0].click().run()                      # start quiz
    for _ in range(8):
        assert not at.exception
        at.radio[0].set_value(at.radio[0].options[0]).run()
        [b for b in at.button if b.label == "Check answer"][0].click().run()
        nxt = [b for b in at.button if b.label in ("Next question", "See my results")][0]
        nxt.click().run()
    assert not at.exception
    assert len(at.session_state.quiz_history) == 1


def test_progress_after_quiz_and_teacher():
    """Progress tabs, study plan and badges render after a quiz; teacher page and PDFs work."""
    at = run("pages/4_Quiz.py")
    at.button[0].click().run()
    for _ in range(8):
        at.radio[0].set_value(at.radio[0].options[0]).run()
        [b for b in at.button if b.label == "Check answer"][0].click().run()
        [b for b in at.button if b.label in ("Next question", "See my results")][0].click().run()
    at = at.switch_page("pages/5_Progress.py").run()
    assert not at.exception, [e.value for e in at.exception]
    at = at.switch_page("pages/6_Teacher_Dashboard.py").run()
    assert not at.exception, [e.value for e in at.exception]
    at = at.switch_page("pages/7_Model_Card.py").run()
    assert not at.exception, [e.value for e in at.exception]


def test_cohort_and_reports():
    from src.app_helpers import get_recommender
    from src.cohort import build_cohort, insights, kpis
    from src.reports import class_report_pdf
    c = build_cohort(get_recommender())
    st_df = c["students"]
    assert len(st_df) == 96 and set(st_df["status"]) <= {"On track", "Watch", "Needs attention"}
    assert st_df["suggested_format"].nunique() >= 3          # the model gives a realistic mix
    k = kpis(st_df, c["weekly"])
    pdf = class_report_pdf("All classes", st_df, c["weekly"], c["skills"], k, insights(st_df, c["skills"]), {})
    assert pdf[:4] == b"%PDF"


if __name__ == "__main__":
    test_all_pages_render(); print("pages ok")
    test_quiz_full_flow(); print("quiz flow ok")
    test_progress_after_quiz_and_teacher(); print("progress + teacher ok")
    test_cohort_and_reports(); print("cohort + pdf ok")
