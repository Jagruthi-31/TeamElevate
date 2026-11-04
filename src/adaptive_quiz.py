"""Model B: transparent adaptive-difficulty logic + question bank (topic: Fractions)."""
import random

# difficulty: 1 easy, 2 medium, 3 hard
QUESTIONS = [
    # ---------------- easy ----------------
    dict(id="e1", d=1, skill="Reading fractions",
         q="A pizza is cut into 8 equal slices and you eat 3. What fraction did you eat?",
         options=["3/8", "8/3", "5/8", "3/5"], answer=0,
         hint="The top number counts the slices you ate. The bottom number counts all the slices.",
         explain="You ate 3 of the 8 equal slices, so the fraction is 3/8."),
    dict(id="e2", d=1, skill="Parts of a fraction",
         q="In the fraction 3/4, which number is the denominator?",
         options=["3", "4", "7", "1"], answer=1,
         hint="The denominator is the bottom number. It tells how many equal parts the whole has.",
         explain="The denominator is the bottom number, 4. It means the whole is split into 4 equal parts."),
    dict(id="e3", d=1, skill="Reading fractions",
         q="Which fraction means 'one half'?",
         options=["2/1", "1/2", "1/3", "2/2"], answer=1,
         hint="One half means 1 part out of 2 equal parts.",
         explain="One half is 1 part out of 2 equal parts, written 1/2."),
    dict(id="e4", d=1, skill="Reading fractions",
         q="A chocolate bar has 6 equal pieces and 1 piece is left. What fraction is left?",
         options=["6/1", "1/6", "5/6", "1/5"], answer=1,
         hint="How many pieces are left? How many pieces were there in total?",
         explain="1 piece is left out of 6 equal pieces, so 1/6 is left."),
    dict(id="e5", d=1, skill="Parts of a fraction",
         q="In the fraction 5/9, which number is the numerator?",
         options=["9", "4", "5", "14"], answer=2,
         hint="The numerator is the top number. It counts the parts we are talking about.",
         explain="The numerator is the top number, 5. It counts the parts we have."),
    dict(id="e6", d=1, skill="Reading fractions",
         q="A shape is split into 5 equal parts and 2 are shaded. What fraction is shaded?",
         options=["5/2", "3/5", "2/5", "2/3"], answer=2,
         hint="Shaded parts go on top. Total equal parts go on the bottom.",
         explain="2 shaded parts out of 5 equal parts is 2/5."),
    # ---------------- medium ----------------
    dict(id="m1", d=2, skill="Equivalent fractions",
         q="Which fraction is equal to 1/2?",
         options=["2/4", "2/3", "1/4", "3/4"], answer=0,
         hint="Multiply the top and the bottom by the same number.",
         explain="1/2 x 2/2 = 2/4. Multiplying top and bottom by the same number keeps the value the same."),
    dict(id="m2", d=2, skill="Adding & subtracting",
         q="What is 1/4 + 2/4?",
         options=["3/8", "3/4", "2/8", "1/2"], answer=1,
         hint="The bottom numbers are the same, so only add the top numbers.",
         explain="When the denominators match, add the numerators and keep the denominator: 1 + 2 = 3, so 3/4."),
    dict(id="m3", d=2, skill="Comparing fractions",
         q="Which is greater: 3/5 or 2/5?",
         options=["3/5", "2/5", "They are equal", "Cannot tell"], answer=0,
         hint="The parts are the same size (fifths). Which fraction has more of them?",
         explain="Both are fifths. 3 fifths is more than 2 fifths, so 3/5 is greater."),
    dict(id="m4", d=2, skill="Equivalent fractions",
         q="Simplify 6/8.",
         options=["2/3", "3/4", "6/4", "1/2"], answer=1,
         hint="Divide the top and bottom by the same number. Both 6 and 8 can be divided by 2.",
         explain="6 / 2 = 3 and 8 / 2 = 4, so 6/8 simplifies to 3/4."),
    dict(id="m5", d=2, skill="Comparing fractions",
         q="Which fraction is the smallest?",
         options=["1/2", "1/3", "1/4", "2/3"], answer=2,
         hint="With the same top number, a bigger bottom number means smaller pieces.",
         explain="Quarters are smaller pieces than thirds or halves, so 1/4 is the smallest."),
    dict(id="m6", d=2, skill="Adding & subtracting",
         q="What is 5/6 - 1/6?",
         options=["4/6", "4/0", "6/6", "5/12"], answer=0,
         hint="Same denominator: subtract the top numbers and keep the bottom number.",
         explain="5 - 1 = 4, so the answer is 4/6 (which can be simplified to 2/3)."),
    # ---------------- hard ----------------
    dict(id="h1", d=3, skill="Adding & subtracting",
         q="What is 1/2 + 1/3?",
         options=["2/5", "5/6", "2/6", "1/6"], answer=1,
         hint="Find a common denominator first. Both 2 and 3 fit into 6.",
         explain="1/2 = 3/6 and 1/3 = 2/6. Then 3/6 + 2/6 = 5/6."),
    dict(id="h2", d=3, skill="Multiplying & dividing",
         q="What is 2/3 x 3/4?",
         options=["5/7", "1/2", "5/12", "8/9"], answer=1,
         hint="Multiply the tops, multiply the bottoms, then simplify.",
         explain="2 x 3 = 6 and 3 x 4 = 12, so 6/12, which simplifies to 1/2."),
    dict(id="h3", d=3, skill="Equivalent fractions",
         q="Which fraction is equivalent to 15/20?",
         options=["5/6", "3/4", "1/2", "2/3"], answer=1,
         hint="Find a number that divides both 15 and 20.",
         explain="15 and 20 are both divisible by 5: 15/5 = 3 and 20/5 = 4, so 3/4."),
    dict(id="h4", d=3, skill="Mixed numbers",
         q="Write 7/4 as a mixed number.",
         options=["1 1/4", "1 3/4", "2 1/4", "3/4"], answer=1,
         hint="How many whole groups of 4 fit in 7? What is left over?",
         explain="7 = 4 + 3, so there is 1 whole and 3/4 left over: 1 3/4."),
    dict(id="h5", d=3, skill="Multiplying & dividing",
         q="What is 3/4 divided by 1/2?",
         options=["3/8", "2/3", "3/2", "1/4"], answer=2,
         hint="Dividing by a fraction means multiplying by its flip (reciprocal).",
         explain="3/4 / 1/2 = 3/4 x 2/1 = 6/4 = 3/2, which is 1 1/2."),
    dict(id="h6", d=3, skill="Comparing fractions",
         q="Which is the largest: 3/4, 5/8, 7/10 or 2/3?",
         options=["5/8", "7/10", "2/3", "3/4"], answer=3,
         hint="Turn each into a decimal: divide the top by the bottom.",
         explain="3/4 = 0.75, 5/8 = 0.625, 7/10 = 0.70, 2/3 is about 0.67. So 3/4 is largest."),
]

DIFFICULTY_NAMES = {1: "Easier", 2: "Medium", 3: "Challenging"}
QUIZ_LENGTH = 8


def initial_difficulty(prior_score: float) -> int:
    """Start point from the latest known score (50 = neutral default -> medium)."""
    if prior_score < 40:
        return 1
    if prior_score >= 80:
        return 3
    return 2


def next_difficulty(current: int, history: list[bool]) -> tuple[int, str]:
    """Transparent adaptive rule on the last (up to) 3 answers.

    accuracy < 40%   -> easier questions (+ explanations)
    40% - 70%        -> same difficulty (+ practice)
    accuracy > 70%   -> harder questions
    """
    recent = history[-3:]
    if not recent:
        return current, "Starting level"
    acc = sum(recent) / len(recent)
    if acc < 0.40:
        return max(1, current - 1), "Moving to easier questions with extra explanation"
    if acc > 0.70:
        return min(3, current + 1), "Great work. Moving to harder questions"
    return current, "Staying at this level for more practice"


def pick_question(difficulty: int, used_ids: set, rng: random.Random | None = None) -> dict | None:
    """Pick an unused question at the target level (else the nearest level)."""
    rng = rng or random
    for d in sorted({1, 2, 3}, key=lambda x: (abs(x - difficulty), x)):
        pool = [q for q in QUESTIONS if q["d"] == d and q["id"] not in used_ids]
        if pool:
            return rng.choice(pool)
    return None


def shuffled_options(question: dict, rng: random.Random | None = None) -> tuple[list[str], int]:
    """Shuffle answer order so position is not a giveaway; return (options, correct_index)."""
    rng = rng or random
    order = list(range(len(question["options"])))
    rng.shuffle(order)
    options = [question["options"][i] for i in order]
    return options, order.index(question["answer"])
