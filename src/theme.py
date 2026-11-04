"""Visual design for LearnAble AI: design tokens, global CSS and small HTML components.

Design idea: the four learning formats each own one colour AND one icon shape, so meaning
never depends on colour alone. The logo is a circle cut into four parts (a fraction, which
is also the topic of the lesson). All colours are CSS variables so the high-contrast mode
can swap the whole palette in one place.
"""
import html
import re

import streamlit as st

# --------------------------------------------------------------------------- formats
FORMAT_STYLE = {
    "Text explanation": dict(key="text", short="Text", verb="Read it"),
    "Audio explanation": dict(key="audio", short="Audio", verb="Listen to it"),
    "Visual diagrams": dict(key="visual", short="Diagrams", verb="See it"),
    "Step-by-step": dict(key="steps", short="Steps", verb="Do it in small steps"),
}

_GLYPHS = {
    "text": '<path d="M4 6h16M4 12h16M4 18h10"/>',
    "audio": '<path d="M4 10v4M8 6v12M12 3v18M16 7v10M20 10v4"/>',
    "visual": '<circle cx="12" cy="12" r="9"/><path d="M12 3v9h9"/>',
    "steps": '<path d="M3 21h6v-6h6V9h6"/>',
}

JOURNEY = ["Profile", "Recommendation", "Lesson", "Quiz", "Progress"]


def _key(fmt: str) -> str:
    return FORMAT_STYLE.get(fmt, FORMAT_STYLE["Text explanation"])["key"]


def glyph(fmt_or_key: str, size: int = 24) -> str:
    k = FORMAT_STYLE[fmt_or_key]["key"] if fmt_or_key in FORMAT_STYLE else fmt_or_key
    return (f'<svg class="la-glyph" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{_GLYPHS[k]}</svg>')


def md(markup: str) -> None:
    """Render trusted HTML. Collapsed to one line so Markdown never treats it as code."""
    st.markdown(" ".join(line.strip() for line in markup.strip().splitlines()),
                unsafe_allow_html=True)


# --------------------------------------------------------------------------- CSS
_FONT_FACES = """
@font-face{font-family:'Bricolage Grotesque';font-weight:200 800;font-display:swap;
  src:url('app/static/fonts/bricolage-grotesque-latin-wght-normal.woff2') format('woff2');}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:400;font-display:swap;
  src:url('app/static/fonts/atkinson-hyperlegible-latin-400-normal.woff2') format('woff2');}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:700;font-display:swap;
  src:url('app/static/fonts/atkinson-hyperlegible-latin-700-normal.woff2') format('woff2');}
"""

_TOKENS = """
:root{
  --ink:#15173D; --paper:#F4F5FB; --surface:#FFFFFF; --line:#D9DCEF; --muted:#555A80;
  --brand:#3A3FD8; --on-brand:#FFFFFF; --focus:#15173D;
  --f-text:#3A3FD8; --f-audio:#B8175F; --f-visual:#0A7C74; --f-steps:#A85A00; --on-fmt:#FFFFFF;
  --t-text:#E8E9FB; --t-audio:#FBE5EE; --t-visual:#DCF2EF; --t-steps:#FBEBD5;
  --good:#0B7A4B; --good-bg:#E1F4EA; --bad:#B3261E; --bad-bg:#FBE7E5;
  --display:'Bricolage Grotesque','Trebuchet MS','Segoe UI',system-ui,sans-serif;
  --r-lg:20px; --r-md:14px; --r-sm:10px;
}
"""

_BASE = """
.stApp{background:var(--paper);color:var(--ink);}
[data-testid="stMainBlockContainer"]{max-width:1120px;padding-top:2.2rem;padding-bottom:5rem;}
[data-testid="stHeader"]{background:transparent;}

/* ---- type ---- */
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.la-display{font-family:var(--display);color:var(--ink);
  letter-spacing:-0.02em;line-height:1.1;}
.stApp h2{font-size:1.9rem;font-weight:700;margin-top:2.6rem;}
.stApp h3{font-size:1.4rem;font-weight:700;}
.stApp h4{font-size:1.15rem;font-weight:700;}
.stApp p,.stApp li{line-height:1.6;}
[data-testid="stCaptionContainer"]{color:var(--muted);}
.stApp a{color:var(--brand);}

/* ---- keyboard focus: always visible ---- */
.stApp *:focus-visible{outline:3px solid var(--focus)!important;outline-offset:3px!important;
  border-radius:6px;}

/* ---- sidebar ---- */
[data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--line);}
[data-testid="stSidebarHeader"]{align-items:center;justify-content:flex-start;gap:.6rem;padding-bottom:.4rem;}
[data-testid="stSidebarHeader"]>div:first-child{order:0;}
[data-testid="stSidebarHeader"]::after{content:"LearnAble AI";order:1;font-family:var(--display);
  font-weight:800;font-size:1.3rem;letter-spacing:-0.02em;color:var(--ink);}
[data-testid="stSidebarCollapseButton"]{order:2;margin-left:auto;}
[data-testid="stSidebarLogo"]{height:2rem;}
[data-testid="stSidebarNav"] a{border-radius:var(--r-sm);padding:.45rem .7rem;}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:var(--t-text);font-weight:700;}
[data-testid="stSidebarNav"] a[aria-current="page"] span{color:var(--brand);}
[data-testid="stSidebar"] h3{font-size:1.05rem;margin-bottom:.4rem;}
.la-side-note{font-size:.82rem;color:var(--muted);line-height:1.5;}

/* ---- journey bar (a real sequence) ---- */
.la-journey ol{list-style:none;display:flex;gap:.35rem;margin:0 0 1.6rem;padding:0;flex-wrap:wrap;}
.la-journey li{display:flex;align-items:center;gap:.5rem;padding:.28rem .8rem .28rem .3rem;
  border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--muted);
  font-size:.85rem;font-weight:600;}
.la-journey .n{display:grid;place-items:center;width:1.45rem;height:1.45rem;border-radius:50%;
  background:var(--paper);border:1px solid var(--line);font-size:.75rem;font-weight:700;}
.la-journey li.is-current{background:var(--brand);border-color:var(--brand);color:var(--on-brand);}
.la-journey li.is-current .n{background:var(--on-brand);color:var(--brand);border-color:var(--on-brand);}
@media (max-width:700px){.la-journey li:not(.is-current) .t{display:none;}}

/* ---- page header ---- */
.la-head h1{font-size:clamp(2.1rem,4.6vw,3.2rem);font-weight:800;margin:0 0 .6rem;padding:0;}
.la-head .lede{font-size:1.15rem;color:var(--muted);max-width:44rem;margin:0 0 1.4rem;line-height:1.55;}

/* ---- bordered containers become the card surface ---- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]){}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line)!important;
  background:var(--surface);border-radius:var(--r-lg)!important;padding:.55rem .6rem .7rem;}
[data-testid="stForm"]{background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r-lg);padding:1.6rem;}

/* ---- buttons ---- */
.stButton>button,[data-testid="stFormSubmitButton"]>button,.stDownloadButton>button{
  border-radius:var(--r-md);font-weight:700;padding:.6rem 1.3rem;border:1.5px solid var(--line);
  background:var(--surface);color:var(--ink);min-height:2.9rem;transition:background .15s,border-color .15s;}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--brand);color:var(--brand);}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primary"],
button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--brand);color:var(--on-brand);border-color:var(--brand);}
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:var(--ink);border-color:var(--ink);color:#fff;}
button[data-testid="stBaseButton-primary"] p,button[data-testid="stBaseButton-primaryFormSubmit"] p{color:inherit;}

/* ---- page links ---- */
[data-testid="stPageLink-NavLink"]{border-radius:var(--r-md);font-weight:700;padding:.55rem .9rem;
  border:1.5px solid var(--line);background:var(--surface);text-decoration:none;
  transition:border-color .15s;width:fit-content;}
[data-testid="stPageLink-NavLink"]:hover{border-color:var(--brand);}
[data-testid="stPageLink-NavLink"] p{color:var(--brand);}
.st-key-cta [data-testid="stPageLink-NavLink"]{background:var(--brand);border-color:var(--brand);
  padding:.85rem 1.5rem;font-size:1.05rem;}
.st-key-cta [data-testid="stPageLink-NavLink"] p,.st-key-cta [data-testid="stPageLink-NavLink"] span{
  color:var(--on-brand);}
.st-key-cta [data-testid="stPageLink-NavLink"]:hover{background:var(--ink);border-color:var(--ink);}

/* ---- inputs ---- */
[data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="base-input"],textarea{
  border-radius:var(--r-sm)!important;background:var(--paper)!important;border:1.5px solid var(--line)!important;}
[data-baseweb="input"]:focus-within>div{border-color:var(--brand)!important;}
[data-testid="stTextInputRootElement"],[data-testid="stNumberInputContainer"],[data-testid="stTextAreaRootElement"]{
  background:var(--paper)!important;border:1.5px solid var(--line)!important;border-radius:var(--r-sm)!important;}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stTextAreaRootElement"]:focus-within{
  border-color:var(--brand)!important;}
[data-testid="stTextInputRootElement"] input{background:transparent!important;}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]{box-shadow:0 0 0 4px var(--t-text);}

/* ---- radios: pills when horizontal, option cards when stacked (old and new Streamlit markup) ---- */
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]){border:1.5px solid var(--line);
  background:var(--surface);border-radius:var(--r-md);padding:.7rem 1rem;margin:0 .5rem .5rem 0;
  transition:border-color .15s,background .15s;cursor:pointer;}
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]):hover{border-color:var(--brand);}
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]):has(input:checked){
  border-color:var(--brand);background:var(--t-text);box-shadow:inset 0 0 0 1px var(--brand);}
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]) p{font-weight:600;}
[data-testid="stRadioGroup"][aria-orientation="vertical"]>div,
[data-testid="stRadio"] [role="radiogroup"][aria-orientation="vertical"]>label{width:100%;}
[data-testid="stRadioGroup"][aria-orientation="vertical"] label[data-testid="stRadioOption"]{
  width:100%;margin-right:0;}
[data-testid="stRadio"] [role="radiogroup"][aria-orientation="vertical"] label[data-baseweb="radio"]{
  width:100%;margin-right:0;}

[data-testid="stElementContainer"]:has(>[data-testid="stRadio"]),[data-testid="stRadio"]{width:100%!important;}

/* ---- metrics ---- */
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r-lg);padding:1.1rem 1.3rem;}
[data-testid="stMetricValue"]{font-family:var(--display);font-weight:800;letter-spacing:-0.02em;}
[data-testid="stMetricLabel"] p{color:var(--muted);font-weight:600;}

/* ---- expanders, alerts, tables ---- */
[data-testid="stExpander"] details{border:1px solid var(--line);border-radius:var(--r-md);
  background:var(--surface);}
[data-testid="stExpander"] summary{font-weight:700;}
[data-testid="stAlert"]{border-radius:var(--r-md);}
[data-testid="stProgress"] [role="progressbar"]>div{height:.7rem;border-radius:999px;}
[data-testid="stProgress"] [data-baseweb="progress-bar"]>div{background:var(--line);}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:var(--r-md);overflow:hidden;}
hr{border-color:var(--line)!important;}

/* ================== components ================== */
.la-glyph{flex:0 0 auto;vertical-align:middle;}

/* hero */
.la-hero h1{font-size:clamp(2.4rem,4.6vw,3.7rem);font-weight:800;line-height:1.02;margin:0 0 1.1rem;padding:0;}
.la-hero .lede{font-size:1.2rem;line-height:1.55;color:var(--muted);max-width:32rem;margin:0 0 1.6rem;}
.la-promise{border-left:4px solid var(--f-visual);padding:.2rem 0 .2rem 1rem;max-width:32rem;
  margin:1.4rem 0 0;color:var(--ink);font-size:.98rem;line-height:1.5;}
.la-pie{display:block;width:100%;max-width:470px;height:auto;margin:0 auto;overflow:visible;}
.la-pie text{font-family:var(--display);font-weight:700;fill:var(--on-fmt);}
.la-pie .sector{fill:var(--c);}
.la-pie .sector.is-picked{stroke:var(--ink);stroke-width:0;}
@media (prefers-reduced-motion:no-preference){
  .la-pie g.piece{animation:la-assemble .9s cubic-bezier(.2,.8,.2,1) both;animation-delay:var(--d);}
  @keyframes la-assemble{from{transform:translate(0,0);opacity:0;}to{transform:translate(var(--dx),var(--dy));opacity:1;}}
}
.la-pie g.piece{transform:translate(var(--dx),var(--dy));}

/* path cards on Home */
.la-step-title{font-family:var(--display);font-weight:700;font-size:clamp(.82rem,1.2vw,1.05rem);margin:.5rem 0 .3rem;white-space:nowrap;}
.la-step-copy{color:var(--muted);font-size:.9rem;line-height:1.5;margin:0 0 .8rem;}
@media (min-width:900px){.la-step-copy{min-height:7.2em;}}
.la-badge{display:inline-grid;place-items:center;width:2rem;height:2rem;border-radius:50%;
  background:var(--t-text);color:var(--brand);font-weight:800;font-size:.9rem;}
.la-chips{display:flex;flex-wrap:wrap;gap:.5rem;margin:.4rem 0 0;}
.la-chip{padding:.4rem .9rem;border:1px solid var(--line);border-radius:999px;background:var(--surface);
  font-weight:600;font-size:.92rem;}

/* recommendation */
.la-result{border-radius:var(--r-lg);padding:1.8rem 2rem;background:var(--c);color:var(--on-fmt);
  display:flex;gap:1.4rem;align-items:center;flex-wrap:wrap;margin-bottom:1rem;}
.la-result .big{display:grid;place-items:center;width:5rem;height:5rem;border-radius:50%;
  background:rgba(255,255,255,.18);flex:0 0 auto;}
.la-result .kicker{font-size:.95rem;font-weight:600;opacity:.92;margin:0 0 .2rem;}
.la-result .name{font-family:var(--display);font-weight:800;font-size:clamp(1.8rem,4vw,2.7rem);
  letter-spacing:-0.02em;line-height:1.05;margin:0;}
.la-result .second{margin:.7rem 0 0;font-size:.98rem;display:flex;align-items:center;gap:.5rem;}
.la-result .second b{font-weight:700;}
.la-bars{display:flex;flex-direction:column;gap:.9rem;margin:.4rem 0 .2rem;padding-bottom:.3rem;}
.la-bar{display:grid;grid-template-columns:8.5rem 1fr 3rem;align-items:center;gap:.8rem;font-weight:600;}
.la-bar .lbl{display:flex;align-items:center;gap:.5rem;color:var(--c);}
.la-bar .lbl span{color:var(--ink);}
.la-bar .track{height:.85rem;background:var(--paper);border:1px solid var(--line);border-radius:999px;
  overflow:hidden;}
.la-bar .fill{height:100%;background:var(--c);border-radius:999px;}
.la-bar .pct{text-align:right;font-variant-numeric:tabular-nums;}
@media (max-width:560px){.la-bar{grid-template-columns:6.5rem 1fr 2.6rem;}}
.la-panel-title{font-family:var(--display);font-weight:700;font-size:1.25rem;margin:0 0 .6rem;}
.la-list{margin:0;padding:0 0 .6rem;list-style:none;display:flex;flex-direction:column;gap:.65rem;}
.la-list li{display:flex;gap:.7rem;line-height:1.5;}
.la-list li::before{content:"";flex:0 0 .55rem;height:.55rem;margin-top:.5rem;border-radius:50%;
  background:var(--brand);}

/* lesson */
.la-section-head{display:flex;align-items:center;gap:.8rem;margin:0 0 .4rem;}
.la-section-head .num{display:grid;place-items:center;width:2.2rem;height:2.2rem;border-radius:50%;
  background:var(--fmt,var(--brand));color:var(--on-fmt);font-weight:800;flex:0 0 auto;}
.la-section-head h3{margin:0;}
.la-diagram{background:#fff;border:1px solid var(--line);border-radius:var(--r-md);padding:1rem;}
.la-support{display:flex;gap:.7rem;align-items:flex-start;padding:1rem 1.2rem;border-radius:var(--r-md);
  background:var(--t-visual);border:1px solid var(--f-visual);margin-bottom:1rem;}

/* quiz */
.la-qmeta{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin:.2rem 0 1rem;}
.la-pill{padding:.25rem .8rem;border-radius:999px;font-weight:700;font-size:.85rem;
  background:var(--t-text);color:var(--brand);border:1px solid var(--brand);}
.la .la-question{font-family:var(--display);font-weight:700;font-size:clamp(1.5rem,3.2vw,2.1rem);
  line-height:1.2;letter-spacing:-0.015em;margin:.2rem 0 1.2rem;}
.la-verdict{display:flex;gap:.7rem;align-items:center;font-family:var(--display);font-weight:800;
  font-size:1.3rem;padding:.8rem 1.1rem;border-radius:var(--r-md);margin:1rem 0 .6rem;}
.la-verdict.ok{background:var(--good-bg);color:var(--good);border:1px solid var(--good);}
.la-verdict.no{background:var(--bad-bg);color:var(--bad);border:1px solid var(--bad);}
.la-verdict span{font-family:inherit;}
.la-score{font-family:var(--display);font-weight:800;font-size:clamp(3rem,8vw,5rem);line-height:1;
  letter-spacing:-0.03em;color:var(--brand);}

/* feedback */
.la-empty{display:flex;gap:1rem;align-items:center;padding:1.6rem;border:1.5px dashed var(--line);
  border-radius:var(--r-lg);background:var(--surface);margin-bottom:1rem;}
"""


_PRO = """
/* ================== professional layer: imagery, dashboards, achievements ================== */
.stApp{background-color:var(--paper);background-image:url('app/static/img/texture_bg.jpg');
  background-repeat:no-repeat;background-size:100% auto;background-position:top center;}

.st-key-hero{background:linear-gradient(90deg,rgba(244,245,251,.86) 0%,rgba(244,245,251,.4) 55%,rgba(244,245,251,0) 100%),
  url('app/static/img/hero_bg.jpg') center/cover;border:1px solid var(--line);border-radius:28px;
  padding:2.4rem 2.6rem 2.2rem;margin-bottom:1.2rem;}
.st-key-hero .la-hero h1{font-size:clamp(2.3rem,4.2vw,3.5rem);}

.la-band{border-radius:var(--r-lg);padding:2.2rem 2.4rem;margin:0 0 1.4rem;color:#fff;overflow:hidden;
  background:linear-gradient(100deg,rgba(21,23,61,.55),rgba(21,23,61,.05)),url('app/static/img/band_bg.jpg') center/cover;}
.stApp .la-band h1{color:#fff;font-size:clamp(2rem,4vw,2.9rem);font-weight:800;margin:0 0 .5rem;padding:0;}
.la-band .lede{color:rgba(255,255,255,.9);max-width:44rem;margin:0;font-size:1.1rem;line-height:1.55;}
.la-band .tag{display:inline-flex;gap:.5rem;align-items:center;padding:.3rem .85rem;border-radius:999px;
  background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.4);font-weight:600;font-size:.85rem;margin-bottom:1rem;}

.st-key-ctaband{background:linear-gradient(100deg,rgba(21,23,61,.5),rgba(21,23,61,.05)),
  url('app/static/img/band_bg.jpg') center/cover;border-radius:var(--r-lg);padding:2rem 2.4rem;margin-top:2.4rem;}
.st-key-ctaband h2,.st-key-ctaband p,.st-key-ctaband span{color:#fff!important;}
.st-key-ctaband h2{margin:0 0 .4rem;font-size:1.8rem;}
.st-key-ctaband [data-testid="stPageLink-NavLink"]{background:#fff;border-color:#fff;padding:.8rem 1.4rem;}
.st-key-ctaband [data-testid="stPageLink-NavLink"] p,.st-key-ctaband [data-testid="stPageLink-NavLink"] span{
  color:var(--ink)!important;}

/* stat strip */
.la-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;margin:0 0 1rem;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;}
.la-stat{padding:1.1rem 1.4rem;border-right:1px solid var(--line);}
.la-stat:last-child{border-right:0;}
.la-stat .v{font-family:var(--display);font-weight:800;font-size:2rem;letter-spacing:-0.02em;line-height:1.1;color:var(--brand);}
.la-stat .l{color:var(--muted);font-size:.9rem;line-height:1.35;margin-top:.2rem;}

/* KPI cards with sparklines */
.la-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:1rem;margin:0 0 1.2rem;}
.la-kpi .valrow{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;}
.la-kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);padding:1.1rem 1.3rem 1rem;}
.la-kpi .top{display:flex;justify-content:space-between;align-items:center;gap:.5rem;}
.la-kpi .lbl{color:var(--muted);font-weight:600;font-size:.92rem;}
.la-kpi .val{font-family:var(--display);font-weight:800;font-size:2.3rem;letter-spacing:-0.02em;line-height:1.15;margin:.2rem 0 .2rem;}
.la-delta{white-space:nowrap;display:inline-flex;align-items:center;gap:.25rem;padding:.12rem .55rem;border-radius:999px;
  font-weight:700;font-size:.78rem;}
.la-delta.good{background:var(--good-bg);color:var(--good);} .la-delta.bad{background:var(--bad-bg);color:var(--bad);}
.la-delta.flat{background:var(--paper);color:var(--muted);}
.la-spark{display:block;width:100%;height:34px;margin-top:.2rem;}
.la-kpi .sub{color:var(--muted);font-size:.82rem;}

/* insights */
.la-insight{display:flex;gap:.8rem;padding:.8rem 0;border-bottom:1px solid var(--line);line-height:1.5;}
.la-insight:last-child{border-bottom:0;padding-bottom:.6rem;}
.la-insight .dot{flex:0 0 auto;width:2rem;height:2rem;border-radius:50%;display:grid;place-items:center;
  background:var(--t-text);color:var(--brand);}

/* status pills */
.la-status{display:inline-flex;align-items:center;gap:.4rem;padding:.2rem .7rem;border-radius:999px;font-weight:700;font-size:.82rem;}
.la-status.on{background:var(--good-bg);color:var(--good);border:1px solid var(--good);}
.la-status.watch{background:var(--t-steps);color:var(--f-steps);border:1px solid var(--f-steps);}
.la-status.att{background:var(--bad-bg);color:var(--bad);border:1px solid var(--bad);}

/* achievements */
.la-level{display:flex;align-items:center;gap:1.6rem;flex-wrap:wrap;}
.la-level .ring{position:relative;width:132px;height:132px;flex:0 0 auto;}
.la-level .ring .n{position:absolute;inset:0;display:grid;place-items:center;text-align:center;
  font-family:var(--display);font-weight:800;font-size:2.2rem;line-height:1;}
.la-level .ring .n small{display:block;font-size:.72rem;font-weight:600;color:var(--muted);font-family:inherit;margin-top:.15rem;}
.la-level .info{flex:1 1 220px;}
.la-level .info .big{font-family:var(--display);font-weight:800;font-size:1.6rem;letter-spacing:-0.02em;}
.la-badges{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.9rem;}
.la-bdg{border:1px solid var(--line);border-radius:var(--r-md);padding:1rem;background:var(--surface);display:flex;gap:.8rem;align-items:flex-start;}
.la-bdg .ic{flex:0 0 auto;width:2.6rem;height:2.6rem;border-radius:50%;display:grid;place-items:center;
  background:var(--c);color:var(--on-fmt);}
.la-bdg.locked{background:var(--paper);}
.la-bdg.locked .ic{background:var(--line);color:var(--muted);}
.la-bdg .nm{font-weight:700;line-height:1.2;} .la-bdg .ds{color:var(--muted);font-size:.85rem;line-height:1.35;margin-top:.15rem;}
.la-bdg .st{font-size:.75rem;font-weight:700;color:var(--good);margin-top:.3rem;}
.la-bdg.locked .st{color:var(--muted);}

/* sidebar groups (labels are plain text, not decoration: they tell students from teachers) */
[data-testid="stSidebarNav"] li:nth-child(2)::before,[data-testid="stSidebarNav"] li:nth-child(7)::before,
[data-testid="stSidebarNav"] li:nth-child(8)::before{display:block;padding:.9rem .7rem .25rem;font-size:.8rem;
  font-weight:700;color:var(--muted);}
[data-testid="stSidebarNav"] li:nth-child(2)::before{content:"For students";}
[data-testid="stSidebarNav"] li:nth-child(7)::before{content:"For teachers";}
[data-testid="stSidebarNav"] li:nth-child(8)::before{content:"About the system";}

/* tabs and dialogs */
[data-baseweb="tab-list"]{gap:.4rem;border-bottom:1px solid var(--line);}
button[role="tab"]{font-weight:700;padding:.7rem 1rem;}
[data-testid="stDialog"] div[role="dialog"]{border-radius:var(--r-lg);}
.la-note{font-size:.86rem;color:var(--muted);line-height:1.5;}
"""

_PRO_CONTRAST = """
.stApp{background-image:none!important;}
.st-key-hero,.la-band,.st-key-ctaband{background:#000!important;border:2px solid #fff!important;}
.la-band h1,.la-band .lede,.la-band .tag,.st-key-ctaband h2,.st-key-ctaband p{color:#fff!important;}
.la-stats,.la-kpi,.la-bdg{border:2px solid #fff;}
.la-stat{border-color:#fff;}
.la-spark polyline{stroke:#ffe600!important;} .la-spark circle{fill:#ffe600!important;}
.la-delta,.la-status{border:1px solid #fff;color:#fff!important;background:#000!important;}
.la-bdg.locked .ic{background:#000;border:2px dashed #fff;color:#fff;}
.la-bdg .ic{background:#ffe600;color:#000;}
.st-key-ctaband [data-testid="stPageLink-NavLink"]{background:#ffe600!important;}
.st-key-ctaband [data-testid="stPageLink-NavLink"] p,.st-key-ctaband [data-testid="stPageLink-NavLink"] span{color:#000!important;}
"""

_CONTRAST = """
:root{
  --ink:#FFFFFF; --paper:#000000; --surface:#000000; --line:#FFFFFF; --muted:#FFFFFF;
  --brand:#FFE600; --on-brand:#000000; --focus:#FFE600;
  --f-text:#FFE600; --f-audio:#FFE600; --f-visual:#FFE600; --f-steps:#FFE600; --on-fmt:#000000;
  --t-text:#000000; --t-audio:#000000; --t-visual:#000000; --t-steps:#000000;
  --good:#7CFFB2; --good-bg:#000000; --bad:#FF9C9C; --bad-bg:#000000;
}
.stApp,[data-testid="stSidebar"],[data-testid="stHeader"]{background:#000!important;}
.stApp :is(p,li,label,span,h1,h2,h3,h4,small,summary,div[data-testid="stMarkdownContainer"],
  [data-testid="stCaptionContainer"],[data-testid="stMetricValue"],[data-testid="stMetricLabel"]):not(.la *):not(button *):not([data-testid="stPageLink-NavLink"] *){
  color:#fff!important;}
.stApp a{color:#ffe600!important;text-decoration:underline!important;}
[data-testid="stSidebarNav"] a,[data-testid="stPageLink-NavLink"]{text-decoration:none!important;}
.la-badge{border:2px solid #ffe600;}
[data-testid="stSidebarNav"] a{color:#fff!important;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{
  background:#000!important;color:#ffe600!important;border:2px solid #ffe600!important;}
.stButton>button p,[data-testid="stFormSubmitButton"]>button p{color:#ffe600!important;}
.stButton>button:hover,button[data-testid="stBaseButton-primary"]:hover{background:#ffe600!important;color:#000!important;}
.stButton>button:hover p,button[data-testid="stBaseButton-primary"]:hover p{color:#000!important;}
[data-testid="stPageLink-NavLink"]{background:#000!important;border:2px solid #ffe600!important;}
[data-testid="stPageLink-NavLink"] p,[data-testid="stPageLink-NavLink"] span{color:#ffe600!important;}
.st-key-cta [data-testid="stPageLink-NavLink"]{background:#ffe600!important;}
.st-key-cta [data-testid="stPageLink-NavLink"] p,.st-key-cta [data-testid="stPageLink-NavLink"] span{color:#000!important;}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,textarea,[data-testid="stTextInputRootElement"]{background:#000!important;
  color:#fff!important;border:2px solid #fff!important;}
[data-testid="stMetric"],[data-testid="stExpander"] details,[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"]{border:2px solid #fff!important;background:#000!important;}
[data-testid="stExpander"] details,[data-testid="stExpander"] summary{background:#000!important;}
[data-testid="stAlert"]{background:#000!important;border:2px solid #fff!important;}
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]){border:2px solid #fff;background:#000;}
:is(label[data-baseweb="radio"],label[data-testid="stRadioOption"]):has(input:checked){background:#000;
  border-color:#ffe600;box-shadow:inset 0 0 0 3px #ffe600;}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:#000;border:2px solid #ffe600;}
table,th,td{background:#000!important;color:#fff!important;border-color:#fff!important;}
.la-pie text{fill:#000;} .la-glyph{color:currentColor;}
.la-bar .fill{background:#ffe600;} .la-bar .track{border-color:#fff;background:#000;}
.la-result{border:3px solid #ffe600;background:#000;color:#fff;}
.la-result .big{background:#000;border:2px solid #ffe600;}
.la-diagram{background:#fff!important;}
"""


def design_css(font_pct: int, contrast: bool, readable: bool, spacing: bool) -> str:
    css = [_FONT_FACES, _TOKENS, _BASE, _PRO]
    if contrast:
        css.append(_CONTRAST)
        css.append(_PRO_CONTRAST)
    # Non-icon text in the easy-to-read face (icon fonts must stay untouched)
    if readable:
        css.append(
            ":root{--display:'Atkinson Hyperlegible',Verdana,Arial,sans-serif;}"
            ".stApp *:not([data-testid='stIconMaterial']):not(.material-symbols-rounded):not([class*='icon']){"
            "font-family:'Atkinson Hyperlegible',Verdana,Arial,sans-serif!important;}")
    if spacing:
        css.append(".stApp p,.stApp li,.stApp label{line-height:1.9!important;"
                   "letter-spacing:.03em!important;word-spacing:.1em!important;}")
    css.append(f"html{{font-size:{font_pct}%!important;}}")
    return "".join(css)


# --------------------------------------------------------------------------- components
def journey(current: int) -> str:
    items = []
    for i, name in enumerate(JOURNEY, start=1):
        cur = ' class="is-current" aria-current="step"' if i == current else ""
        items.append(f'<li{cur}><span class="n">{i}</span><span class="t">{name}</span></li>')
    return f'<nav class="la-journey" aria-label="Your path through LearnAble"><ol>{"".join(items)}</ol></nav>'


def page_header(title: str, lede: str, step: int | None = None) -> None:
    md(f'<div class="la la-head">{journey(step) if step else ""}<h1>{html.escape(title)}</h1>'
       f'<p class="lede">{html.escape(lede)}</p></div>')


_PIECES = [  # key, label, quadrant path, label centre, pull direction, delay
    ("text", "Text", "M0 0V-150A150 150 0 0 1 150 0Z", (62, -62), (1, -1), "0s"),
    ("audio", "Audio", "M0 0H150A150 150 0 0 1 0 150Z", (62, 62), (1, 1), ".12s"),
    ("visual", "Diagrams", "M0 0V150A150 150 0 0 1 -150 0Z", (-62, 62), (-1, 1), ".24s"),
    ("steps", "Steps", "M0 0H-150A150 150 0 0 1 0 -150Z", (-62, -62), (-1, -1), ".36s"),
]


def hero_pie() -> str:
    """The signature graphic: one circle (the lesson) cut into four formats."""
    out = []
    for key, label, path, (lx, ly), (dx, dy), delay in _PIECES:
        gap = 9
        icon = (f'<g transform="translate({lx - 14},{ly - 30}) scale(1.17)" fill="none" stroke="var(--on-fmt)" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{_GLYPHS[key]}</g>')
        out.append(
            f'<g class="piece" style="--dx:{dx * gap}px;--dy:{dy * gap}px;--d:{delay}">'
            f'<path class="sector" style="--c:var(--f-{key})" d="{path}"/>{icon}'
            f'<text x="{lx}" y="{ly + 26}" text-anchor="middle" font-size="19">{label}</text></g>')
    return ('<svg class="la-pie" viewBox="-175 -175 350 350" role="img" '
            'aria-label="A circle cut into four parts: text, audio, diagrams and steps. '
            'The same lesson, four ways.">' + "".join(out) + "</svg>")


def result_card(fmt: str, second: str | None) -> None:
    k = _key(fmt)
    sec = ""
    if second:
        sec = (f'<p class="second">{glyph(second, 20)}<span>Also a good fit: <b>{html.escape(second)}</b></span></p>')
    md(f'<div class="la la-result" style="--c:var(--f-{k})"><div class="big">{glyph(fmt, 40)}</div>'
       f'<div><p class="kicker">Suggested format for you</p><h2 class="name" style="margin:0;color:inherit">'
       f'{html.escape(fmt)}</h2>{sec}</div></div>')


def ranking_bars(ranking: list[tuple[str, float]]) -> str:
    rows = []
    for fmt, p in ranking:
        pct = round(p * 100)
        k = _key(fmt)
        rows.append(
            f'<div class="la-bar" style="--c:var(--f-{k})"><div class="lbl">{glyph(fmt, 20)}'
            f'<span>{html.escape(FORMAT_STYLE[fmt]["short"])}</span></div>'
            f'<div class="track" role="img" aria-label="{html.escape(fmt)}: worked for {pct} percent">'
            f'<div class="fill" style="width:{pct}%"></div></div><div class="pct">{pct}%</div></div>')
    return f'<div class="la la-bars">{"".join(rows)}</div>'


def _inline(text: str) -> str:
    """Escape text, then turn **bold** into <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(text))


def bullet_list(items: list[str]) -> str:
    return '<ul class="la-list">' + "".join(f"<li><span>{_inline(i)}</span></li>" for i in items) + "</ul>"


def panel(title: str, body_html: str) -> None:
    """A titled block that lives inside st.container(border=True)."""
    md(f'<div class="la"><p class="la-panel-title">{html.escape(title)}</p>{body_html}</div>')


def format_color_vars(fmt: str) -> str:
    """CSS that tints lesson numbering with the chosen format's colour."""
    return f"<style>.stApp{{--fmt:var(--f-{_key(fmt)});}}</style>"


def verdict(correct: bool, text: str) -> None:
    icon = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + ('<path d="M5 12.5l4.5 4.5L19 7.5"/>' if correct else '<path d="M6 6l12 12M18 6L6 18"/>')
            + "</svg>")
    md(f'<div class="la la-verdict {"ok" if correct else "no"}" role="status">{icon}<span>{text}</span></div>')


FORMAT_HEX = {"Text explanation": "#3A3FD8", "Audio explanation": "#B8175F",
              "Visual diagrams": "#0A7C74", "Step-by-step": "#A85A00"}


def style_fig(fig, height: int = 320, top: int = 96):
    """Apply the shared look to a Plotly figure (and respect high-contrast mode)."""
    hc = st.session_state.get("a11y_contrast", False)
    ink, grid, bg = ("#FFFFFF", "#555555", "#000000") if hc else ("#15173D", "#E3E5F3", "rgba(0,0,0,0)")
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=top, b=10), paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="Figtree, Segoe UI, system-ui, sans-serif", color=ink, size=14),
        title=dict(font=dict(family="Bricolage Grotesque, Trebuchet MS, sans-serif", size=20, color=ink), x=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title_text=""))
    fig.update_xaxes(gridcolor=grid, zeroline=False, linecolor=grid)
    fig.update_yaxes(gridcolor=grid, zeroline=False, linecolor=grid)
    return fig


# --------------------------------------------------------------------------- professional components
def band_header(title: str, lede: str, tag: str = "") -> None:
    """Dark image header used on the teacher and model pages."""
    t = f'<div class="tag">{html.escape(tag)}</div><br>' if tag else ""
    md(f'<div class="la la-band">{t}<h1>{html.escape(title)}</h1><p class="lede">{html.escape(lede)}</p></div>')


def sparkline(values: list[float], color: str = "var(--brand)") -> str:
    if len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pts = [(i * 120 / (len(values) - 1), 30 - (v - lo) / span * 26) for i, v in enumerate(values)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    x, y = pts[-1]
    return (f'<svg class="la-spark" viewBox="0 0 120 34" preserveAspectRatio="none" aria-hidden="true">'
            f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{color}"/></svg>')


def kpi_cards(cards: list[dict]) -> None:
    """cards: label, value, delta (float|None), unit, up_is_good(bool), spark(list), sub(str)."""
    out = []
    for c in cards:
        d = c.get("delta")
        delta = ""
        if d is not None:
            good = (d >= 0) == c.get("up_is_good", True)
            cls = "flat" if abs(d) < 0.05 else ("good" if good else "bad")
            arrow = "M12 5l6 8H6z" if d >= 0 else "M12 19l-6-8h12z"
            delta = (f'<span class="la-delta {cls}"><svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" '
                     f'aria-hidden="true"><path d="{arrow}"/></svg>{d:+.1f}{c.get("unit_d", "")}</span>')
        out.append(f'<div class="la-kpi"><div class="top"><span class="lbl">{html.escape(c["label"])}</span></div>'
                   f'<div class="valrow"><div class="val">{c["value"]}</div>{delta}</div>{sparkline(c.get("spark", []))}'
                   f'<div class="sub">{html.escape(c.get("sub", ""))}</div></div>')
    md(f'<div class="la la-kpis">{"".join(out)}</div>')


def stat_strip(items: list[tuple[str, str]]) -> None:
    md('<div class="la la-stats">' + "".join(
        f'<div class="la-stat"><div class="v">{html.escape(v)}</div><div class="l">{html.escape(l)}</div></div>'
        for v, l in items) + "</div>")


def insight_list(items: list[str]) -> str:
    bulb = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/></svg>')
    return "".join(f'<div class="la-insight"><span class="dot">{bulb}</span><span>{_inline(t)}</span></div>' for t in items)


def status_pill(status: str) -> str:
    cls = {"On track": "on", "Watch": "watch", "Needs attention": "att"}[status]
    return f'<span class="la-status {cls}">{html.escape(status)}</span>'


def xp_ring(level: int, pct: float) -> str:
    r, c = 56, 2 * 3.14159 * 56
    return (f'<div class="ring"><svg width="132" height="132" viewBox="0 0 132 132" role="img" '
            f'aria-label="Level {level}, {pct * 100:.0f} percent to the next level">'
            f'<circle cx="66" cy="66" r="{r}" fill="none" stroke="var(--line)" stroke-width="12"/>'
            f'<circle cx="66" cy="66" r="{r}" fill="none" stroke="var(--brand)" stroke-width="12" stroke-linecap="round" '
            f'stroke-dasharray="{c * pct:.1f} {c:.1f}" transform="rotate(-90 66 66)"/></svg>'
            f'<div class="n"><div>{level}<small>Level</small></div></div></div>')


def badge_grid(badges: list[dict]) -> None:
    lock = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/>'
            '<path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>')
    out = []
    for b in badges:
        icon = glyph(b["glyph"], 20) if b["earned"] else lock
        cls = "" if b["earned"] else " locked"
        out.append(f'<div class="la-bdg{cls}" style="--c:var(--f-{b["glyph"]})"><span class="ic">{icon}</span><div>'
                   f'<div class="nm">{html.escape(b["name"])}</div><div class="ds">{html.escape(b["desc"])}</div>'
                   f'<div class="st">{"Earned" if b["earned"] else "Locked"}</div></div></div>')
    md(f'<div class="la la-badges">{"".join(out)}</div>')
