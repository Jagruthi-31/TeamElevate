"""Evaluate the recommender. Run:  python -m src.evaluate

All numbers are measured on SIMULATED data. They show the model learns the
patterns in that data; they do NOT prove real-world educational effectiveness.
"""
import json
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay, accuracy_score, classification_report, f1_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

from .config import ASSETS_DIR, EVAL_JSON, FEATURES, FORMATS, TARGET
from .data_processing import ensure_dataset, preprocess
from .recommendation import PARAM_GRID, Recommender, build_pipeline, clean_profile

# Documented expected recommendations, written BEFORE running the model, from the
# assumptions listed in data_processing._format_scores.
PERSONAS = [
    ("Visual learner", dict(pref_text=2, pref_audio=2, pref_visual=5, reading_speed=2, pace=2,
                            complexity_pref=1, quiz_score=60, attempts=2, time_spent_min=15),
     "Visual diagrams"),
    ("Audio-first, slower reader", dict(pref_text=1, pref_audio=5, pref_visual=2, reading_speed=1,
                                        pace=1, complexity_pref=1, quiz_score=60, attempts=2,
                                        time_spent_min=18), "Audio explanation"),
    ("Needs small steps", dict(pref_text=3, pref_audio=3, pref_visual=3, reading_speed=2, pace=1,
                               complexity_pref=1, quiz_score=30, attempts=4, time_spent_min=28),
     "Step-by-step"),
    ("Confident reader", dict(pref_text=5, pref_audio=1, pref_visual=2, reading_speed=3, pace=3,
                              complexity_pref=3, quiz_score=85, attempts=1, time_spent_min=10),
     "Text explanation"),
    ("Fast visual learner", dict(pref_text=3, pref_audio=1, pref_visual=5, reading_speed=3, pace=3,
                                 complexity_pref=2, quiz_score=80, attempts=1, time_spent_min=9),
     "Visual diagrams"),
]


def main() -> dict:
    df = preprocess(ensure_dataset())
    X, y = df[FEATURES], df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    gs = GridSearchCV(build_pipeline(), PARAM_GRID, cv=cv, scoring="accuracy").fit(X_tr, y_tr)
    model = gs.best_estimator_
    pred = model.predict(X_te)

    proba = model.predict_proba(X_te)
    classes = list(model.classes_)
    top2 = np.mean([y_te.iloc[i] in [classes[j] for j in np.argsort(-proba[i])[:2]]
                    for i in range(len(y_te))])
    baseline = y_tr.value_counts(normalize=True).iloc[0]
    # fair comparison: majority class applied to the test set
    majority = y_tr.value_counts().idxmax()
    baseline_acc = accuracy_score(y_te, [majority] * len(y_te))

    # Persona agreement using the model trained on the full cleaned data
    rec = Recommender().fit(df)
    persona_rows = []
    for name, prof, expected in PERSONAS:
        out = rec.recommend(clean_profile(prof))
        persona_rows.append({"persona": name, "expected": expected, "recommended": out["top_format"],
                             "agree": out["top_format"] == expected})
    agreement = float(np.mean([r["agree"] for r in persona_rows]))

    # Response time
    times = []
    for _ in range(200):
        t0 = time.perf_counter()
        rec.recommend(PERSONAS[0][1])
        times.append((time.perf_counter() - t0) * 1000)

    # Confusion matrix figure
    ASSETS_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ConfusionMatrixDisplay.from_predictions(y_te, pred, labels=FORMATS, ax=ax,
                                            xticks_rotation=30, cmap="Blues", colorbar=False)
    ax.set_title("Recommender: held-out test set (simulated data)")
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    results = {
        "n_training_examples": int(len(df)),
        "n_test_examples": int(len(y_te)),
        "best_params": {k.split("__")[1]: v for k, v in gs.best_params_.items()},
        "cv_accuracy_train": round(float(gs.best_score_), 3),
        "test_accuracy": round(float(accuracy_score(y_te, pred)), 3),
        "test_macro_f1": round(float(f1_score(y_te, pred, average="macro")), 3),
        "test_top2_accuracy": round(float(top2), 3),
        "majority_class_baseline_accuracy": round(float(baseline_acc), 3),
        "random_baseline_accuracy": 0.25,
        "persona_agreement": round(agreement, 2),
        "personas": persona_rows,
        "mean_response_ms": round(float(np.mean(times)), 2),
        "p95_response_ms": round(float(np.percentile(times, 95)), 2),
        "per_class_report": classification_report(y_te, pred, output_dict=True, zero_division=0),
    }
    EVAL_JSON.parent.mkdir(exist_ok=True)
    EVAL_JSON.write_text(json.dumps(results, indent=2, default=float))
    return results


if __name__ == "__main__":
    r = main()
    show = {k: v for k, v in r.items() if k not in ("personas", "per_class_report")}
    print(json.dumps(show, indent=2))
    print(pd.DataFrame(r["personas"]).to_string(index=False))
