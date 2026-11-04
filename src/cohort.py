"""Simulated class cohort for the teacher dashboard.

Everything here is SIMULATED (seeded, reproducible). No real students. The cohort is built so the
dashboard can show what a school would see: class trends, who needs attention, which skills are
weak, and which learning format the model suggests for each learner.

The system never diagnoses or labels a student: it only reports learning activity and format
preferences, and a teacher can override any suggestion.
"""
import numpy as np
import pandas as pd

from .adaptive_quiz import QUESTIONS

CLASSES = ["Grade 6A", "Grade 6B", "Grade 7A", "Grade 7B"]
CLASS_OFFSET = {"Grade 6A": 4, "Grade 6B": 0, "Grade 7A": -3, "Grade 7B": 1}
WEEKS = 8
SKILLS = sorted({q["skill"] for q in QUESTIONS})
SKILL_EFFECT = {"Reading fractions": 8, "Parts of a fraction": 6, "Comparing fractions": 0,
                "Adding & subtracting": -5, "Equivalent fractions": -8, "Multiplying & dividing": -10}
STATUSES = ["On track", "Watch", "Needs attention"]

_FIRST = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Isha", "Arjun", "Anaya", "Vihaan", "Saanvi",
          "Neil", "Tara", "Ishan", "Riya", "Dev", "Nisha", "Karan", "Pooja", "Yash", "Sana",
          "Omar", "Leila", "Noah", "Maya", "Liam", "Zoya", "Ethan", "Aisha", "Lucas", "Priya",
          "Sam", "Nora", "Ravi", "Anika", "Jay", "Kiara", "Tejas", "Mira", "Zane", "Esha",
          "Veer", "Lina", "Aryan", "Sia", "Dhruv", "Jiya", "Reyansh", "Avni"]
_INITIALS = "ABCDEFGHJKLMNPRSTV"


def _sample_profile(rng) -> dict:
    dominant = rng.choice(["pref_text", "pref_audio", "pref_visual"], p=[.34, .28, .38])
    prefs = {k: int(rng.integers(1, 4)) for k in ("pref_text", "pref_audio", "pref_visual")}
    prefs[dominant] = int(rng.integers(4, 6))
    return {**prefs,
            "reading_speed": int(rng.choice([1, 2, 3], p=[.25, .5, .25])),
            "pace": int(rng.choice([1, 2, 3], p=[.25, .55, .20])),
            "complexity_pref": int(rng.choice([1, 2, 3], p=[.3, .45, .25]))}


def build_cohort(recommender, per_class: int = 24, seed: int = 11) -> dict:
    """Return {'students': DataFrame, 'weekly': DataFrame (student x week), 'skills': DataFrame}."""
    rng = np.random.default_rng(seed)
    students, weekly, skill_rows = [], [], []
    n = 0
    for cls in CLASSES:
        for _ in range(per_class):
            sid = f"S-{1000 + n}"
            name = f"{_FIRST[n % len(_FIRST)]} {_INITIALS[(n * 7 + 3) % len(_INITIALS)]}."
            n += 1
            prof = _sample_profile(rng)
            ability = rng.normal(62 + CLASS_OFFSET[cls], 15)
            slope = rng.normal(1.8, 2.0)
            engagement = rng.normal(0, 1)
            drop = rng.random() < 0.12                      # some learners go quiet recently
            scores, sessions, minutes = [], [], []
            for w in range(WEEKS):
                scores.append(float(np.clip(ability + slope * w + rng.normal(0, 6), 12, 100)))
                lam = float(np.clip(3.2 + 1.2 * engagement, 0.4, 8))
                if drop and w >= WEEKS - 2:
                    lam *= 0.25
                s = int(rng.poisson(lam))
                sessions.append(s)
                minutes.append(round(s * float(np.clip(rng.normal(14, 4), 5, 30)), 0))
                weekly.append({"id": sid, "class_name": cls, "week": w + 1, "score": round(scores[-1], 1),
                               "sessions": s, "minutes": minutes[-1]})
            for sk in SKILLS:
                skill_rows.append({"id": sid, "class_name": cls, "skill": sk, "accuracy": float(np.clip(
                    ability + slope * 3 + SKILL_EFFECT.get(sk, 0) + rng.normal(0, 12), 8, 100))})

            latest = round(float(np.mean(scores[-2:])), 1)
            change = round(float(np.mean(scores[-2:]) - np.mean(scores[:2])), 1)
            recent_drop = round(float(np.mean(scores[-2:]) - np.mean(scores[-4:-2])), 1)
            sess_recent = float(np.mean(sessions[-2:]))
            reasons = []
            if latest < 45:
                reasons.append(f"Latest score is low ({latest:.0f}%).")
            if recent_drop <= -8:
                reasons.append(f"Score fell {abs(recent_drop):.0f} points in the last 2 weeks.")
            if sess_recent < 1.5:
                reasons.append("Fewer than 2 sessions a week recently.")
            if len(reasons) >= 1 and (latest < 45 or recent_drop <= -8 or sess_recent < 1.5):
                status = "Needs attention"
            elif latest < 60 or recent_drop <= -4:
                status = "Watch"
                reasons.append("Score is below 60% or slipping." if latest < 60 else "Score is slipping.")
            else:
                status = "On track"
                reasons.append("Steady progress.")
            quiz_n = int(rng.integers(2, 9))
            profile_in = {**prof, "quiz_score": latest, "attempts": min(quiz_n, 3),
                          "time_spent_min": float(np.clip(np.mean(minutes) * 0.6, 5, 35))}
            rec = recommender.recommend(profile_in)
            students.append({
                "id": sid, "name": name, "class_name": cls, **prof,
                "latest_score": latest, "change": change, "recent_change": recent_drop,
                "sessions_wk": round(sess_recent, 1), "minutes_wk": round(float(np.mean(minutes[-2:])), 0),
                "quizzes": quiz_n, "trend": [round(s, 1) for s in scores],
                "suggested_format": rec["top_format"], "second_format": rec["second_format"],
                "support_level": rec["support_level"], "status": status, "reason": " ".join(reasons),
            })
    st_df = pd.DataFrame(students)
    sk_df = pd.DataFrame(skill_rows)
    weakest = sk_df.groupby("id").apply(lambda g: g.loc[g["accuracy"].idxmin(), "skill"],
                                        include_groups=False)
    st_df["weakest_skill"] = st_df["id"].map(weakest)
    return {"students": st_df, "weekly": pd.DataFrame(weekly), "skills": sk_df}


def kpis(students: pd.DataFrame, weekly: pd.DataFrame) -> dict:
    """Headline numbers for the filtered group, each with a recent trend for the sparkline."""
    ids = set(students["id"])
    w = weekly[weekly["id"].isin(ids)]
    by_week = w.groupby("week").agg(score=("score", "mean"), sessions=("sessions", "mean"),
                                    minutes=("minutes", "mean"))
    active = w[w["week"] == WEEKS].groupby("id")["sessions"].sum()
    return {
        "avg_score": float(students["latest_score"].mean()) if len(students) else 0.0,
        "score_trend": by_week["score"].round(1).tolist(),
        "score_delta": float(by_week["score"].iloc[-2:].mean() - by_week["score"].iloc[:2].mean())
        if len(by_week) else 0.0,
        "active_pct": float((active >= 2).mean() * 100) if len(active) else 0.0,
        "sessions_trend": by_week["sessions"].round(2).tolist(),
        "attention": int((students["status"] == "Needs attention").sum()),
        "watch": int((students["status"] == "Watch").sum()),
        "on_track_pct": float((students["status"] == "On track").mean() * 100) if len(students) else 0.0,
        "minutes_wk": float(students["minutes_wk"].mean()) if len(students) else 0.0,
        "minutes_trend": by_week["minutes"].round(1).tolist(),
        "n": len(students),
    }


def insights(students: pd.DataFrame, skills: pd.DataFrame) -> list[str]:
    """Plain-language things a teacher can act on this week."""
    out = []
    if not len(students):
        return ["No students match the current filters."]
    n_att = int((students["status"] == "Needs attention").sum())
    if n_att:
        out.append(f"**{n_att} {'student needs' if n_att == 1 else 'students need'} attention.** "
                   "Open the Students tab to see why and to set a teacher override.")
    sk = skills[skills["id"].isin(students["id"])]
    if len(sk):
        low = sk.groupby("skill")["accuracy"].apply(lambda s: (s < 60).mean() * 100).sort_values(ascending=False)
        out.append(f"**{low.index[0]}** is the weakest skill: {low.iloc[0]:.0f}% of students are below 60%. "
                   "A small-group session could help.")
    top = students["suggested_format"].value_counts()
    out.append(f"**{top.index[0]}** is the most suggested format ({top.iloc[0] / len(students) * 100:.0f}% of "
               "students). Plan at least one lesson in the other formats too.")
    quiet = int((students["sessions_wk"] < 1.5).sum())
    if quiet:
        out.append(f"**{quiet} {'student has' if quiet == 1 else 'students have'}** done fewer than 2 sessions "
                   "a week recently. A short check-in may re-engage them.")
    return out
