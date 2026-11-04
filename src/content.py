"""Lesson content: one topic (Fractions), every section written in several formats.

The recommender chooses WHICH version is shown; the text itself is pre-written.
"""
import math

# Each section has: standard, simplified, audio (script), steps (list), visual spec + caption
SECTIONS = [
    dict(
        id="s1", title="What is a fraction?",
        standard=("A fraction represents a part of a whole. It is written with two numbers "
                  "separated by a line: the numerator on top and the denominator on the bottom. "
                  "Together they describe how many equal parts of a whole are being considered."),
        simplified=("Imagine a pizza cut into 4 equal pieces. If you eat 1 piece, you ate "
                    "1/4 of the pizza. A fraction tells us how much of something we have."),
        audio=("Imagine a pizza cut into four equal pieces. If you eat one piece, you have eaten "
               "one quarter of the pizza. A fraction tells us how much of something we have. "
               "We write one quarter as one, over four."),
        steps=["Picture one whole thing, like a pizza.",
               "Cut it into equal pieces. Say it is 4 pieces.",
               "Pick the pieces you are talking about. Say you eat 1 piece.",
               "Write it as 1/4: 1 piece out of 4 equal pieces."],
        visual=[("pie", 1, 4), ("pie", 3, 4)],
        caption="Left: 1 of 4 equal parts is shaded (1/4). Right: 3 of 4 equal parts are shaded (3/4).",
    ),
    dict(
        id="s2", title="Numerator and denominator",
        standard=("The denominator (bottom number) states into how many equal parts the whole is "
                  "divided. The numerator (top number) states how many of those parts are counted. "
                  "In 3/8, the whole is divided into 8 equal parts and 3 of them are counted."),
        simplified=("Every fraction has a top number and a bottom number. The bottom number says "
                    "how many equal pieces there are in total. The top number says how many "
                    "pieces we have. In 3/8: 8 pieces in total, we have 3."),
        audio=("Every fraction has a top number and a bottom number. The bottom number, called the "
               "denominator, says how many equal pieces there are in total. The top number, called "
               "the numerator, says how many pieces we have. In three eighths, there are eight "
               "pieces in total, and we have three."),
        steps=["Look at the bottom number. This is the denominator: total equal pieces.",
               "Look at the top number. This is the numerator: pieces we have.",
               "Read 3/8 as 'three out of eight equal pieces'."],
        visual=[("pie", 3, 8)],
        caption="3/8: the circle has 8 equal parts (denominator) and 3 are shaded (numerator).",
    ),
    dict(
        id="s3", title="Equivalent fractions",
        standard=("Equivalent fractions are different fractions that represent the same amount. "
                  "They are found by multiplying or dividing the numerator and denominator by the "
                  "same non-zero number. For example, 1/2 = 2/4 = 4/8."),
        simplified=("Sometimes different fractions mean the same amount. Half a pizza is 1/2. "
                    "If you cut the pizza into 4 pieces, half is 2/4. It is the same amount "
                    "of pizza, just cut differently."),
        audio=("Sometimes different fractions mean the same amount. Half a pizza is one half. "
               "If you cut the same pizza into four pieces, half of it is two quarters. "
               "One half, two quarters, and four eighths are all the same amount."),
        steps=["Start with 1/2.",
               "Multiply the top and bottom by 2: 1 x 2 = 2 and 2 x 2 = 4.",
               "Now you have 2/4. It is the same amount as 1/2.",
               "Multiply by 4 instead and you get 4/8. Also the same amount."],
        visual=[("bar", 1, 2), ("bar", 2, 4), ("bar", 4, 8)],
        caption="Three bars of the same length. 1/2, 2/4 and 4/8 shade exactly the same amount.",
    ),
    dict(
        id="s4", title="Comparing and adding fractions",
        standard=("When fractions share a denominator, the one with the larger numerator is "
                  "greater, and they can be added by adding the numerators and keeping the "
                  "denominator. For example, 3/5 > 2/5 and 1/4 + 2/4 = 3/4."),
        simplified=("If the pieces are the same size, count the pieces. 3 fifths is more than "
                    "2 fifths. To add, count all the pieces together: 1 quarter plus 2 quarters "
                    "is 3 quarters."),
        audio=("If the pieces are the same size, just count the pieces. Three fifths is more than "
               "two fifths. To add fractions with the same bottom number, add the top numbers. "
               "One quarter plus two quarters is three quarters."),
        steps=["Check the bottom numbers. Are they the same?",
               "If yes, compare the top numbers: bigger top number means bigger fraction.",
               "To add, add the top numbers: 1 + 2 = 3.",
               "Keep the bottom number the same: the answer is 3/4."],
        visual=[("bar", 3, 5), ("bar", 2, 5), ("bar", 3, 4)],
        caption="3/5 is longer than 2/5. And 1/4 + 2/4 fills 3 of the 4 parts: 3/4.",
    ),
]

SHADE = "#0A7C74"
EMPTY = "#ffffff"
LINE = "#15173D"


def _pie_svg(num: int, den: int, size: int = 150) -> str:
    cx = cy = size / 2
    r = size / 2 - 6
    parts = []
    for i in range(den):
        a0 = -math.pi / 2 + 2 * math.pi * i / den
        a1 = -math.pi / 2 + 2 * math.pi * (i + 1) / den
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if (a1 - a0) > math.pi else 0
        fill = SHADE if i < num else EMPTY
        parts.append(
            f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} Z" '
            f'fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
    if den == 1:
        parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SHADE if num else EMPTY}" '
                 f'stroke="{LINE}" stroke-width="2"/>']
    return (f'<svg role="img" aria-label="Circle with {num} of {den} equal parts shaded" '
            f'width="{size}" height="{size + 28}" viewBox="0 0 {size} {size + 28}" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}'
            f'<text x="{cx}" y="{size + 20}" text-anchor="middle" font-size="20" '
            f'font-family="Bricolage Grotesque, Trebuchet MS, sans-serif" font-weight="bold" fill="{LINE}">{num}/{den}</text></svg>')


def _bar_svg(num: int, den: int, width: int = 300) -> str:
    h, w = 34, width
    cell = (w - 4) / den
    cells = "".join(
        f'<rect x="{2 + i * cell:.1f}" y="2" width="{cell:.1f}" height="{h}" '
        f'fill="{SHADE if i < num else EMPTY}" stroke="{LINE}" stroke-width="2"/>'
        for i in range(den))
    return (f'<svg role="img" aria-label="Bar with {num} of {den} equal parts shaded" '
            f'width="{w}" height="{h + 30}" viewBox="0 0 {w} {h + 30}" '
            f'xmlns="http://www.w3.org/2000/svg">{cells}'
            f'<text x="{w / 2}" y="{h + 22}" text-anchor="middle" font-size="18" '
            f'font-family="Bricolage Grotesque, Trebuchet MS, sans-serif" font-weight="bold" fill="{LINE}">{num}/{den}</text></svg>')


def visual_html(section: dict) -> str:
    """HTML (on a white card, so it stays readable in dark / high-contrast mode)."""
    items = []
    for kind, num, den in section["visual"]:
        items.append(_pie_svg(num, den) if kind == "pie" else _bar_svg(num, den))
    layout = "row" if section["visual"][0][0] == "pie" else "column"
    return (f'<div class="la-diagram" style="display:flex;flex-direction:{layout};gap:24px;'
            f'align-items:center;justify-content:center;flex-wrap:wrap;">{"".join(items)}</div>')


def text_for(section: dict, complexity_pref: int, force_standard: bool = False) -> str:
    """Simplified wording for complexity 1-2, standard wording for 3 (or when forced)."""
    if force_standard or complexity_pref >= 3:
        return section["standard"]
    return section["simplified"]
