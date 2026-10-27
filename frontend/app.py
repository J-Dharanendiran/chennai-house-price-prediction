from __future__ import annotations

import base64
import html
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests
import streamlit as st

from pdf_report import (
    FEATURE_LABELS,
    build_valuation_pdf,
    feature_display_value,
    format_inr,
    format_indian_number,
    format_prediction_price,
    parse_numeric_price,
)

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ChennaiHomes | Property Estimator",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# ============================================================
# 2. MODEL INPUT OPTIONS
# Keep the model's expected values unchanged.
# ============================================================
AREAS = [
    "Adyar",
    "Anna Nagar",
    "Chrompet",
    "KK Nagar",
    "Karapakkam",
    "T Nagar",
    "Velachery",
]

SALE_CONDITIONS = ["AbNormal", "AdjLand", "Family", "Normal Sale", "Partial"]
PARKING_OPTIONS = ["No", "Yes"]
BUILDING_TYPES = ["Commercial", "House", "Other", "Others"]
UTILITY_OPTIONS = ["AllPub", "ELO", "NoSeWa", "NoSewr"]
STREET_TYPES = ["Gravel", "No Access", "Paved"]
ZONE_OPTIONS = ["A", "C", "I", "RH", "RL", "RM"]

# ============================================================
# 3. ASSET HELPERS
# Assets are embedded as data URIs so this also works after deployment.
# Keep the assets/ folder next to app.py when using this project bundle.
# ============================================================
def image_data_uri(path: Path) -> str | None:
    """Return a base64 data URI for a local image, or None if it is absent."""
    try:
        content = path.read_bytes()
    except OSError:
        return None

    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(content).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


HERO_IMAGE_URI = image_data_uri(ASSET_DIR / "coastal_city.jpeg")
MAP_IMAGE_URI = image_data_uri(ASSET_DIR / "chennai_vintage_map.jpeg")


# ============================================================
# 4. FORMATTING / API HELPERS
# ============================================================
def api_error_message(response: requests.Response) -> str:
    """Extract a readable error from a FastAPI response."""
    try:
        body = response.json()
        detail = body.get("detail", response.text) if isinstance(body, dict) else body

        if isinstance(detail, dict):
            return str(detail)
        if isinstance(detail, list):
            messages: list[str] = []
            for item in detail:
                if isinstance(item, dict):
                    location = item.get("loc", [])
                    message = item.get("msg", "Invalid input")
                    messages.append(f"{location}: {message}")
                else:
                    messages.append(str(item))
            return "; ".join(messages)
        return str(detail)
    except (ValueError, AttributeError):
        return response.text or "Unknown API error."


def feature_tiles_html(features: dict[str, Any]) -> str:
    """Build escaped HTML showing every submitted feature and value."""
    tiles: list[str] = []
    for key, label in FEATURE_LABELS:
        if key not in features:
            continue
        display_value = feature_display_value(key, features[key])
        tiles.append(
            '<div class="ch-feature-tile">'
            f'<div class="ch-feature-label">{html.escape(label)}</div>'
            f'<div class="ch-feature-value">{html.escape(display_value)}</div>'
            '</div>'
        )
    return "".join(tiles)


# ============================================================
# 5. CUSTOM DESIGN SYSTEM
# ============================================================
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --ch-ink: #202d2b;
  --ch-muted: #687673;
  --ch-green: #1f5b4d;
  --ch-green-dark: #173e36;
  --ch-mint: #e8f0e9;
  --ch-sand: #f5f1e8;
  --ch-paper: #fcfbf8;
  --ch-border: #e4e7df;
  --ch-gold: #c49b5b;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--ch-paper); color: var(--ch-ink); }
[data-testid="stHeader"] { background: rgba(252,251,248,.92); }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { max-width: 1200px; padding-top: 1.2rem; padding-bottom: 3.5rem; }
#MainMenu, footer { visibility: hidden; }

/* Sidebar stays purposeful and quiet. */
[data-testid="stSidebar"] { background: #173e36; }
[data-testid="stSidebar"] * { color: #f7f5ed; }
[data-testid="stSidebar"] input { color: #20302d !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #dce6df; }
[data-testid="stSidebar"] button { border-radius: 10px; }

/* Brand navigation */
.ch-navbar { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.35rem 0 1.2rem; margin-bottom:.45rem; }
.ch-brand { display:flex; align-items:center; gap:.75rem; text-decoration:none; color:var(--ch-ink); min-width:0; }
.ch-brand-mark { display:flex; align-items:center; justify-content:center; width:44px; height:44px; border-radius:14px; background:var(--ch-green); color:white; font:800 1rem 'Manrope',sans-serif; letter-spacing:-.06em; flex:0 0 auto; }
.ch-brand-name { display:block; font:800 1.06rem 'Manrope',sans-serif; letter-spacing:-.035em; color:var(--ch-ink); line-height:1.2; }
.ch-brand-sub { display:block; color:#74817c; font-size:.61rem; font-weight:700; letter-spacing:.16em; margin-top:.22rem; }
.ch-nav-links { display:flex; gap:1.3rem; align-items:center; }
.ch-nav-links a { color:#56635f; font-weight:600; font-size:.86rem; text-decoration:none; }
.ch-nav-links a:hover { color:var(--ch-green); }
.ch-nav-tag { border:1px solid #dce3db; color:var(--ch-green); border-radius:999px; padding:.55rem .85rem; font-size:.72rem; font-weight:700; letter-spacing:.08em; white-space:nowrap; }

/* Hero */
.ch-hero { position:relative; overflow:hidden; isolation:isolate; min-height:390px; border-radius:26px; padding:clamp(2rem,5vw,4.2rem); display:flex; flex-direction:column; justify-content:center; box-sizing:border-box; margin-bottom:1rem; color:#fff; background-color:#183d38; background-image:linear-gradient(90deg,rgba(14,43,39,.94) 0%,rgba(19,53,48,.82) 45%,rgba(20,50,46,.28) 100%)HERO_BACKGROUND; background-size:cover; background-position:center 48%; }
.ch-hero-content { max-width:660px; position:relative; z-index:1; }
.ch-hero-badge { display:inline-flex; align-items:center; gap:.55rem; color:#f3e8d4; font-size:.71rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; margin-bottom:1.4rem; }
.ch-hero-dot { width:7px; height:7px; border-radius:50%; background:#d5b77d; display:inline-block; }
.ch-hero h1 { color:#fff; font:800 clamp(2.3rem,5.5vw,4.45rem)/1.05 'Manrope',sans-serif; letter-spacing:-.065em; max-width:720px; margin:0 0 1.25rem; }
.ch-hero h1 span { color:#d9c396; }
.ch-hero p { color:#e2e9e4; font-size:1.02rem; line-height:1.8; max-width:560px; margin:0 0 1.7rem; }
.ch-hero-cta { display:inline-block; padding:.85rem 1.15rem; border-radius:11px; color:#183d36; background:#f4efe3; font-size:.91rem; font-weight:800; text-decoration:none; }
.ch-hero-cta:hover { background:#fff; }
.ch-hero-footnote { color:#d1ddd5; font-size:.76rem; margin-top:1.15rem; }

/* Trust/process strip */
.ch-process { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; padding:1.1rem 0 2.8rem; }
.ch-process-item { display:flex; align-items:center; gap:.75rem; padding:.9rem 1rem; border:1px solid var(--ch-border); border-radius:14px; background:rgba(255,255,255,.58); min-width:0; }
.ch-process-num { display:flex; flex:0 0 auto; align-items:center; justify-content:center; width:34px; height:34px; border-radius:11px; background:var(--ch-mint); color:var(--ch-green); font:800 .8rem 'Manrope',sans-serif; }
.ch-process-title { font-weight:800; color:var(--ch-ink); font-size:.87rem; }
.ch-process-caption { color:var(--ch-muted); font-size:.75rem; margin-top:.15rem; }

/* Section headings and form */
.ch-section-kicker { color:#8f784f; font-size:.7rem; font-weight:800; letter-spacing:.17em; text-transform:uppercase; margin-bottom:.55rem; }
.ch-section-title { color:var(--ch-ink); font:800 clamp(1.65rem,3vw,2.25rem)/1.2 'Manrope',sans-serif; letter-spacing:-.045em; margin:0 0 .65rem; }
.ch-section-copy { color:var(--ch-muted); font-size:.96rem; line-height:1.75; max-width:720px; margin:0 0 1.4rem; }
.ch-group-title { color:var(--ch-green-dark); font:800 1.05rem 'Manrope',sans-serif; letter-spacing:-.02em; margin:.1rem 0 .35rem; }
.ch-group-caption { color:var(--ch-muted); font-size:.84rem; line-height:1.65; margin-bottom:1rem; }
div[data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--ch-border); border-radius:18px; background:#fff; }
[data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p { color:#344640 !important; font-size:.86rem !important; font-weight:700 !important; }
[data-baseweb="select"] > div, [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input { border-radius:10px; }
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input { min-height:43px; }
[data-baseweb="select"] > div { min-height:43px; }
div[data-testid="stFormSubmitButton"] button { min-height:3.25rem; border:0; border-radius:12px; background:var(--ch-green); color:#fff; font-weight:800; font-size:.96rem; transition:background .15s ease; }
div[data-testid="stFormSubmitButton"] button:hover { background:#174638; color:#fff; }
.stButton button { border-radius:10px; }

/* Result area */
.ch-result-card { position:relative; overflow:hidden; border-radius:22px; border:1px solid #dbe5dc; background:linear-gradient(120deg,#fff 0%,#f0f5ee 100%); padding:clamp(1.35rem,4vw,2.35rem); margin:.75rem 0 1.2rem; }
.ch-result-card:after { content:""; position:absolute; width:180px; height:180px; border-radius:50%; border:1px solid rgba(31,91,77,.12); right:-52px; top:-65px; box-shadow:0 0 0 22px rgba(31,91,77,.035),0 0 0 44px rgba(31,91,77,.025); pointer-events:none; }
.ch-result-top { position:relative; z-index:1; display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.ch-result-label { color:#687872; font-size:.73rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; }
.ch-status-pill { border:1px solid #d4e3d4; background:#f7fbf6; color:#2d6b4e; border-radius:999px; padding:.42rem .7rem; font-size:.72rem; font-weight:700; }
.ch-result-price { position:relative; z-index:1; color:#173e36; font:800 clamp(2.3rem,6vw,4rem)/1.15 'Manrope',sans-serif; letter-spacing:-.065em; overflow-wrap:anywhere; margin:1rem 0 .85rem; }
.ch-result-note { position:relative; z-index:1; color:var(--ch-muted); font-size:.87rem; line-height:1.75; max-width:750px; margin:0; }
.ch-metric-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin:1rem 0 1.6rem; }
.ch-metric-card { background:white; border:1px solid var(--ch-border); border-radius:15px; padding:1rem 1.1rem; min-width:0; }
.ch-metric-label { color:#75817c; font-size:.76rem; margin-bottom:.5rem; }
.ch-metric-value { color:#203d35; font:800 1.14rem 'Manrope',sans-serif; overflow-wrap:anywhere; }
.ch-subsection-title { color:var(--ch-ink); font:800 1.1rem 'Manrope',sans-serif; margin:1.5rem 0 .3rem; }
.ch-subsection-copy { color:var(--ch-muted); font-size:.84rem; line-height:1.7; margin:0 0 1rem; }
.ch-feature-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.7rem; margin:.8rem 0 1.2rem; }
.ch-feature-tile { background:#fff; border:1px solid var(--ch-border); border-radius:13px; padding:.9rem 1rem; min-width:0; }
.ch-feature-label { color:#76827c; font-size:.76rem; margin-bottom:.38rem; }
.ch-feature-value { color:#263d35; font-size:.92rem; font-weight:800; line-height:1.45; overflow-wrap:anywhere; }
.ch-notice { border-left:3px solid #c4a36d; border-radius:0 10px 10px 0; background:#f7f2e8; color:#61553e; padding:1rem 1.1rem; font-size:.83rem; line-height:1.7; margin:1rem 0; }
.ch-empty-state { border:1px dashed #d4ddd3; border-radius:18px; background:rgba(255,255,255,.62); padding:1.7rem; margin:.8rem 0 1rem; }
.ch-empty-icon { width:42px; height:42px; display:flex; align-items:center; justify-content:center; background:#e8f0e9; color:var(--ch-green); border-radius:13px; font-size:1.2rem; margin-bottom:.9rem; }
.ch-empty-title { color:var(--ch-ink); font:800 1.05rem 'Manrope',sans-serif; margin-bottom:.4rem; }
.ch-empty-copy { color:var(--ch-muted); font-size:.88rem; line-height:1.7; margin:0; }

/* Chennai editorial section */
.ch-city-story { display:grid; grid-template-columns:minmax(240px,.78fr) minmax(0,1.22fr); align-items:center; gap:clamp(1.5rem,5vw,4rem); padding:1.35rem; margin-top:2.5rem; border-radius:22px; background:#f1eee4; border:1px solid #e6e1d4; }
.ch-city-map-wrap { display:flex; justify-content:center; align-items:center; min-width:0; }
.ch-city-map { display:block; width:100%; max-width:340px; max-height:485px; object-fit:contain; border-radius:9px; box-shadow:0 12px 28px rgba(52,51,42,.11); }
.ch-city-story-copy { padding:1rem .5rem 1rem 0; }
.ch-city-story-copy h2 { color:#243b34; font:800 clamp(1.5rem,3vw,2.2rem)/1.2 'Manrope',sans-serif; letter-spacing:-.045em; margin:.3rem 0 .9rem; }
.ch-city-story-copy p { color:#65716b; font-size:.92rem; line-height:1.85; }
.ch-city-tag { display:inline-block; padding:.42rem .7rem; border:1px solid #d3d8c9; border-radius:999px; color:#53624f; font-size:.7rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.ch-footer { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:.8rem; border-top:1px solid var(--ch-border); color:#7c8882; font-size:.77rem; padding-top:1.35rem; margin-top:2.5rem; }
.ch-footer strong { color:#46564f; }

@media (max-width: 760px) {
  .block-container { padding-top:.65rem; }
  .ch-nav-links { display:none; }
  .ch-nav-tag { font-size:.62rem; padding:.45rem .55rem; }
  .ch-hero { min-height:420px; border-radius:20px; padding:1.6rem; background-position:57% center; }
  .ch-hero h1 { font-size:clamp(2.15rem,9vw,3rem); }
  .ch-process { grid-template-columns:1fr; padding-bottom:2.1rem; }
  .ch-metric-grid { grid-template-columns:1fr; }
  .ch-feature-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .ch-city-story { grid-template-columns:1fr; padding:1rem; }
  .ch-city-map { max-height:420px; }
  .ch-city-story-copy { padding:.2rem .3rem .5rem; }
  .ch-footer { flex-direction:column; align-items:flex-start; }
}
@media (max-width: 420px) {
  .ch-brand-sub { letter-spacing:.09em; font-size:.54rem; }
  .ch-feature-grid { grid-template-columns:1fr; }
  .ch-result-price { letter-spacing:-.045em; }
}
</style>
""".replace("HERO_BACKGROUND", f', url("{HERO_IMAGE_URI}")' if HERO_IMAGE_URI else ""))


# ============================================================
# 6. SESSION STATE
# ============================================================
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None
if "prediction_error" not in st.session_state:
    st.session_state.prediction_error = None
if "last_features" not in st.session_state:
    st.session_state.last_features = None
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL


# ============================================================
# 7. SIDEBAR / API CONNECTION
# ============================================================
with st.sidebar:
    st.markdown("## 🏡 ChennaiHomes")
    st.caption("Property estimation workspace")
    st.divider()
    st.markdown("### Backend connection")

    api_url_input = st.text_input(
        "FastAPI base URL",
        value=st.session_state.api_url,
        help="Example: http://127.0.0.1:8000",
    ).strip().rstrip("/")
    st.session_state.api_url = api_url_input

    if st.button("Check API connection", use_container_width=True):
        if not api_url_input:
            st.error("Enter the FastAPI base URL first.")
        else:
            try:
                response = requests.get(f"{api_url_input}/", timeout=5)
                response.raise_for_status()
                try:
                    body = response.json()
                    message = body.get("message", "FastAPI is responding.") if isinstance(body, dict) else "FastAPI is responding."
                except ValueError:
                    message = "FastAPI is responding."
                st.success(message)
            except requests.RequestException:
                st.error("Cannot reach FastAPI. Confirm that the backend is running and the URL is correct.")

    st.divider()
    st.markdown("### Estimation flow")
    st.markdown(
        "1. Enter property details.\n2. Send the features to FastAPI.\n3. Review the model's estimated sale price."
    )
    st.caption("This interface uses the existing API. It does not retrain or modify your model.")


# ============================================================
# 8. BRAND NAVIGATION + HERO
# ============================================================
st.html(
    """
<div class="ch-navbar" id="top">
  <a class="ch-brand" href="#top" aria-label="ChennaiHomes home">
    <span class="ch-brand-mark">CH</span>
    <span>
      <span class="ch-brand-name">ChennaiHomes</span>
      <span class="ch-brand-sub">PROPERTY INTELLIGENCE</span>
    </span>
  </a>
  <nav class="ch-nav-links" aria-label="Main navigation">
    <a href="#estimate">Estimate price</a>
    <a href="#how-it-works">How it works</a>
    <a href="#chennai">Chennai</a>
  </nav>
  <span class="ch-nav-tag">CHENNAI · TAMIL NADU</span>
</div>
<div class="ch-hero">
  <div class="ch-hero-content">
    <div class="ch-hero-badge"><span class="ch-hero-dot"></span> Chennai property estimator</div>
    <h1>A clearer view of your home's <span>estimated value.</span></h1>
    <p>Explore a machine-learning estimate based on the property details you provide. Thoughtfully designed for a simpler, clearer house-price estimation experience.</p>
    <a class="ch-hero-cta" href="#estimate">Estimate a property <span aria-hidden="true">↗</span></a>
    <div class="ch-hero-footnote">An automated estimate based on the model and data behind this project.</div>
  </div>
</div>
<div class="ch-process" id="how-it-works">
  <div class="ch-process-item"><span class="ch-process-num">01</span><div><div class="ch-process-title">Describe the property</div><div class="ch-process-caption">Location, size and characteristics</div></div></div>
  <div class="ch-process-item"><span class="ch-process-num">02</span><div><div class="ch-process-title">Run the estimate</div><div class="ch-process-caption">Your details go to the existing API</div></div></div>
  <div class="ch-process-item"><span class="ch-process-num">03</span><div><div class="ch-process-title">Review the result</div><div class="ch-process-caption">See the estimate and every input</div></div></div>
</div>
"""
)


# ============================================================
# 9. PROPERTY FORM
# ============================================================
st.html(
    """
<div id="estimate" class="ch-section-kicker">01 / Property profile</div>
<div class="ch-section-title">Tell us about the property</div>
<div class="ch-section-copy">Enter the details below to generate an estimate. Labels are written for people; the underlying feature names sent to the model remain unchanged.</div>
"""
)

with st.form("house_prediction_form", clear_on_submit=False):
    with st.container(border=True):
        st.html(
            """
<div class="ch-group-title">⌖ Location &amp; space</div>
<div class="ch-group-caption">Start with the property's neighbourhood, built-up area and room configuration.</div>
"""
        )
        area = st.selectbox("Property location", AREAS, index=AREAS.index("Chrompet"), help="Choose from the locations available in the model's current input options.")

        size_col, room_col = st.columns(2)
        with size_col:
            int_sqft = st.number_input("Built-up area (sq. ft.)", min_value=1, max_value=100000, value=1000, step=50)
        with room_col:
            n_room = st.number_input("Total rooms", min_value=1, max_value=100, value=4, step=1)

        bed_col, bath_col = st.columns(2)
        with bed_col:
            n_bedroom = st.number_input("Bedrooms", min_value=0, max_value=50, value=2, step=1)
        with bath_col:
            n_bathroom = st.number_input("Bathrooms", min_value=0, max_value=50, value=2, step=1)

    with st.container(border=True):
        st.html(
            """
<div class="ch-group-title">⌂ Building &amp; surroundings</div>
<div class="ch-group-caption">Choose the values that best match the property's building type, access and facilities.</div>
"""
        )
        building_col, sale_col = st.columns(2)
        with building_col:
            buildtype = st.selectbox("Building type", BUILDING_TYPES, index=BUILDING_TYPES.index("House"))
        with sale_col:
            sale_cond = st.selectbox("Sale condition", SALE_CONDITIONS, index=SALE_CONDITIONS.index("Normal Sale"))

        park_col, utility_col = st.columns(2)
        with park_col:
            park_facil = st.selectbox("Parking facility", PARKING_OPTIONS, index=PARKING_OPTIONS.index("Yes"))
        with utility_col:
            utility_avail = st.selectbox("Utility availability (dataset value)", UTILITY_OPTIONS, index=UTILITY_OPTIONS.index("AllPub"), help="The dropdown preserves the category values expected by the trained model.")

        street_col, zone_col = st.columns(2)
        with street_col:
            street = st.selectbox("Street access", STREET_TYPES, index=STREET_TYPES.index("Paved"))
        with zone_col:
            mzzone = st.selectbox("Zone code (MZ zone)", ZONE_OPTIONS, index=ZONE_OPTIONS.index("RL"), help="This is the category code used by the training dataset.")

    with st.container(border=True):
        st.html(
            """
<div class="ch-group-title">✦ Quality &amp; sale details</div>
<div class="ch-group-caption">These fields are included because the existing model expects them as input features.</div>
"""
        )
        quality_col, commission_col = st.columns(2)
        with quality_col:
            qs_overall = st.number_input("Overall quality score", min_value=0.0, max_value=5.0, value=3.0, step=0.5, help="Confirm that this input range matches the training data and model documentation.")
        with commission_col:
            commission = st.number_input("Commission (₹)", min_value=0, value=100000, step=10000, format="%d", help="Enter the commission in the same units used in the source dataset.")

    st.write("")
    submitted = st.form_submit_button("Estimate property value  →", type="primary", use_container_width=True)


# ============================================================
# 10. SEND REQUEST TO FASTAPI
# Keep the endpoint and JSON schema the same as the supplied code.
# ============================================================
if submitted:
    st.session_state.prediction_result = None
    st.session_state.prediction_error = None

    if not st.session_state.api_url:
        st.session_state.prediction_error = "Enter the FastAPI base URL in the sidebar."
    else:
        features = {
            "AREA": area,
            "INT_SQFT": float(int_sqft),
            "N_BEDROOM": float(n_bedroom),
            "N_BATHROOM": float(n_bathroom),
            "N_ROOM": float(n_room),
            "SALE_COND": sale_cond,
            "PARK_FACIL": park_facil,
            "BUILDTYPE": buildtype,
            "UTILITY_AVAIL": utility_avail,
            "STREET": street,
            "MZZONE": mzzone,
            "QS_OVERALL": float(qs_overall),
            "COMMIS": float(commission),
        }
        st.session_state.last_features = features

        with st.spinner("Estimating your property's value…"):
            try:
                response = requests.post(
                    f"{st.session_state.api_url}/predict",
                    json={"features": features},
                    timeout=45,
                )
                if response.ok:
                    result = response.json()
                    if not isinstance(result, dict) or "predicted_price" not in result:
                        st.session_state.prediction_error = "The API response did not contain a predicted_price field."
                    else:
                        st.session_state.prediction_result = result
                else:
                    st.session_state.prediction_error = f"HTTP {response.status_code}: {api_error_message(response)}"
            except requests.Timeout:
                st.session_state.prediction_error = "The API request timed out. Check that the backend is running and responsive."
            except requests.ConnectionError:
                st.session_state.prediction_error = "Could not connect to FastAPI. Check the URL and make sure the backend is running."
            except requests.RequestException as exc:
                st.session_state.prediction_error = f"The request failed: {exc}"
            except ValueError:
                st.session_state.prediction_error = "The API did not return valid JSON."


# ============================================================
# 11. PREDICTION SUMMARY
# ============================================================
st.write("")
st.html(
    """
<div class="ch-section-kicker">02 / Your estimate</div>
<div class="ch-section-title">Property valuation summary</div>
<div class="ch-section-copy">Review the model-generated estimate and the exact feature values used for this request.</div>
"""
)

result = st.session_state.prediction_result
error = st.session_state.prediction_error
features = st.session_state.last_features

if result:
    raw_price = result["predicted_price"]
    currency = str(result.get("currency", "INR"))
    price_display, numeric_price = format_prediction_price(raw_price, currency)

    st.html(
        f"""
<div class="ch-result-card">
  <div class="ch-result-top">
    <div class="ch-result-label">Estimated sale price</div>
    <div class="ch-status-pill">✓ Estimate generated</div>
  </div>
  <div class="ch-result-price">{price_display}</div>
  <p class="ch-result-note">This is a model-generated estimate based on the information submitted. It is not a formal property valuation or a guaranteed selling price.</p>
</div>
"""
    )

    if features:
        metric_tiles = [
            ("Property location", str(features.get("AREA", "—"))),
            ("Built-up area", f"{format_indian_number(features['INT_SQFT'])} sq. ft."),
        ]
        if numeric_price is not None and numeric_price >= 0 and float(features.get("INT_SQFT", 0)) > 0:
            per_sqft = numeric_price / float(features["INT_SQFT"])
            metric_tiles.append(("Estimated price per sq. ft.", format_inr(per_sqft)))
        else:
            metric_tiles.append(("Bedrooms", format_indian_number(features.get("N_BEDROOM", 0))))

        metrics_html = "".join(
            '<div class="ch-metric-card">'
            f'<div class="ch-metric-label">{html.escape(label)}</div>'
            f'<div class="ch-metric-value">{html.escape(value)}</div>'
            '</div>'
            for label, value in metric_tiles
        )
        st.html(f'<div class="ch-metric-grid">{metrics_html}</div>')

        st.html(
            """
<div class="ch-subsection-title">Property details used for this estimate</div>
<div class="ch-subsection-copy">Every item below shows the feature name in plain language and the value submitted to the model.</div>
"""
        )
        st.html(f'<div class="ch-feature-grid">{feature_tiles_html(features)}</div>')

        # Offer a simple downloadable CSV summary without extra dependencies.
        csv_rows = ["Feature,Value"]
        for key, label in FEATURE_LABELS:
            if key in features:
                value = str(features[key]).replace('"', '""')
                csv_rows.append(f'"{label}","{value}"')
        value_for_csv = "\n".join(csv_rows)
        st.download_button(
            "Download submitted features (CSV)",
            data=value_for_csv,
            file_name="chennaihomes_property_features.csv",
            mime="text/csv",
            use_container_width=False,
        )

        try:
            pdf_report = build_valuation_pdf(features, raw_price, currency, numeric_price)
            st.download_button(
                "Download property valuation report (PDF)",
                data=pdf_report,
                file_name="ChennaiHomes_Property_Valuation_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=False,
                help="Download the estimate, all 13 submitted features, price per square foot when available, and the valuation disclaimer.",
            )
        except Exception as exc:
            st.error(f"Could not generate the PDF report: {exc}")

elif error:
    st.error(error)
    st.html(
        """
<div class="ch-notice"><strong>What to check:</strong> confirm that FastAPI is running, that the base URL is correct, and that the feature names and category values still match the saved model's expected schema.</div>
"""
    )
else:
    st.html(
        """
<div class="ch-empty-state">
  <div class="ch-empty-icon">⌂</div>
  <div class="ch-empty-title">Your estimate will appear here</div>
  <p class="ch-empty-copy">Complete the property form above and choose <strong>Estimate property value</strong>. The result section will show the estimated price, price per square foot when available, and every submitted feature by name.</p>
</div>
<div class="ch-notice"><strong>A note on estimates:</strong> the result depends on the model, its training data and the details supplied. It should not be treated as a professional valuation or a current market quote.</div>
"""
    )


# ============================================================
# 12. CHENNAI EDITORIAL SECTION
# The supplied coastal photo is used in the hero; this map is shown below.
# ============================================================
map_img_tag = (
    f'<img class="ch-city-map" src="{MAP_IMAGE_URI}" alt="Vintage-style illustrated map poster labelled Chennai, India">'
    if MAP_IMAGE_URI
    else '<div class="ch-notice">Add the supplied Chennai map image to the assets folder to display it here.</div>'
)

st.html(
    f"""
<div class="ch-city-story" id="chennai">
  <div class="ch-city-map-wrap">{map_img_tag}</div>
  <div class="ch-city-story-copy">
    <span class="ch-city-tag">Made for the Chennai context</span>
    <h2>Local details matter.</h2>
    <p>Property prices can vary with location, size, building characteristics and other factors represented in the training data. ChennaiHomes brings the inputs together in one clear place, then sends them to the existing prediction API.</p>
    <p>The locations and categories available in the form are the options currently configured for this project. They should not be interpreted as a complete list of every neighbourhood in Chennai.</p>
  </div>
</div>
<div class="ch-footer">
  <div><strong>ChennaiHomes</strong> · Machine-learning property estimate</div>
  <div>Built with Streamlit + FastAPI · For informational use</div>
</div>
"""
)
