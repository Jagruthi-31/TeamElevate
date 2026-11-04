"""Shared constants for LearnAble AI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
ASSETS_DIR = ROOT / "assets"

SIMULATED_CSV = DATA_DIR / "student_data.csv"
FEEDBACK_CSV = DATA_DIR / "feedback.csv"
MODEL_PATH = MODEL_DIR / "recommendation_model.pkl"
EVAL_JSON = MODEL_DIR / "evaluation_results.json"

# Learning formats the system can recommend (this is the ML target)
FORMATS = [
    "Text explanation",
    "Audio explanation",
    "Visual diagrams",
    "Step-by-step",
]

# Model input features (all self-reported or measured in the app)
FEATURES = [
    "pref_text",        # 1-5  how much the student likes reading
    "pref_audio",       # 1-5  how much the student likes listening
    "pref_visual",      # 1-5  how much the student likes diagrams
    "reading_speed",    # 1 slow, 2 medium, 3 fast (self-chosen)
    "pace",             # 1 slower, 2 normal, 3 faster (self-chosen)
    "complexity_pref",  # 1 very simple, 2 moderate, 3 detailed
    "quiz_score",       # 0-100 latest quiz accuracy
    "attempts",         # number of quiz attempts on the topic
    "time_spent_min",   # minutes spent on lesson + quiz
]
TARGET = "format_used"

# A past interaction counts as "worked well" if the learner rated it highly
# and their quiz score improved.
GOOD_RATING = 4
GOOD_GAIN = 10

FEATURE_LABELS = {
    "pref_text": "Likes reading",
    "pref_audio": "Likes listening",
    "pref_visual": "Likes diagrams",
    "reading_speed": "Reading speed",
    "pace": "Learning pace",
    "complexity_pref": "Explanation detail",
    "quiz_score": "Latest quiz score",
    "attempts": "Quiz attempts",
    "time_spent_min": "Time spent (min)",
}

SPEED_LABELS = {1: "Slower", 2: "Medium", 3: "Faster"}
COMPLEXITY_LABELS = {1: "Very simple", 2: "Moderate", 3: "Detailed"}

DEFAULT_PROFILE = {
    "name": "",
    "pref_text": 3,
    "pref_audio": 3,
    "pref_visual": 3,
    "reading_speed": 2,
    "pace": 2,
    "complexity_pref": 2,
    "quiz_score": 50.0,   # neutral prior until a quiz is taken
    "attempts": 1,
    "time_spent_min": 10.0,
}
