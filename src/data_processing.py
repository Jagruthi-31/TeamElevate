"""Simulated learner-interaction dataset + preprocessing.

IMPORTANT: this data is SIMULATED for demonstration. It is generated from
documented rules plus noise (see `generate_simulated_data`). It does not
describe real students and cannot show real-world educational effectiveness.
"""
import numpy as np
import pandas as pd

from .config import (
    DATA_DIR, FEEDBACK_CSV, FEATURES, FORMATS, GOOD_GAIN, GOOD_RATING,
    SIMULATED_CSV, TARGET,
)

# Probability of each learner archetype in the simulation
_ARCHETYPES = ["visual", "audio", "text", "struggling"]
_ARCH_P = [0.30, 0.25, 0.25, 0.20]


def _format_scores(df: pd.DataFrame) -> np.ndarray:
    """Latent 'how suitable is each format' score used ONLY to simulate outcomes.

    Documented assumptions (not educational findings):
    - Text suits learners who like reading, read faster, or want simple wording.
    - Audio suits learners who like listening, and slower readers.
    - Visuals suit learners who like diagrams and those scoring lower.
    - Step-by-step suits learners with low scores, many attempts, slower pace.
    """
    text = df.pref_text + 0.5 * (df.reading_speed - 2) + 0.3 * (3 - df.complexity_pref)
    audio = df.pref_audio + 0.5 * (2 - df.reading_speed)
    visual = df.pref_visual + 0.3 * (df.quiz_score < 50)
    steps = (1.6 + 0.5 * (df.attempts - 1) + 1.2 * (df.quiz_score < 45)
             + 0.5 * (df.pace == 1))
    return np.column_stack([text, audio, visual, steps])


def generate_simulated_data(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Create `n` simulated learner interactions (one learner, one format tried)."""
    rng = np.random.default_rng(seed)
    arch = rng.choice(_ARCHETYPES, size=n, p=_ARCH_P)

    def pref(high_mask):
        base = np.where(high_mask, rng.normal(4.3, 0.7, n), rng.normal(2.6, 0.9, n))
        return np.clip(np.rint(base), 1, 5).astype(int)

    df = pd.DataFrame({
        "pref_text": pref(arch == "text"),
        "pref_audio": pref(arch == "audio"),
        "pref_visual": pref(arch == "visual"),
    })
    df["reading_speed"] = np.where(
        arch == "audio", rng.choice([1, 2], n, p=[0.6, 0.4]),
        np.where(arch == "text", rng.choice([2, 3], n, p=[0.4, 0.6]),
                 rng.choice([1, 2, 3], n, p=[0.3, 0.45, 0.25])))
    df["pace"] = np.where(
        arch == "struggling", rng.choice([1, 2], n, p=[0.65, 0.35]),
        rng.choice([1, 2, 3], n, p=[0.2, 0.55, 0.25]))
    df["complexity_pref"] = rng.choice([1, 2, 3], n, p=[0.3, 0.45, 0.25])
    quiz = np.where(arch == "struggling", rng.normal(36, 10, n), rng.normal(66, 15, n))
    df["quiz_score"] = np.clip(np.rint(quiz), 5, 100)
    df["attempts"] = np.where(
        arch == "struggling", rng.integers(3, 6, n), rng.integers(1, 4, n))
    df["time_spent_min"] = np.clip(
        np.rint(rng.normal(14, 5, n) + 3 * (df["attempts"] - 1)), 4, 45)

    # Each simulated learner tried one format at random
    used_idx = rng.integers(0, len(FORMATS), n)
    scores = _format_scores(df) + rng.normal(0, 0.45, (n, len(FORMATS)))
    best = scores.max(axis=1)
    used_score = scores[np.arange(n), used_idx]
    gap = best - used_score
    p_good = np.clip(0.9 - 0.5 * gap, 0.03, 0.9)
    good = rng.random(n) < p_good

    df["format_used"] = [FORMATS[i] for i in used_idx]
    df["feedback_rating"] = np.where(
        good, rng.choice([4, 5], n, p=[0.45, 0.55]), rng.choice([1, 2, 3], n))
    df["score_gain"] = np.rint(np.where(
        good, rng.normal(18, 6, n), rng.normal(3, 8, n))).astype(int)
    df["completion_pct"] = np.clip(
        np.rint(np.where(good, rng.normal(92, 6, n), rng.normal(65, 20, n))), 10, 100)
    df["source"] = "simulated"
    return df


def ensure_dataset() -> pd.DataFrame:
    """Load the simulated CSV, generating it first if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SIMULATED_CSV.exists():
        generate_simulated_data().to_csv(SIMULATED_CSV, index=False)
    return pd.read_csv(SIMULATED_CSV)


def load_feedback() -> pd.DataFrame:
    if FEEDBACK_CSV.exists():
        try:
            return pd.read_csv(FEEDBACK_CSV)
        except pd.errors.EmptyDataError:
            pass
    return pd.DataFrame(columns=FEATURES + [TARGET, "feedback_rating", "score_gain", "source"])


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and keep only interactions that 'worked well'.

    The recommender learns: for learners like this, which format worked well?
    """
    df = df.copy()
    needed = FEATURES + [TARGET, "feedback_rating"]
    df = df.dropna(subset=needed)
    df = df[df[TARGET].isin(FORMATS)]
    df["quiz_score"] = df["quiz_score"].clip(0, 100)
    if "score_gain" not in df.columns:
        df["score_gain"] = GOOD_GAIN  # feedback rows: rating is the signal
    df["score_gain"] = df["score_gain"].fillna(GOOD_GAIN)
    good = (df["feedback_rating"] >= GOOD_RATING) & (df["score_gain"] >= GOOD_GAIN)
    return df[good].reset_index(drop=True)


def load_training_data(include_feedback: bool = True) -> pd.DataFrame:
    df = ensure_dataset()
    if include_feedback:
        fb = load_feedback()
        if len(fb):
            df = pd.concat([df, fb], ignore_index=True)
    return preprocess(df)


if __name__ == "__main__":
    data = generate_simulated_data()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(SIMULATED_CSV, index=False)
    print(f"Saved {len(data)} simulated interactions to {SIMULATED_CSV}")
    print(preprocess(data)[TARGET].value_counts())
