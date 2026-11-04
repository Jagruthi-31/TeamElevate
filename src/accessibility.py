"""Accessibility settings: font size, contrast, readable font, spacing, text-to-speech."""
import html

import streamlit as st
import streamlit.components.v1 as components

from .theme import design_css

DEFAULTS = {
    "a11y_font_pct": 100,
    "a11y_contrast": False,
    "a11y_readable_font": False,
    "a11y_spacing": False,
    "a11y_tts": True,
}


def init_settings() -> None:
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)
        # keep value alive when a page without this widget is shown
        st.session_state[k] = st.session_state[k]


def sidebar_settings() -> None:
    """Render accessibility controls in the sidebar (called on every page)."""
    with st.sidebar:
        st.markdown("### Accessibility")
        st.slider("Text size (%)", 80, 200, key="a11y_font_pct", step=10,
                  help="Makes all text larger or smaller.")
        st.toggle("High contrast", key="a11y_contrast")
        st.toggle("Easy-to-read font", key="a11y_readable_font",
                  help="Uses Atkinson Hyperlegible (designed for readability).")
        st.toggle("Extra line spacing", key="a11y_spacing")
        st.toggle("Show read-aloud buttons", key="a11y_tts")
        st.markdown('<p class="la-side-note">Keyboard: Tab and Shift+Tab to move, Enter or Space to '
                    'select, arrow keys on sliders and radio buttons.</p>', unsafe_allow_html=True)


def inject_css() -> None:
    """Global look (src/theme.py) plus the user's accessibility choices."""
    s = st.session_state
    css = design_css(s.a11y_font_pct, s.a11y_contrast, s.a11y_readable_font, s.a11y_spacing)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def read_aloud(text: str, label: str = "Read aloud", rate: float = 1.0, key: str = "tts") -> None:
    """Browser text-to-speech button (uses the Web Speech API, no server needed)."""
    if not st.session_state.get("a11y_tts", True):
        return
    safe = html.escape(text, quote=True).replace("\n", " ")
    contrast = st.session_state.get("a11y_contrast", False)
    bg, fg, bd = ("#000", "#ffe600", "#ffe600") if contrast else ("#3A3FD8", "#fff", "#3A3FD8")
    page = f"""
    <div style="display:flex;gap:8px;font-family:Figtree,Segoe UI,Arial,sans-serif;background:transparent">
      <button id="play-{key}" aria-label="{label}" style="padding:10px 18px;font-size:16px;font-weight:700;font-family:inherit;border-radius:12px;
        border:2px solid {bd};background:{bg};color:{fg};cursor:pointer">&#128266; {label}</button>
      <button id="stop-{key}" aria-label="Stop reading" style="padding:10px 18px;font-size:16px;font-weight:700;font-family:inherit;border-radius:12px;
        border:2px solid {bd};background:transparent;color:{bd};cursor:pointer">&#9632; Stop</button>
    </div>
    <script>
      const txt = "{safe}";
      document.getElementById("play-{key}").onclick = () => {{
        if (!('speechSynthesis' in window)) {{ alert('Read-aloud is not supported in this browser.'); return; }}
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(txt); u.rate = {rate}; u.lang = 'en-US';
        window.speechSynthesis.speak(u);
      }};
      document.getElementById("stop-{key}").onclick = () => window.speechSynthesis.cancel();
    </script>""".strip()
    if hasattr(st, "iframe"):              # newer Streamlit
        st.iframe(page, height=60)
    else:                                  # older Streamlit fallback
        components.html(page, height=60)
