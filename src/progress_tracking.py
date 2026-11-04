"""Progress tracking: quiz history, per-skill accuracy, next-step suggestions."""
from datetime import datetime

import pandas as pd

ATTENTION_THRESHOLD = 60  # % accuracy below which a skill needs attention


def make_quiz_record(quiz_no: int, answers: list[dict]) -> dict:
    """Summarise one finished quiz. `answers` items: question dict fields + correct + seconds."""
    n = len(answers)
    correct = sum(a["correct"] for a in answers)
    return {
        "quiz_no": quiz_no,
        "time": datetime.now().strftime("%H:%M"),
        "questions": n,
        "correct": correct,
        "score_pct": round(100 * correct / n, 1) if n else 0.0,
        "avg_seconds": round(sum(a["seconds"] for a in answers) / n, 1) if n else 0.0,
        "total_minutes": round(sum(a["seconds"] for a in answers) / 60, 1),
        "final_difficulty": answers[-1]["d"] if n else 1,
        "difficulty_path": [a["d"] for a in answers],
        "answers": answers,
    }


def history_frame(history: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([{k: v for k, v in r.items() if k != "answers"} for r in history])


def skill_accuracy(history: list[dict]) -> pd.DataFrame:
    rows = [{"skill": a["skill"], "correct": a["correct"]}
            for r in history for a in r["answers"]]
    if not rows:
        return pd.DataFrame(columns=["skill", "accuracy", "answered"])
    df = pd.DataFrame(rows)
    out = df.groupby("skill")["correct"].agg(["mean", "count"]).reset_index()
    out.columns = ["skill", "accuracy", "answered"]
    out["accuracy"] = (out["accuracy"] * 100).round(0)
    return out.sort_values("accuracy").reset_index(drop=True)


def improvement(history: list[dict]) -> float | None:
    if len(history) < 2:
        return None
    return round(history[-1]["score_pct"] - history[0]["score_pct"], 1)


def next_steps(history: list[dict]) -> list[str]:
    if not history:
        return ["Take your first quiz to see your progress here."]
    steps = []
    weak = skill_accuracy(history)
    weak = weak[weak["accuracy"] < ATTENTION_THRESHOLD]
    if len(weak):
        names = ", ".join(weak["skill"].head(3))
        steps.append(f"Revisit the lesson sections on: {names}.")
    last = history[-1]
    if last["score_pct"] >= 75:
        steps.append("Strong result. Try another quiz to reach the challenging questions.")
    elif last["score_pct"] >= 50:
        steps.append("Good progress. One more quiz will help lock in the ideas.")
    else:
        steps.append("Re-read the lesson in a different format, then retry the quiz. "
                     "There is no time limit.")
    imp = improvement(history)
    if imp is not None and imp > 0:
        steps.append(f"Your score has improved by {imp:.0f} points since the first quiz.")
    return steps


def profile_update_from_history(history: list[dict]) -> dict:
    """Numbers fed back to the recommender after quizzes."""
    if not history:
        return {}
    return {
        "quiz_score": history[-1]["score_pct"],
        "attempts": min(len(history), 10),
        "time_spent_min": max(1.0, round(sum(r["total_minutes"] for r in history), 1)),
    }
