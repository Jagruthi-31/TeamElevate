"""PDF reports (student progress report and class report) built with reportlab + matplotlib."""
import io
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

INK, BRAND, MUTED, LINE = "#15173D", "#3A3FD8", "#555A80", "#D9DCEF"
TEAL, OCHRE, PAPER = "#0A7C74", "#A85A00", "#F4F5FB"


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=24,
                                textColor=colors.HexColor(INK), alignment=0, spaceAfter=2, leading=28),
        "sub": ParagraphStyle("s", parent=ss["Normal"], fontSize=10.5, textColor=colors.HexColor(MUTED),
                              spaceAfter=10),
        "h2": ParagraphStyle("h", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13.5,
                             textColor=colors.HexColor(INK), spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("b", parent=ss["Normal"], fontSize=10, leading=14.5,
                               textColor=colors.HexColor(INK)),
        "small": ParagraphStyle("sm", parent=ss["Normal"], fontSize=8, leading=11,
                                textColor=colors.HexColor(MUTED)),
    }


def _plain(text: str) -> str:
    return text.replace("**", "")


def _table(rows, col_widths, header=True):
    t = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [("FONTSIZE", (0, 0), (-1, -1), 9), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(INK)),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor(LINE))]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(PAPER)),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def _kpi_row(items):
    """A row of big-number tiles: [(label, value), ...]."""
    s = _styles()
    cells = [[Paragraph(f'<font size="18" color="{BRAND}"><b>{v}</b></font><br/>'
                        f'<font size="8" color="{MUTED}">{l}</font>', s["body"]) for l, v in items]]
    w = (A4[0] - 40 * mm) / len(items)
    t = Table(cells, colWidths=[w] * len(items))
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(LINE)),
                           ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor(LINE)),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                           ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10)]))
    return t


def _fig_image(fig, width_mm=170, height_mm=62):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight", transparent=False, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_mm * mm, height=height_mm * mm)


def _style_ax(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=LINE, linewidth=0.6)
    ax.set_axisbelow(True)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.drawString(20 * mm, 10 * mm, "LearnAble AI. Suggests learning adaptations; never diagnoses or labels a student.")
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _build(story) -> bytes:
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                      bottomMargin=18 * mm, title="LearnAble AI report", author="LearnAble AI").build(
        story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


# ------------------------------------------------------------------ student report
def student_report_pdf(name: str, history: list[dict], rec: dict, skills: pd.DataFrame,
                       steps: list[str], plan: pd.DataFrame, level: int, xp: int) -> bytes:
    s = _styles()
    scores = [r["score_pct"] for r in history]
    story = [Paragraph("Learning progress report", s["title"]),
             Paragraph(f"{name or 'Student'} &nbsp;|&nbsp; Topic: Fractions &nbsp;|&nbsp; {date.today():%d %b %Y}", s["sub"]),
             _kpi_row([("Quizzes taken", str(len(history))), ("Latest score", f"{scores[-1]:.0f}%"),
                       ("Best score", f"{max(scores):.0f}%"), ("Level", f"{level} ({xp} XP)")])]

    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.plot(range(1, len(scores) + 1), scores, color=BRAND, linewidth=2.4, marker="o", markersize=6)
    ax.set_ylim(0, 105)
    ax.set_xticks(range(1, len(scores) + 1))
    ax.set_xlabel("Quiz number", fontsize=8, color=MUTED)
    ax.set_ylabel("Score (%)", fontsize=8, color=MUTED)
    _style_ax(ax)
    story += [Paragraph("Score over time", s["h2"]), _fig_image(fig)]

    story += [Paragraph("Accuracy by skill", s["h2"])]
    rows = [["Skill", "Accuracy", "Questions", "Status"]] + [
        [r.skill, f"{r.accuracy:.0f}%", str(int(r.answered)),
         "Needs attention" if r.accuracy < 60 else "On track"] for r in skills.itertuples()]
    story.append(_table(rows, [70 * mm, 28 * mm, 28 * mm, 44 * mm]))

    story += [Paragraph("Recommended learning format", s["h2"]),
              Paragraph(f"<b>{rec['top_format']}</b>" + (f", with <b>{rec['second_format']}</b> as a good second option."
                                                         if rec["second_format"] else "."), s["body"]),
              Spacer(1, 4)]
    for r in rec["reasons"]:
        story.append(Paragraph("&bull; " + _plain(r), s["body"]))

    story.append(Paragraph("Next steps", s["h2"]))
    for t in steps:
        story.append(Paragraph("&bull; " + _plain(t), s["body"]))

    story.append(Paragraph("Five-day study plan", s["h2"]))
    story.append(_table([list(plan.columns)] + plan.astype(str).values.tolist(),
                        [18 * mm, 86 * mm, 38 * mm, 28 * mm]))
    return _build(story)


# ------------------------------------------------------------------ class report
def class_report_pdf(scope: str, students: pd.DataFrame, weekly: pd.DataFrame, skills: pd.DataFrame,
                     k: dict, notes: list[str], overrides: dict) -> bytes:
    s = _styles()
    story = [Paragraph("Class learning report", s["title"]),
             Paragraph(f"{scope} &nbsp;|&nbsp; {k['n']} students &nbsp;|&nbsp; {date.today():%d %b %Y}", s["sub"]),
             Paragraph("<b>Simulated demonstration data.</b> The cohort is generated for demonstration and is not "
                       "real student information.", s["small"]), Spacer(1, 8),
             _kpi_row([("Average score", f"{k['avg_score']:.0f}%"), ("On track", f"{k['on_track_pct']:.0f}%"),
                       ("Need attention", str(k["attention"])), ("Active learners", f"{k['active_pct']:.0f}%")])]

    story.append(Paragraph("What to act on this week", s["h2"]))
    for n in notes:
        story.append(Paragraph("&bull; " + _plain(n), s["body"]))

    w = weekly[weekly["id"].isin(students["id"])].groupby(["class_name", "week"])["score"].mean().unstack(0)
    fig, ax = plt.subplots(figsize=(7, 2.6))
    for c, col in zip(w.columns, [BRAND, TEAL, OCHRE, "#B8175F"]):
        ax.plot(w.index, w[c], label=c, color=col, linewidth=2.2)
    ax.set_xlabel("Week", fontsize=8, color=MUTED)
    ax.set_ylabel("Average score (%)", fontsize=8, color=MUTED)
    ax.legend(frameon=False, fontsize=8, ncol=4, loc="lower right")
    _style_ax(ax)
    story += [Paragraph("Average score by week", s["h2"]), _fig_image(fig)]

    sk = skills[skills["id"].isin(students["id"])].groupby("skill")["accuracy"].mean().sort_values()
    fig2, ax2 = plt.subplots(figsize=(7, 2.6))
    ax2.barh(sk.index, sk.values, color=[OCHRE if v < 60 else TEAL for v in sk.values])
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("Average accuracy (%)", fontsize=8, color=MUTED)
    _style_ax(ax2)
    story += [Paragraph("Skill accuracy", s["h2"]), _fig_image(fig2)]

    att = students[students["status"] == "Needs attention"].sort_values("latest_score")
    story.append(Paragraph(f"Students who need attention ({len(att)})", s["h2"]))
    if len(att):
        rows = [["Student", "Class", "Score", "Why", "Suggested format"]]
        for r in att.itertuples():
            fmt = overrides.get(r.id, {}).get("format")
            rows.append([f"{r.name} ({r.id})", r.class_name, f"{r.latest_score:.0f}%",
                         Paragraph(r.reason, s["small"]), (fmt + " (teacher)") if fmt else r.suggested_format])
        story.append(_table(rows, [34 * mm, 20 * mm, 14 * mm, 68 * mm, 34 * mm]))
    else:
        story.append(Paragraph("No students need attention in this group.", s["body"]))
    return _build(story)
