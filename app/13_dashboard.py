"""
13_dashboard.py  — ER-alpha Drug Repurposing Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Redesigned frontend: publication-quality scientific analytics platform
Theme: Obsidian · Crimson · Gold · Ivory
Run:   streamlit run 13_dashboard.py
"""

import warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")


try:
    import streamlit as st
    import plotly.graph_objects as go
except ImportError:
    raise ImportError("pip install streamlit plotly  ->  streamlit run 13_dashboard.py")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hybrid-VLS | ER-α Drug Repurposing",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("results")

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM
#  ─────────────────────────────────────────────────────────────────────────────
#  Color tokens, font tokens, and shared constants live here.
#  Reference C["token"] everywhere — never hardcode hex values.
# ══════════════════════════════════════════════════════════════════════════════

C = {
    # Backgrounds — layered depth
    "bg_base":      "#08080a",      # near-black, deepest layer
    "bg_surface":   "#0f0d0e",      # main surface
    "bg_elevated":  "#161012",      # raised surfaces (cards, panels)
    "bg_card":      "#1c1214",      # deepest card background
    "bg_card_hi":   "#221517",      # hover/active card state
    "bg_sidebar":   "#100c0d",      # sidebar background

    # Borders
    "border":       "#2a1a1c",      # base border (very dim)
    "border_mid":   "#3d2020",      # mid-weight border
    "border_hi":    "#6b2020",      # strong crimson border
    "border_gold":  "#5a4010",      # gold border

    # Crimson — primary accent
    "crimson":      "#c41e3a",
    "crimson_dim":  "#6b1222",
    "crimson_hi":   "#e6304e",
    "crimson_glow": "rgba(196,30,58,0.18)",

    # Gold — secondary accent
    "gold":         "#c8920f",
    "gold_dim":     "#7a5808",
    "gold_hi":      "#e8b420",
    "gold_pale":    "#f5d980",
    "gold_glow":    "rgba(200,146,15,0.15)",

    # Text
    "ivory":        "#f0ebe0",      # primary text
    "ivory_mid":    "#bdb5a0",      # secondary text
    "ivory_lo":     "#6e6558",      # tertiary / labels
    "ivory_ghost":  "#38322a",      # very dim text

    # Semantic
    "success":      "#3db874",
    "warn":         "#e07b30",
    "info":         "#4a9ec4",

    "white":        "#ffffff",
}

# Font families
F_DISPLAY = "Cormorant SC"         # Elegant serif for hero/display titles
F_HEADING = "DM Serif Display"     # Strong serif for section headings
F_BODY    = "Jost"                 # Clean geometric sans for body
F_MONO    = "JetBrains Mono"       # Technical mono for data/labels/stats

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS INJECTION
#  ─────────────────────────────────────────────────────────────────────────────
#  Injected once at top. Overrides all default Streamlit styles.
#  Sections: fonts → base → sidebar → metrics → tabs → buttons →
#            inputs → headings → dataframe → scrollbar → utilities
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+SC:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&family=Jost:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

/* ── CSS Custom Properties ── */
:root {{
  --crimson:      {C["crimson"]};
  --crimson-dim:  {C["crimson_dim"]};
  --crimson-hi:   {C["crimson_hi"]};
  --gold:         {C["gold"]};
  --gold-hi:      {C["gold_hi"]};
  --ivory:        {C["ivory"]};
  --ivory-mid:    {C["ivory_mid"]};
  --ivory-lo:     {C["ivory_lo"]};
  --bg-base:      {C["bg_base"]};
  --bg-elevated:  {C["bg_elevated"]};
  --border:       {C["border"]};
  --border-hi:    {C["border_hi"]};
  --font-display: '{F_DISPLAY}', serif;
  --font-heading: '{F_HEADING}', serif;
  --font-body:    '{F_BODY}', sans-serif;
  --font-mono:    '{F_MONO}', monospace;
}}

/* ── Base ── */
html, body, [class*="css"] {{
    font-family: var(--font-body);
    background-color: {C["bg_base"]};
    color: {C["ivory"]};
}}
.stApp {{
    background-color: {C["bg_base"]};
    background-image:
        radial-gradient(ellipse 80% 60% at 5% 0%, {C["crimson"]}14 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 95% 100%, {C["gold"]}0c 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 50% 50%, {C["crimson"]}06 0%, transparent 70%);
}}

/* ── Streamlit main block padding ── */
.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1400px !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {C["bg_sidebar"]} !important;
    border-right: 1px solid {C["border_mid"]} !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.5rem !important;
}}
section[data-testid="stSidebar"] * {{
    color: {C["ivory_mid"]} !important;
}}
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4 {{
    color: {C["gold"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(145deg, {C["bg_card"]} 0%, {C["bg_elevated"]} 100%);
    border: 1px solid {C["border_mid"]};
    border-top: 2px solid {C["crimson"]};
    border-radius: 3px;
    padding: 18px 20px 14px 20px;
    transition: all 220ms ease;
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {C["crimson"]}80, transparent);
}}
[data-testid="metric-container"]:hover {{
    border-color: {C["gold"]};
    border-top-color: {C["gold_hi"]};
    box-shadow: 0 0 28px {C["crimson"]}22, 0 4px 20px rgba(0,0,0,0.4);
    transform: translateY(-1px);
}}
[data-testid="stMetricLabel"] p {{
    color: {C["ivory_lo"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 9.5px !important;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    color: {C["gold_hi"]} !important;
    font-family: var(--font-display) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    line-height: 1.15 !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 1px solid {C["border_hi"]};
    gap: 0;
    padding: 0;
}}
[data-testid="stTabs"] button {{
    font-family: var(--font-mono);
    font-size: 10.5px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {C["ivory_lo"]};
    padding: 10px 22px;
    border-radius: 0;
    transition: all 180ms ease;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}}
[data-testid="stTabs"] button:hover {{
    color: {C["ivory_mid"]};
    background: {C["bg_elevated"]};
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {C["gold_hi"]};
    background: linear-gradient(180deg, {C["bg_card"]} 0%, transparent 100%);
    border-bottom: 2px solid {C["gold"]};
    font-weight: 500;
}}
[data-testid="stTabs"] [role="tabpanel"] {{
    padding-top: 1.5rem;
}}

/* ── Buttons ── */
.stDownloadButton button, .stButton button {{
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: transparent;
    color: {C["ivory_mid"]};
    border: 1px solid {C["border_hi"]};
    border-radius: 2px;
    padding: 9px 22px;
    transition: all 180ms ease;
}}
.stDownloadButton button:hover, .stButton button:hover {{
    background: {C["crimson"]};
    color: {C["ivory"]};
    border-color: {C["crimson_hi"]};
    box-shadow: 0 0 20px {C["crimson"]}55;
}}

/* ── Inputs ── */
.stTextInput input {{
    background: {C["bg_elevated"]} !important;
    border: 1px solid {C["border_mid"]} !important;
    border-radius: 2px !important;
    color: {C["ivory"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    transition: border-color 180ms ease !important;
}}
.stTextInput input:focus {{
    border-color: {C["crimson"]} !important;
    box-shadow: 0 0 10px {C["crimson"]}33 !important;
    outline: none !important;
}}
.stSelectbox > div > div {{
    background: {C["bg_elevated"]} !important;
    border: 1px solid {C["border_mid"]} !important;
    border-radius: 2px !important;
    color: {C["ivory"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
}}
.stMultiSelect > div > div {{
    background: {C["bg_elevated"]} !important;
    border: 1px solid {C["border_mid"]} !important;
    border-radius: 2px !important;
}}

/* ── Sliders ── */
[data-testid="stSlider"] [role="slider"] {{
    background: {C["crimson"]} !important;
    border: 2px solid {C["crimson_hi"]} !important;
}}
[data-testid="stSlider"] > div > div > div {{
    background: {C["border_hi"]} !important;
}}
[data-testid="stSlider"] .stSlider {{
    color: {C["ivory_lo"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
}}

/* ── Checkboxes / Radio ── */
.stCheckbox label, .stRadio label {{
    font-family: var(--font-mono);
    font-size: 11px;
    color: {C["ivory_mid"]};
    letter-spacing: 0.04em;
}}

/* ── Headings (native markdown) ── */
h1 {{
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    color: {C["ivory"]} !important;
    letter-spacing: 0.04em;
    line-height: 1.1;
}}
h2 {{
    font-family: var(--font-heading) !important;
    font-weight: 400 !important;
    color: {C["gold"]} !important;
    font-size: 21px !important;
    letter-spacing: 0.02em;
    border-bottom: 1px solid {C["border_mid"]};
    padding-bottom: 10px;
    margin-bottom: 22px;
}}
h3 {{
    font-family: var(--font-mono) !important;
    color: {C["ivory_lo"]} !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}}
p {{
    font-family: var(--font-body);
    line-height: 1.7;
    color: {C["ivory_mid"]};
}}

/* ── Divider ── */
hr {{
    border: none !important;
    border-top: 1px solid {C["border_mid"]} !important;
    opacity: 0.6 !important;
    margin: 1.5rem 0 !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {C["border_hi"]};
    border-radius: 3px;
    overflow: hidden;
}}
[data-testid="stDataFrame"] th {{
    background: {C["bg_elevated"]} !important;
    color: {C["gold"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid {C["border_hi"]} !important;
    padding: 10px 12px !important;
}}
[data-testid="stDataFrame"] td {{
    background: {C["bg_card"]} !important;
    color: {C["ivory_mid"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    border-bottom: 1px solid {C["border"]} !important;
}}
[data-testid="stDataFrame"] tr:hover td {{
    background: {C["bg_card_hi"]} !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: {C["bg_elevated"]} !important;
    border: 1px solid {C["border_mid"]} !important;
    border-radius: 3px !important;
}}
[data-testid="stExpander"] summary {{
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    color: {C["ivory_mid"]} !important;
    text-transform: uppercase !important;
}}
[data-testid="stExpander"] summary:hover {{
    color: {C["gold"]} !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {C["bg_base"]}; }}
::-webkit-scrollbar-thumb {{
    background: {C["crimson_dim"]};
    border-radius: 2px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {C["crimson"]}; }}

/* ── Caption ── */
.stCaption, small {{
    color: {C["ivory_lo"]} !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 0.06em !important;
}}

/* ── Alert / Warning ── */
[data-testid="stAlert"] {{
    background: {C["bg_elevated"]} !important;
    border: 1px solid {C["border_hi"]} !important;
    border-radius: 3px !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  REUSABLE UI COMPONENTS
#  ─────────────────────────────────────────────────────────────────────────────
#  All custom HTML components live here as functions.
#  Import/call these — don't inline raw HTML elsewhere.
# ══════════════════════════════════════════════════════════════════════════════

def section_label(text: str):
    """Eyebrow label above section headings."""
    st.markdown(
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['crimson']};letter-spacing:0.22em;"
        f"text-transform:uppercase;margin:0 0 6px 0;line-height:1'>{text}</p>",
        unsafe_allow_html=True,
    )


def section_heading(text: str, subtitle: str = ""):
    """Styled h2 heading with optional subtitle."""
    html = (
        f"<h2 style='font-family:{F_HEADING};font-weight:400;font-size:22px;"
        f"color:{C['gold']};letter-spacing:0.02em;border-bottom:1px solid {C['border_mid']};"
        f"padding-bottom:10px;margin:0 0 6px 0'>{text}</h2>"
    )
    if subtitle:
        html += (
            f"<p style='font-family:{F_MONO};font-size:10px;color:{C['ivory_lo']};"
            f"letter-spacing:0.08em;margin:0 0 18px 0'>{subtitle}</p>"
        )
    st.markdown(html, unsafe_allow_html=True)


def stat_card(label: str, value: str, sub: str = "", accent_color: str = None):
    """
    Standalone stat card rendered as HTML.
    Used where native st.metric is not enough control.
    """
    color = accent_color or C["gold_hi"]
    st.markdown(
        f"<div style='background:linear-gradient(145deg,{C['bg_card']} 0%,{C['bg_elevated']} 100%);"
        f"border:1px solid {C['border_mid']};border-top:2px solid {color};"
        f"border-radius:3px;padding:18px 20px;'>"
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
        f"letter-spacing:0.16em;text-transform:uppercase;margin:0 0 8px 0'>{label}</p>"
        f"<p style='font-family:{F_DISPLAY};font-size:34px;font-weight:600;"
        f"color:{color};margin:0;line-height:1'>{value}</p>"
        f"{'<p style='+chr(39)+'font-family:'+F_MONO+';font-size:10px;color:'+C['ivory_lo']+';margin:6px 0 0 0'+chr(39)+'>'+sub+'</p>' if sub else ''}"
        f"</div>",
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str, accent: str = None):
    """
    General-purpose info/annotation card.
    accent: hex color for left border.
    """
    border_color = accent or C["crimson"]
    st.markdown(
        f"<div style='background:linear-gradient(135deg,{C['bg_card']} 0%,{C['bg_elevated']} 100%);"
        f"border:1px solid {C['border_mid']};border-left:3px solid {border_color};"
        f"border-radius:3px;padding:16px 20px;margin-bottom:12px'>"
        f"<p style='font-family:{F_MONO};font-size:9.5px;color:{C['ivory_lo']};"
        f"letter-spacing:0.14em;text-transform:uppercase;margin:0 0 8px 0'>{title}</p>"
        f"<p style='font-family:{F_BODY};font-size:12px;color:{C['ivory_mid']};margin:0;line-height:1.6'>{body}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


def progress_row(label: str, n: int, total: int, color: str):
    """
    Inline label + count + mini bar.
    Used for classification breakdown.
    """
    pct = 100 * n / max(total, 1)
    st.markdown(
        f"<div style='margin-bottom:12px'>"
        f"<div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px'>"
        f"<span style='font-family:{F_MONO};font-size:10.5px;color:{color};letter-spacing:0.04em'>{label}</span>"
        f"<span style='font-family:{F_DISPLAY};font-size:17px;font-weight:600;color:{C['ivory']}'>"
        f"{n}<span style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};margin-left:5px'>{pct:.0f}%</span>"
        f"</span></div>"
        f"<div style='height:2px;background:{C['border']};border-radius:2px'>"
        f"<div style='height:2px;width:{max(pct,1.5):.1f}%;background:{color};"
        f"border-radius:2px;transition:width 0.6s ease'></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


def color_dot_legend(items: list):
    """
    Horizontal legend row of color dot + label pairs.
    items: list of (label, color, description) tuples.
    """
    html = "<div style='display:flex;flex-wrap:wrap;gap:18px;margin:8px 0 16px 0'>"
    for label, color, desc in items:
        html += (
            f"<div style='display:flex;align-items:center;gap:7px'>"
            f"<div style='width:8px;height:8px;border-radius:2px;background:{color};"
            f"flex-shrink:0'></div>"
            f"<span style='font-family:{F_MONO};font-size:10px;color:{C['ivory_mid']}'>"
            f"<span style='color:{color}'>{label}</span> — {desc}</span>"
            f"</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def pipeline_step(num: int, title: str, detail: str, is_last: bool = False):
    """One step in the methodology pipeline overview."""
    st.markdown(
        f"<div style='display:flex;gap:16px;margin-bottom:{'4px' if not is_last else '0'}'>"
        f"<div style='display:flex;flex-direction:column;align-items:center;flex-shrink:0'>"
        f"<div style='width:28px;height:28px;border-radius:50%;background:{C['bg_card']};"
        f"border:1.5px solid {C['crimson']};display:flex;align-items:center;justify-content:center;"
        f"font-family:{F_MONO};font-size:10px;color:{C['crimson_hi']};font-weight:600;flex-shrink:0'>{num}</div>"
        f"{'<div style=width:1px;flex:1;background:'+C['border_mid']+';margin:4px 0></div>' if not is_last else ''}"
        f"</div>"
        f"<div style='padding-bottom:{'18px' if not is_last else '0'}'>"
        f"<p style='font-family:{F_BODY};font-size:13px;font-weight:500;color:{C['ivory']};margin:4px 0 3px 0;line-height:1.3'>{title}</p>"
        f"<p style='font-family:{F_MONO};font-size:10px;color:{C['ivory_lo']};margin:0;line-height:1.6'>{detail}</p>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PLOTLY THEME UTILITIES
#  ─────────────────────────────────────────────────────────────────────────────
#  All Plotly charts use make_layout() + axis_style() for unified theming.
# ══════════════════════════════════════════════════════════════════════════════

def make_layout(**kwargs):
    """
    Build a Plotly layout dict with our design system defaults.
    Pass any axis or other overrides as kwargs — they merge over the base.
    """
    base = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",   # transparent to show card bg
        plot_bgcolor=C["bg_base"],
        font=dict(
            family=f"'{F_MONO}', monospace",
            color=C["ivory_mid"],
            size=11,
        ),
        margin=dict(l=52, r=28, t=48, b=46),
        hoverlabel=dict(
            bgcolor=C["bg_elevated"],
            bordercolor=C["border_hi"],
            font=dict(
                family=f"'{F_MONO}', monospace",
                size=12,
                color=C["ivory"],
            ),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=C["border_mid"],
            borderwidth=1,
            font=dict(size=10, color=C["ivory_mid"]),
        ),
    )
    base.update(kwargs)
    return base


def axis_style(**kwargs):
    """Return a consistently styled Plotly axis dict. Override with kwargs."""
    base = dict(
        gridcolor=C["border"],
        gridwidth=1,
        zerolinecolor=C["border_hi"],
        zerolinewidth=1,
        tickfont=dict(size=10, color=C["ivory_mid"], family=f"'{F_MONO}'"),
        title_font=dict(size=11, color=C["ivory_lo"], family=f"'{F_MONO}'"),
        showline=True,
        linecolor=C["border_mid"],
        linewidth=1,
    )
    base.update(kwargs)
    return base


# ══════════════════════════════════════════════════════════════════════════════
#  DATA LOADING  (unchanged from original)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    cand_path = DATA_DIR / "final_ranked_candidates.csv"
    admet_path = DATA_DIR / "admet_results.csv"
    dock_path = DATA_DIR / "docking_scores.csv"
    sum_path = DATA_DIR / "analysis_summary.txt"

    # Safely load files only if they exist, otherwise create empty DataFrames
    df_cand = pd.read_csv(cand_path) if cand_path.exists() else pd.DataFrame()
    df_admet = pd.read_csv(admet_path) if admet_path.exists() else pd.DataFrame()
    df_dock = pd.read_csv(dock_path) if dock_path.exists() else pd.DataFrame()

    # Read summary text if available
    if sum_path.exists():
        with open(sum_path, "r", encoding="utf-8") as f:
            summary_text = f.read()
    else:
        summary_text = "Virtual Screening analysis complete."

    # Fallback checking: Core candidate file is absolutely required
    if df_cand.empty:
        st.error(f"⚠️ Core file missing: '{cand_path.name}' not found in '{DATA_DIR}' folder.")
        st.stop()

    return df_cand, df_admet, df_dock, summary_text


# Execute the data loading function
df_cand, df_admet, df_dock, summary_text = load_data()

df = df_cand
source_file = "final_ranked_candidates.csv"

if not df.empty:
    if "strong_hits" not in df.columns:
        if "vina_score" in df.columns:
            df["strong_hits"] = df["vina_score"] <= -9.0
        else:
            df["strong_hits"] = False

    if "drug_like" not in df.columns:
        df["drug_like"] = True

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Branding block
    st.markdown(
        f"<div style='padding:4px 0 16px 0;border-bottom:1px solid {C['border_mid']};margin-bottom:20px'>"
        f"<p style='font-family:{F_DISPLAY};font-size:13px;letter-spacing:0.2em;"
        f"color:{C['ivory_lo']};margin:0 0 3px 0;text-transform:uppercase'>Hybrid-VLS</p>"
        f"<p style='font-family:{F_DISPLAY};font-size:20px;color:{C['crimson_hi']};"
        f"font-weight:600;letter-spacing:0.06em;margin:0;line-height:1.2'>ER-α Pipeline</p>"
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['gold_dim']};"
        f"margin:6px 0 0 0;letter-spacing:0.12em;text-transform:uppercase'>"
        f"PDB 1ERE · Breast Cancer · FDA Drugs</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Filters ──
    st.markdown(
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
        f"letter-spacing:0.18em;text-transform:uppercase;margin:0 0 10px 0'>Compound Filters</p>",
        unsafe_allow_html=True,
    )
    show_strong    = st.checkbox("Strong hits only", value=False)
    show_drug_like = st.checkbox("Drug-like only (Ro5 + Veber + no alerts)", value=False)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if "vina_score" in df_cand.columns:
        v_min = float(df["vina_score"].min())
        vina_range = st.slider("Vina score (kcal/mol)", v_min, 0.0, (v_min, 0.0), step=0.1)
    else:
        vina_range = (-12.0, 0.0)

    st.divider()

    # ── Composite weights ──
    st.markdown(
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
        f"letter-spacing:0.18em;text-transform:uppercase;margin:0 0 10px 0'>Composite Weights</p>",
        unsafe_allow_html=True,
    )
    w_dp   = st.slider("DeepPurpose weight", 0.0, 1.0, 0.4, 0.05)
    w_vina = round(1.0 - w_dp, 2)
    st.markdown(
        f"<div style='background:{C['bg_elevated']};border:1px solid {C['border_mid']};"
        f"border-radius:2px;padding:10px 12px;margin-top:4px'>"
        f"<div style='display:flex;justify-content:space-between'>"
        f"<span style='font-family:{F_MONO};font-size:10px;color:{C['ivory_lo']}'>Vina weight</span>"
        f"<span style='font-family:{F_DISPLAY};font-size:16px;color:{C['gold_hi']};font-weight:600'>"
        f"{w_vina}</span></div></div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Data info ──
    st.markdown(
        f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
        f"letter-spacing:0.18em;text-transform:uppercase;margin:0 0 8px 0'>Data Source</p>"
        f"<p style='font-family:{F_MONO};font-size:10px;color:{C['ivory_lo']};line-height:1.8'>"
        f"File: <span style='color:{C['ivory_mid']}'>{source_file}</span><br>"
        f"Candidates: <span style='color:{C['gold_hi']};font-weight:500'>{len(df):,}</span><br>"
        f"Strong hits: <span style='color:{C['crimson_hi']}'>{int(df['strong_hit'].sum())}</span><br>"
        f"Drug-like: <span style='color:{C['success']}'>{int(df['drug_like'].sum())}</span>"
        f"</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FILTER APPLICATION  (unchanged logic)
# ══════════════════════════════════════════════════════════════════════════════

mask = pd.Series([True] * len(df), index=df.index)
if show_strong:    mask &= df["strong_hit"]
if show_drug_like: mask &= df["drug_like"]
if "vina_score" in df.columns:
    mask &= df["vina_score"].between(*vina_range)
fdf = df[mask].copy()

if "dp_percentile" in fdf.columns and "vina_percentile" in fdf.columns:
    fdf["composite_score"] = w_dp * fdf["dp_percentile"] + w_vina * fdf["vina_percentile"]
    fdf["composite_rank"]  = fdf["composite_score"].rank(method="min").astype(int)
    fdf = fdf.sort_values("composite_rank")


# ══════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
#  ─────────────────────────────────────────────────────────────────────────────
#  Full-width header with project identity, pipeline overview, and about block.
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f"<div style='padding:2px 0 8px 0'>"
    f"<p style='font-family:{F_MONO};font-size:9px;color:{C['crimson']};letter-spacing:0.22em;"
    f"text-transform:uppercase;margin:0 0 8px 0'>Computational Drug Repurposing · Target PDB 1ERE</p>"
    f"<h1 style='font-family:{F_DISPLAY};font-size:42px;font-weight:600;margin:0;line-height:1.1;"
    f"background:linear-gradient(95deg,{C['ivory']} 0%,{C['gold_pale']} 60%,{C['gold_hi']} 100%);"
    f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"
    f"letter-spacing:0.03em'>Estrogen Receptor-α Drug Repurposing</h1>"
    f"<p style='font-family:{F_BODY};font-size:14px;color:{C['ivory_lo']};margin:10px 0 0 0;"
    f"letter-spacing:0.02em;font-weight:300'>"
    f"DeepPurpose MPNN-CNN &ensp;·&ensp; AutoDock Vina 3D Docking &ensp;·&ensp; RDKit ADMET Profiling</p>"
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── KPI Strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

best_vina = f"{df['vina_score'].min():.2f}" if "vina_score" in df.columns else "--"
best_ml   = f"{df['binding_score'].min():.1f}" if "binding_score" in df.columns else "--"

k1.metric("Screened",      "2,057",    help="FDA-approved Broad Hub compounds screened")
k2.metric("ML Top Hits",   f"{len(df):,}",    help="DeepPurpose top candidates")
k3.metric("Strong Hits",   int(df["strong_hit"].sum()), help="Vina ≤ −7.0 AND top-25% ML score")
k4.metric("Drug-like",     int(df["drug_like"].sum()),  help="Pass Ro5 + Veber + no PAINS/BRENK alerts")
k5.metric("Best Vina",     best_vina,  help="ΔG kcal/mol — lower is stronger binding")
k6.metric("Best ML (nM)",  best_ml,    help="DeepPurpose predicted Ki in nM — lower is better")

st.divider()


# ── About + Methodology expander block ────────────────────────────────────────
with st.expander("◈  About this Dashboard & Methodology", expanded=False):
    col_about, col_pipe = st.columns([3, 2], gap="large")

    with col_about:
        section_label("Project Overview")
        st.markdown(
            f"<h3 style='font-family:{F_HEADING};font-weight:400;font-size:18px;"
            f"color:{C['gold']};margin:0 0 12px 0;letter-spacing:0.01em'>"
            f"What is this dashboard?</h3>"
            f"<p style='font-family:{F_BODY};font-size:13px;color:{C['ivory_mid']};line-height:1.75;margin:0 0 14px 0'>"
            f"This platform presents results from a hybrid virtual ligand screening (VLS) pipeline targeting the "
            f"<strong style='color:{C['ivory']}'>Estrogen Receptor-alpha (ER-α)</strong>, a primary driver in "
            f"hormone receptor-positive breast cancer (~75% of cases). By systematically screening FDA-approved "
            f"drugs against the resolved crystal structure (PDB: 1ERE), we identify repurposing candidates — "
            f"approved compounds that may exhibit previously unreported ER-α antagonism."
            f"</p>"
            f"<p style='font-family:{F_BODY};font-size:13px;color:{C['ivory_mid']};line-height:1.75;margin:0 0 14px 0'>"
            f"<strong style='color:{C['ivory']}'>Motivation:</strong> Drug repurposing leverages known safety profiles "
            f"and pharmacokinetics to dramatically reduce time-to-clinic. Traditional de novo drug discovery takes "
            f"10–15 years; repurposing shortens this substantially. Computational screening enables rapid, low-cost "
            f"hypothesis generation before expensive wet-lab validation."
            f"</p>"
            f"<p style='font-family:{F_BODY};font-size:13px;color:{C['ivory_mid']};line-height:1.75;margin:0 0 14px 0'>"
            f"<strong style='color:{C['ivory']}'>Datasets & Models:</strong> The Broad Institute's FDA-approved drug "
            f"library (2,057 compounds) was screened. Binding affinity (Ki, nM) was predicted by <em>DeepPurpose</em>'s "
            f"MPNN-CNN architecture. Top ML candidates were re-scored via <em>AutoDock Vina</em> 3D molecular docking "
            f"against PDB 1ERE. All compounds were characterized with <em>RDKit</em> ADMET descriptors."
            f"</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
            f"letter-spacing:0.16em;text-transform:uppercase;margin:16px 0 8px 0'>What you can explore</p>",
            unsafe_allow_html=True,
        )
        for item in [
            ("Overview", "ML score vs. docking score scatter, classification breakdown, correlation statistics"),
            ("Docking", "Full ranked docking score table, score distribution, per-compound energy analysis"),
            ("ADMET", "Drug-likeness radar, Lipinski/Veber rule compliance, MW vs. LogP landscape"),
            ("Top Candidates", "Ranked composite leaderboard, filterable by weights, downloadable CSV"),
            ("Full Table", "Complete results with multi-column search, filter, and export"),
        ]:
            st.markdown(
                f"<div style='display:flex;gap:10px;margin-bottom:8px;align-items:flex-start'>"
                f"<span style='font-family:{F_MONO};font-size:9px;color:{C['crimson']};margin-top:3px;"
                f"letter-spacing:0.1em;flex-shrink:0;text-transform:uppercase'>{item[0]}</span>"
                f"<span style='font-family:{F_BODY};font-size:12px;color:{C['ivory_lo']};line-height:1.6'>{item[1]}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    with col_pipe:
        section_label("Pipeline")
        st.markdown(
            f"<p style='font-family:{F_HEADING};font-weight:400;font-size:18px;"
            f"color:{C['gold']};margin:0 0 18px 0'>Screening Workflow</p>",
            unsafe_allow_html=True,
        )
        pipeline_steps = [
            ("Library Preparation", "FDA-approved compound library (Broad Hub, 2,057 drugs) · SMILES canonicalization · RDKit sanitization"),
            ("ML Affinity Prediction", "DeepPurpose MPNN-CNN model · Predicted Ki (nM) for ER-α sequence · Ranked by predicted binding affinity"),
            ("Candidate Filtering", "Top 5% by ML score selected · Structural flagging (PAINS, Alarm-NMR) · Lipinski Ro5 pre-filter"),
            ("3D Molecular Docking", "AutoDock Vina · Receptor: PDB 1ERE (pre-processed) · Grid: ligand-binding domain · 9 conformers/compound"),
            ("ADMET Profiling", "RDKit descriptors: MW, LogP, HBD/A, TPSA, RotBonds, Fsp3, QED · Veber oral bioavailability filter"),
            ("Composite Ranking", "Weighted percentile score: w_DP × DP_pct + w_Vina × Vina_pct · User-adjustable weights in sidebar"),
        ]
        for i, (title, detail) in enumerate(pipeline_steps):
            pipeline_step(i + 1, title, detail, is_last=(i == len(pipeline_steps) - 1))

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"<div style='background:{C['bg_card']};border:1px solid {C['border_mid']};"
            f"border-left:3px solid {C['gold_dim']};border-radius:3px;padding:12px 14px'>"
            f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
            f"letter-spacing:0.14em;text-transform:uppercase;margin:0 0 6px 0'>Note</p>"
            f"<p style='font-family:{F_BODY};font-size:11px;color:{C['ivory_lo']};margin:0;line-height:1.6'>"
            f"All predictions are computational only. Results require experimental validation "
            f"(binding assays, cell viability, in vivo) before any clinical interpretation."
            f"</p></div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⬡  Overview",
    "◈  Docking",
    "◇  ADMET",
    "★  Top Candidates",
    "▦  Full Table",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    section_label("Dual-Score Analysis")
    section_heading("ML Score vs. Docking Score", "Comparative landscape of predicted binding affinity")

    if "binding_score" in fdf.columns and "vina_score" in fdf.columns:
        col_l, col_r = st.columns([3, 1], gap="large")

        with col_l:
            def classify_row(row):
                if row.get("strong_hit") and row.get("drug_like"): return "Prime Candidate"
                if row.get("strong_hit"):  return "Strong Hit"
                if row.get("drug_like"):   return "Drug-like"
                return "Candidate"

            fdf["_class"] = fdf.apply(classify_row, axis=1)
            cmap = {
                "Prime Candidate": C["gold_hi"],
                "Strong Hit":      C["crimson_hi"],
                "Drug-like":       C["success"],
                "Candidate":       C["ivory_ghost"],
            }

            fig_sc = go.Figure()
            for cls, grp in fdf.groupby("_class"):
                sz = (grp["QED"] * 20 + 6).tolist() if "QED" in grp.columns else [9] * len(grp)
                fig_sc.add_trace(go.Scatter(
                    x=grp["binding_score"], y=grp["vina_score"],
                    mode="markers",
                    marker=dict(
                        size=sz,
                        color=cmap.get(cls, C["ivory_ghost"]),
                        line=dict(width=0.8, color=C["bg_base"]),
                        opacity=0.85,
                    ),
                    name=cls,
                    text=grp["drug_name"],
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "ML Score: %{x:.2f} nM<br>"
                        "Vina ΔG: %{y:.2f} kcal/mol"
                        "<extra></extra>"
                    ),
                ))

            # Reference lines with clean annotation style
            fig_sc.add_hline(
                y=-7.0, line_dash="dash",
                line=dict(color=C["crimson"], width=1, dash="dot"),
                annotation_text="Vina −7.0 threshold",
                annotation_font=dict(color=C["crimson"], size=9, family=F_MONO),
                annotation_position="bottom right",
            )
            if len(fdf) > 0:
                dp_cut = np.percentile(fdf["binding_score"], 25)
                fig_sc.add_vline(
                    x=dp_cut, line_dash="dot",
                    line=dict(color=C["gold_dim"], width=1),
                    annotation_text="ML top 25%",
                    annotation_font=dict(color=C["gold_dim"], size=9, family=F_MONO),
                    annotation_position="top left",
                )

            # Quadrant shading — lower-left is the target zone
            fig_sc.add_shape(
                type="rect",
                x0=fdf["binding_score"].min() if len(fdf) else 0,
                x1=dp_cut if len(fdf) > 0 else 0,
                y0=-20, y1=-7.0,
                fillcolor=f"rgba(196,30,58,0.05)",
                line=dict(width=0),
                layer="below",
            )

            fig_sc.update_layout(make_layout(
                height=480,
                xaxis=axis_style(title="DeepPurpose Binding Score (nM)"),
                yaxis=axis_style(title="AutoDock Vina ΔG (kcal/mol)"),
                legend=dict(
                    bgcolor=f"rgba(22,10,13,0.85)",
                    bordercolor=C["border_mid"],
                    borderwidth=1,
                    font=dict(size=10, color=C["ivory_mid"], family=F_MONO),
                    x=0.98, y=0.02, xanchor="right", yanchor="bottom",
                ),
                title=dict(
                    text="Shaded region = strongest candidates (lower-left quadrant)",
                    font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                    x=0, xanchor="left",
                ),
            ))
            st.plotly_chart(fig_sc, use_container_width=True)

        with col_r:
            # Correlation stat card
            corr = fdf[["binding_score", "vina_score"]].corr().iloc[0, 1] if len(fdf) > 1 else 0.0
            corr_color = C["success"] if abs(corr) > 0.3 else C["ivory_lo"]
            st.markdown(
                f"<div style='background:linear-gradient(145deg,{C['bg_card']} 0%,{C['bg_elevated']} 100%);"
                f"border:1px solid {C['border_mid']};border-top:2px solid {corr_color};"
                f"border-radius:3px;padding:18px 20px;margin-bottom:20px;text-align:center'>"
                f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
                f"letter-spacing:0.16em;text-transform:uppercase;margin:0 0 8px 0'>Pearson r<br>ML vs Vina</p>"
                f"<p style='font-family:{F_DISPLAY};font-size:46px;color:{corr_color};"
                f"margin:0;font-weight:600;line-height:1;letter-spacing:0.02em'>{corr:.3f}</p>"
                f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};margin:8px 0 0 0'>"
                f"Correlation coefficient</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
                f"letter-spacing:0.18em;text-transform:uppercase;margin:0 0 12px 0'>"
                f"Classification Breakdown</p>",
                unsafe_allow_html=True,
            )
            for cls, color in cmap.items():
                n = (fdf["_class"] == cls).sum()
                progress_row(cls, n, len(fdf), color)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            info_card(
                "Interpretation",
                "Lower-left quadrant compounds combine high ML-predicted affinity with strong docking energy — "
                "these are the primary repurposing candidates for experimental follow-up.",
                accent=C["gold_dim"],
            )

    else:
        st.warning("⚠  binding_score or vina_score columns not found in data.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — DOCKING
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    section_label("3D Molecular Docking · AutoDock Vina")
    section_heading("Docking Score Distribution", "AutoDock Vina ΔG (kcal/mol) — lower is stronger binding")

    if "vina_score" in fdf.columns:
        col_l, col_r = st.columns([3, 2], gap="large")

        with col_l:
            sdf = fdf.sort_values("vina_score")
            bar_clr = [
                C["gold_hi"]     if v <= -7.5 else
                C["crimson_hi"]  if v <= -7.0 else
                C["crimson_dim"] if v <= -6.0 else
                C["ivory_ghost"]
                for v in sdf["vina_score"]
            ]
            fig_bar = go.Figure(go.Bar(
                x=sdf["vina_score"],
                y=sdf["drug_name"],
                orientation="h",
                marker=dict(
                    color=bar_clr,
                    line=dict(width=0),
                    opacity=0.92,
                ),
                text=sdf["vina_score"].apply(lambda x: f"{x:.2f}"),
                textposition="outside",
                textfont=dict(size=8.5, color=C["ivory_mid"], family=F_MONO),
                hovertemplate="<b>%{y}</b><br>ΔG: %{x:.2f} kcal/mol<extra></extra>",
            ))
            fig_bar.add_vline(
                x=-7.0, line_dash="dot",
                line=dict(color=C["crimson"], width=1.5),
                annotation_text="−7.0",
                annotation_font=dict(color=C["crimson"], size=9, family=F_MONO),
                annotation_position="top right",
            )
            fig_bar.update_layout(make_layout(
                height=max(440, len(sdf) * 24),
                xaxis=axis_style(title="ΔG (kcal/mol)"),
                yaxis=axis_style(
                    tickfont=dict(size=8.5, color=C["ivory_mid"], family=F_MONO),
                    automargin=True,
                ),
                title=dict(
                    text="Gold ≤ −7.5 kcal/mol   ·   Crimson ≤ −7.0 kcal/mol",
                    font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                    x=0, xanchor="left",
                ),
                showlegend=False,
                margin=dict(l=160, r=60, t=48, b=46),
            ))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_r:
            # Score distribution histogram
            fig_hist = go.Figure(go.Histogram(
                x=fdf["vina_score"],
                nbinsx=22,
                marker=dict(
                    color=C["crimson"],
                    line=dict(color=C["bg_base"], width=0.8),
                    opacity=0.82,
                ),
                hovertemplate="ΔG: %{x:.2f}<br>Count: %{y}<extra></extra>",
            ))
            fig_hist.add_vline(
                x=-7.0,
                line=dict(color=C["gold"], width=1.5, dash="dot"),
                annotation_text="−7.0 threshold",
                annotation_font=dict(color=C["gold"], size=9, family=F_MONO),
            )
            fig_hist.update_layout(make_layout(
                height=260,
                xaxis=axis_style(title="ΔG (kcal/mol)"),
                yaxis=axis_style(title="Count"),
                title=dict(
                    text="Vina Score Distribution",
                    font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                    x=0, xanchor="left",
                ),
                margin=dict(l=52, r=24, t=40, b=40),
            ))
            st.plotly_chart(fig_hist, use_container_width=True)

            # Stats block
            st.markdown(
                f"<p style='font-family:{F_MONO};font-size:9px;color:{C['ivory_lo']};"
                f"letter-spacing:0.18em;text-transform:uppercase;margin:4px 0 10px 0'>"
                f"Descriptive Statistics</p>",
                unsafe_allow_html=True,
            )
            stats = fdf["vina_score"].describe()[["min", "25%", "50%", "75%", "max", "mean"]]
            stats_df = stats.rename(index={
                "min": "Min", "25%": "Q1", "50%": "Median",
                "75%": "Q3",  "max": "Max", "mean": "Mean",
            }).to_frame("ΔG (kcal/mol)")
            st.dataframe(
                stats_df.style.format("{:.3f}"),
                use_container_width=True,
                height=252,
            )

            # Color legend
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            color_dot_legend([
                ("≤ −7.5", C["gold_hi"], "Prime binding"),
                ("≤ −7.0", C["crimson_hi"], "Strong hit"),
                ("≤ −6.0", C["crimson_dim"], "Moderate"),
                ("  > −6.0", C["ivory_ghost"], "Weak"),
            ])
    else:
        st.warning("⚠  vina_score column not found.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ADMET
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    section_label("Pharmacokinetic & Safety Profiling")
    section_heading("ADMET Profiling", "Drug-likeness, oral bioavailability, and structural alerts")

    admet_ok = [c for c in ["MW", "LogP", "HBD", "HBA", "TPSA", "RotBonds", "Fsp3", "QED"]
                if c in fdf.columns]

    if not admet_ok:
        st.info("ℹ  Run `12_admet_profiling.py` first to generate ADMET data.")
    else:
        col_l, col_r = st.columns(2, gap="large")

        with col_l:
            # Radar chart — drug-likeness profile
            top8  = fdf.head(8)
            norm  = {"MW": (0, 600), "LogP": (-3, 7), "TPSA": (0, 200),
                     "RotBonds": (0, 15), "QED": (0, 1), "Fsp3": (0, 1)}
            rprops = [p for p in norm if p in top8.columns]
            palette = [
                C["gold_hi"], C["crimson_hi"], C["success"], "#60a5fa",
                "#a78bfa", "#fb923c", "#34d399", C["ivory_mid"],
            ]

            fig_radar = go.Figure()
            for i, (_, row) in enumerate(top8.iterrows()):
                vals = []
                for p in rprops:
                    lo, hi = norm[p]
                    v = float(row[p]) if pd.notna(row.get(p)) else 0.0
                    vals.append(max(0.0, min(1.0, (v - lo) / (hi - lo))))
                vals.append(vals[0])
                color = palette[i % len(palette)]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=rprops + [rprops[0]],
                    name=str(row.get("drug_name", ""))[:22],
                    line=dict(color=color, width=1.8),
                    fill="toself",
                    fillcolor=color,
                    opacity=0.09,
                    hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
                ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor=C["bg_base"],
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        tickfont=dict(color=C["ivory_lo"], size=8.5, family=F_MONO),
                        gridcolor=C["border"],
                        linecolor=C["border"],
                        tickvals=[0.25, 0.5, 0.75, 1.0],
                    ),
                    angularaxis=dict(
                        tickfont=dict(color=C["ivory_mid"], size=11, family=F_MONO),
                        gridcolor=C["border_mid"],
                        linecolor=C["border_hi"],
                    ),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family=f"'{F_MONO}'", color=C["ivory_mid"]),
                height=430,
                title=dict(
                    text="Drug-likeness radar — top 8 by composite rank",
                    font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                    x=0, xanchor="left",
                ),
                legend=dict(
                    font=dict(size=9, color=C["ivory_mid"], family=F_MONO),
                    bgcolor=f"rgba(22,10,13,0.88)",
                    bordercolor=C["border_mid"],
                    borderwidth=1,
                ),
                margin=dict(l=60, r=60, t=48, b=40),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_r:
            # Rule compliance stacked bar
            rules = {
                "Lipinski Ro5":  ("lipinski_ok",  False),
                "Veber (oral)":  ("veber_ok",     False),
                "No PAINS":      ("PAINS_alert",   True),
                "No Alarm-NMR":  ("Alarm_NMR",     True),
                "Drug-like":     ("drug_like",     False),
            }
            n_total = len(fdf)
            labels, passes, fails = [], [], []
            for label, (col, inv) in rules.items():
                if col in fdf.columns:
                    n = int((~fdf[col]).sum()) if inv else int(fdf[col].sum())
                    labels.append(label)
                    passes.append(n)
                    fails.append(n_total - n)

            fig_rules = go.Figure()
            fig_rules.add_trace(go.Bar(
                x=labels, y=passes, name="Pass",
                marker=dict(color=C["success"], line=dict(width=0), opacity=0.85),
                hovertemplate="%{x}: %{y} pass<extra></extra>",
            ))
            fig_rules.add_trace(go.Bar(
                x=labels, y=fails, name="Fail",
                marker=dict(color=C["crimson"], line=dict(width=0), opacity=0.72),
                hovertemplate="%{x}: %{y} fail<extra></extra>",
            ))
            fig_rules.update_layout(make_layout(
                barmode="stack",
                height=270,
                xaxis=axis_style(tickfont=dict(size=10, color=C["ivory_mid"], family=F_MONO)),
                yaxis=axis_style(title="Compounds"),
                title=dict(
                    text="Druggability Rule Compliance",
                    font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                    x=0, xanchor="left",
                ),
                legend=dict(
                    font=dict(size=10, color=C["ivory_mid"], family=F_MONO),
                    bgcolor="rgba(0,0,0,0)",
                    borderwidth=0,
                    orientation="h", x=0.98, xanchor="right", y=1.12,
                ),
                margin=dict(l=52, r=24, t=44, b=44),
            ))
            st.plotly_chart(fig_rules, use_container_width=True)

            # MW vs LogP scatter
            if "MW" in fdf.columns and "LogP" in fdf.columns:
                clrs = [C["gold"] if dl else C["ivory_ghost"] for dl in fdf["drug_like"]]
                fig_mw = go.Figure()
                # Lipinski zone
                fig_mw.add_shape(
                    type="rect", x0=-0.5, x1=5, y0=0, y1=500,
                    fillcolor=f"rgba(196,30,58,0.06)",
                    line=dict(color=C["crimson_dim"], dash="dot", width=1),
                    layer="below",
                )
                fig_mw.add_trace(go.Scatter(
                    x=fdf["LogP"], y=fdf["MW"],
                    mode="markers",
                    marker=dict(
                        size=7,
                        color=clrs,
                        line=dict(width=0.5, color=C["bg_base"]),
                        opacity=0.88,
                    ),
                    text=fdf["drug_name"],
                    hovertemplate="<b>%{text}</b><br>LogP: %{x:.2f}<br>MW: %{y:.1f} Da<extra></extra>",
                ))
                fig_mw.update_layout(make_layout(
                    height=240,
                    xaxis=axis_style(title="LogP"),
                    yaxis=axis_style(title="Molecular Weight (Da)"),
                    title=dict(
                        text="MW vs LogP  ·  Gold = drug-like  ·  Shaded = Lipinski zone",
                        font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                        x=0, xanchor="left",
                    ),
                    showlegend=False,
                    margin=dict(l=52, r=20, t=40, b=40),
                ))
                st.plotly_chart(fig_mw, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — TOP CANDIDATES
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    section_label("Ranked Repurposing Candidates")
    section_heading("Top Candidates", "Ranked by user-weighted composite score (sidebar controls)")

    n_show = st.slider("Show top N compounds", 5, min(30, max(len(fdf), 5)), min(10, len(fdf)))
    top_n  = fdf.head(n_show)

    if "composite_score" in top_n.columns:
        wf = top_n.sort_values("composite_score")

        bar_clr = []
        for _, r in wf.iterrows():
            if r.get("strong_hit") and r.get("drug_like"): bar_clr.append(C["gold_hi"])
            elif r.get("strong_hit"):                       bar_clr.append(C["crimson_hi"])
            elif r.get("drug_like"):                        bar_clr.append(C["success"])
            else:                                           bar_clr.append(C["ivory_ghost"])

        fig_wf = go.Figure(go.Bar(
            x=wf["drug_name"],
            y=wf["composite_score"],
            marker=dict(
                color=bar_clr,
                line=dict(width=0),
                opacity=0.90,
            ),
            text=wf["composite_score"].apply(lambda x: f"{x:.2f}"),
            textposition="outside",
            textfont=dict(size=9, color=C["ivory_mid"], family=F_MONO),
            hovertemplate="<b>%{x}</b><br>Composite: %{y:.2f}<extra></extra>",
        ))
        fig_wf.update_layout(make_layout(
            height=340,
            xaxis=axis_style(
                tickangle=-38,
                tickfont=dict(size=9, color=C["ivory_mid"], family=F_MONO),
            ),
            yaxis=axis_style(title="Composite Score (lower = better)"),
            title=dict(
                text="Composite ranking — weights controlled in sidebar",
                font=dict(size=10, color=C["ivory_lo"], family=F_MONO),
                x=0, xanchor="left",
            ),
            showlegend=False,
            margin=dict(l=52, r=24, t=44, b=80),
        ))
        st.plotly_chart(fig_wf, use_container_width=True)

    # Legend
    color_dot_legend([
        ("Gold",    C["gold_hi"],    "Prime: strong hit + drug-like"),
        ("Crimson", C["crimson_hi"], "Strong hit (Vina ≤ −7.0 + ML top 25%)"),
        ("Green",   C["success"],    "Drug-like (Ro5 + Veber + no alerts)"),
        ("Dim",     C["ivory_ghost"], "Candidate (below threshold)"),
    ])

    # Detailed table
    detail_cols = [c for c in [
        "composite_rank", "drug_name", "binding_score", "vina_score",
        "composite_score", "QED", "LogCmax_est", "MW", "LogP", "TPSA",
        "strong_hit", "drug_like", "smiles",
    ] if c in top_n.columns]

    fmt = {k: v for k, v in {
        "binding_score": "{:.2f}", "vina_score": "{:.2f}", "composite_score": "{:.2f}",
        "QED": "{:.3f}", "LogCmax_est": "{:.2f}", "MW": "{:.1f}",
        "LogP": "{:.2f}", "TPSA": "{:.1f}",
    }.items() if k in detail_cols}

    st.dataframe(
        top_n[detail_cols].style.format(fmt, na_rep="--"),
        use_container_width=True,
        height=400,
    )

    col_dl, _ = st.columns([1, 3])
    with col_dl:
        st.download_button(
            "⬇  Download Top Candidates CSV",
            data=top_n[detail_cols].to_csv(index=False).encode("utf-8"),
            file_name="top_candidates.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — FULL TABLE
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    section_label("Complete Dataset")
    section_heading("Full Results Table", "All filtered compounds — use sidebar controls to narrow")

    default_cols = [c for c in [
        "composite_rank", "drug_name", "binding_score", "vina_score", "composite_score",
        "QED", "MW", "LogP", "TPSA", "RotBonds",
        "lipinski_ok", "veber_ok", "PAINS_alert", "drug_like", "strong_hit",
    ] if c in fdf.columns]

    col_sel, col_srch = st.columns([3, 1], gap="large")
    with col_sel:
        sel_cols = st.multiselect("Columns", list(fdf.columns), default=default_cols)
    with col_srch:
        search = st.text_input("🔍 Drug name search", "")

    view_df = fdf.copy()
    if search:
        view_df = view_df[view_df["drug_name"].str.contains(search, case=False, na=False)]

    display = view_df[sel_cols] if sel_cols else view_df
    st.dataframe(display, use_container_width=True, height=560)
    st.caption(f"Showing {len(view_df):,} of {len(df):,} compounds  ·  source: {source_file}")

    col_dl, _ = st.columns([1, 3])
    with col_dl:
        st.download_button(
            "⬇  Download Full Results CSV",
            data=fdf.to_csv(index=False).encode("utf-8"),
            file_name="drug_repurposing_full_results.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    f"<div style='display:flex;justify-content:space-between;align-items:center;"
    f"padding:4px 0 8px 0;flex-wrap:wrap;gap:8px'>"
    f"<p style='font-family:{F_MONO};font-size:9.5px;color:{C['ivory_lo']};margin:0;"
    f"letter-spacing:0.08em'>"
    f"DeepPurpose MPNN-CNN &ensp;·&ensp; AutoDock Vina 3D Docking &ensp;·&ensp; RDKit ADMET</p>"
    f"<p style='font-family:{F_MONO};font-size:9.5px;color:{C['crimson_dim']};margin:0;"
    f"letter-spacing:0.06em'>"
    f"Computational predictions only — not clinical guidance — requires experimental validation</p>"
    f"</div>",
    unsafe_allow_html=True,
)
