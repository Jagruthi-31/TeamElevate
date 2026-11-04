"""Achievements, XP and a study plan, all derived from the student's own activity."""
import pandas as pd

from .progress_tracking import ATTENTION_THRESHOLD, improvement, skill_accuracy

XP_PER_LEVEL = 100


def xp_total(history: list[dict], formats_viewed: set, profile_saved: bool, feedback_n: int,
             sections_done: int = 0) -> int:
    xp = sum(10 * r["correct"] + 25 for r in history) + 5 * sections_done
    xp += 15 * len(formats_viewed) + (20 if profile_saved else 0) + 10 * feedback_n
    return xp


def level_info(xp: int) -> dict:
    level = xp // XP_PER_LEVEL + 1
    into = xp % XP_PER_LEVEL
    return {"level": level, "into": into, "need": XP_PER_LEVEL - into, "pct": into / XP_PER_LEVEL}


def _max_difficulty(history) -> int:
    return max((a["d"] for r in history for a in r["answers"]), default=0)


def badges(history: list[dict], formats_viewed: set, profile_saved: bool, feedback_n: int,
           sections_done: int = 0) -> list[dict]:
    imp = improvement(history)
    best = max((r["score_pct"] for r in history), default=0)
    return [
        dict(name="First steps", desc="Save your learning profile.", earned=profile_saved, glyph="text"),
        dict(name="Quiz starter", desc="Finish your first quiz.", earned=len(history) >= 1, glyph="steps"),
        dict(name="Sharp mind", desc="Score 80% or more on a quiz.", earned=best >= 80, glyph="visual"),
        dict(name="Perfect run", desc="Answer every question correctly.", earned=best >= 100, glyph="audio"),
        dict(name="Climber", desc="Reach a hard question.", earned=_max_difficulty(history) >= 3, glyph="steps"),
        dict(name="On the rise", desc="Improve your score by 10 points.", earned=bool(imp and imp >= 10), glyph="visual"),
        dict(name="Explorer", desc="Try 3 different lesson formats.", earned=len(formats_viewed) >= 3, glyph="text"),
        dict(name="Steady learner", desc="Finish 3 quizzes.", earned=len(history) >= 3, glyph="audio"),
        dict(name="Bookworm", desc="Finish all four lesson sections.", earned=sections_done >= 4, glyph="text"),
        dict(name="Voice heard", desc="Rate a lesson format.", earned=feedback_n >= 1, glyph="text"),
    ]


def study_plan(history: list[dict], top_format: str, pace: int) -> pd.DataFrame:
    """A simple 5-day plan: weakest skills first, then mixed practice and a check-in quiz."""
    sk = skill_accuracy(history)
    weak = list(sk[sk["accuracy"] < ATTENTION_THRESHOLD]["skill"]) or list(sk["skill"].head(2))
    weak = (weak + ["Mixed fractions review"] * 3)[:3]
    mins = {1: 10, 2: 15, 3: 20}[int(pace)]
    rows = [
        ("Day 1", f"Re-read the lesson section on {weak[0]}", top_format, mins),
        ("Day 2", f"Practice quiz focusing on {weak[0]}", "Adaptive quiz", mins),
        ("Day 3", f"Re-read the lesson section on {weak[1]}", top_format, mins),
        ("Day 4", f"Mixed review of {weak[1]} and {weak[2]}", "Step-by-step", mins),
        ("Day 5", "Check-in quiz to see your progress", "Adaptive quiz", mins + 5),
    ]
    return pd.DataFrame(rows, columns=["Day", "What to do", "Format", "Minutes"])
