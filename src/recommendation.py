"""Model A: KNN-based learning-format recommender (with explanations + feedback loop).

The model finds learners with similar preferences/performance and recommends the
format that worked well for them. It recommends learning *adaptations*; it never
labels or diagnoses a student.
"""
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import (
    FEATURES, FEATURE_LABELS, FEEDBACK_CSV, FORMATS, MODEL_DIR, MODEL_PATH,
    TARGET, SPEED_LABELS,
)
from .data_processing import load_training_data

PARAM_GRID = {
    "knn__n_neighbors": [5, 9, 15, 21],
    "knn__metric": ["euclidean", "cosine"],
}


def build_pipeline(k: int = 15, metric: str = "euclidean") -> Pipeline:
    return Pipeline([
        ("scale", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=k, metric=metric, weights="distance")),
    ])


def clean_profile(profile: dict) -> dict:
    """Validate + clamp a profile so bad/missing inputs never crash the model."""
    ranges = {
        "pref_text": (1, 5), "pref_audio": (1, 5), "pref_visual": (1, 5),
        "reading_speed": (1, 3), "pace": (1, 3), "complexity_pref": (1, 3),
        "quiz_score": (0, 100), "attempts": (1, 10), "time_spent_min": (1, 120),
    }
    defaults = {
        "pref_text": 3, "pref_audio": 3, "pref_visual": 3, "reading_speed": 2,
        "pace": 2, "complexity_pref": 2, "quiz_score": 50, "attempts": 1,
        "time_spent_min": 10,
    }
    out = {}
    for f in FEATURES:
        try:
            v = float(profile.get(f, defaults[f]))
            if np.isnan(v):
                raise ValueError
        except (TypeError, ValueError):
            v = defaults[f]
        lo, hi = ranges[f]
        out[f] = min(max(v, lo), hi)
    return out


def support_level(profile: dict) -> str:
    """Transparent rule: how much extra practice/support to build in."""
    p = clean_profile(profile)
    if p["quiz_score"] < 40 or p["attempts"] >= 4:
        return "high"
    if p["quiz_score"] <= 70 or p["attempts"] >= 3:
        return "moderate"
    return "light"


SUPPORT_ADAPTATIONS = {
    "high": [
        "Break the topic into small sections, one idea at a time",
        "Show worked examples before asking questions",
        "Start practice with easier questions and show explanations after each answer",
        "No time limits. Take as long as you need",
    ],
    "moderate": [
        "Keep the same difficulty and add extra practice questions",
        "Revisit the topics marked 'needs attention' in your progress page",
        "Use a second format (for example diagrams plus text) to reinforce ideas",
    ],
    "light": [
        "Move to harder questions to keep the challenge up",
        "Try the 'standard' explanation for more detail",
        "Use quizzes to check understanding, then move to the next topic",
    ],
}


class Recommender:
    def __init__(self):
        self.pipeline: Pipeline | None = None
        self.train_df: pd.DataFrame | None = None
        self.best_params: dict = {}
        self.cv_accuracy: float | None = None

    # ---------- training ----------
    def fit(self, df: pd.DataFrame | None = None, tune: bool = True) -> "Recommender":
        df = load_training_data() if df is None else df
        X, y = df[FEATURES], df[TARGET]
        if tune and len(df) >= 100:
            cv = StratifiedKFold(5, shuffle=True, random_state=42)
            gs = GridSearchCV(build_pipeline(), PARAM_GRID, cv=cv, scoring="accuracy")
            gs.fit(X, y)
            self.pipeline = gs.best_estimator_
            self.best_params = {k.split("__")[1]: v for k, v in gs.best_params_.items()}
            self.cv_accuracy = float(gs.best_score_)
        else:
            self.pipeline = build_pipeline().fit(X, y)
            self.best_params = {"n_neighbors": 15, "metric": "euclidean"}
        self.train_df = df.reset_index(drop=True)
        return self

    def refit_fast(self) -> "Recommender":
        """Re-train with the best known settings (used after new feedback)."""
        df = load_training_data()
        knn = self.best_params or {"n_neighbors": 15, "metric": "euclidean"}
        k = min(int(knn["n_neighbors"]), len(df))
        self.pipeline = build_pipeline(k, knn["metric"]).fit(df[FEATURES], df[TARGET])
        self.train_df = df.reset_index(drop=True)
        return self

    def save(self, path=MODEL_PATH):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path=MODEL_PATH) -> "Recommender":
        return joblib.load(path)

    # ---------- inference ----------
    def recommend(self, profile: dict, n_neighbors_shown: int = 5) -> dict:
        p = clean_profile(profile)
        x = pd.DataFrame([p])[FEATURES]
        t0 = time.perf_counter()
        proba = self.pipeline.predict_proba(x)[0]
        classes = list(self.pipeline.classes_)
        ranking = sorted(zip(classes, proba), key=lambda t: -t[1])

        # Explainability: who are the nearest "similar learners"?
        scaler, knn = self.pipeline.named_steps["scale"], self.pipeline.named_steps["knn"]
        k = knn.n_neighbors
        dist, idx = knn.kneighbors(scaler.transform(x), n_neighbors=k)
        neighbours = self.train_df.iloc[idx[0]].copy()
        neighbours["distance"] = dist[0]
        votes = neighbours[TARGET].value_counts()
        elapsed_ms = (time.perf_counter() - t0) * 1000

        top = ranking[0][0]
        top_votes = int(votes.get(top, 0))
        level = support_level(p)
        return {
            "top_format": top,
            "ranking": ranking,                      # [(format, probability)]
            "second_format": ranking[1][0] if ranking[1][1] > 0.25 else None,
            "similar_learners": k,
            "similar_votes": {f: int(votes.get(f, 0)) for f in FORMATS},
            "reasons": self._reasons(p, top, top_votes, k),
            "support_level": level,
            "adaptations": SUPPORT_ADAPTATIONS[level],
            "neighbour_table": neighbours.head(n_neighbors_shown)[
                FEATURES + [TARGET, "distance"]],
            "response_ms": elapsed_ms,
        }

    @staticmethod
    def _reasons(p: dict, top: str, top_votes: int, k: int) -> list[str]:
        reasons = [
            f"Of the {k} most similar learners in the data, {top_votes} did well "
            f"with **{top}**."
        ]
        prefs = {"Text explanation": p["pref_text"], "Audio explanation": p["pref_audio"],
                 "Visual diagrams": p["pref_visual"]}
        if top in prefs and prefs[top] >= 4:
            reasons.append(f"You said you like this style ({int(prefs[top])}/5).")
        if top == "Audio explanation" and p["reading_speed"] == 1:
            reasons.append("Listening can take pressure off reading when reading feels slow.")
        if top == "Text explanation" and p["complexity_pref"] == 1:
            reasons.append("Simplified wording will be used because you prefer simple explanations.")
        if top == "Step-by-step":
            reasons.append("Learners with a similar score and attempts count did well "
                           "when ideas were split into small steps.")
        if p["quiz_score"] < 45:
            reasons.append(f"Your latest quiz score ({p['quiz_score']:.0f}%) suggests extra "
                           "practice would help.")
        if p["pace"] == 1:
            reasons.append("You chose a slower pace, so no timers are used.")
        return reasons


# ---------- feedback loop ----------
def add_feedback(profile: dict, format_used: str, rating: int,
                 score_gain: float | None = None) -> None:
    """Store one piece of student feedback (features only, no name)."""
    p = clean_profile(profile)
    row = {**p, TARGET: format_used, "feedback_rating": int(rating),
           "score_gain": score_gain if score_gain is not None else (12 if rating >= 4 else 0),
           "source": "user_feedback"}
    FEEDBACK_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(
        FEEDBACK_CSV, mode="a", header=not FEEDBACK_CSV.exists(), index=False)


def train_and_save() -> Recommender:
    rec = Recommender().fit()
    rec.save()
    return rec


if __name__ == "__main__":
    rec = train_and_save()
    print("Best params:", rec.best_params, "| CV accuracy:", round(rec.cv_accuracy, 3))
    demo = {"pref_text": 2, "pref_audio": 2, "pref_visual": 5, "reading_speed": 2,
            "pace": 2, "complexity_pref": 1, "quiz_score": 55, "attempts": 2,
            "time_spent_min": 15}
    out = rec.recommend(demo)
    print("Recommended:", out["top_format"], [(f, round(p, 2)) for f, p in out["ranking"]])
