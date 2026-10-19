import base64
import hashlib
from html import escape
from pathlib import Path
import sys

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.utils.uploads import (
    image_request_files,
    leaf_request_files,
)
from backend.utils.config import (
    API_URL,
    MODEL_NAME,
)


def choose_crop(crop):
    st.session_state.selected_crop = crop


st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="wide",
)

hero_image = PROJECT_ROOT / "frontend" / "assets" / "plantvision-hero.jpg"
hero_image_data = base64.b64encode(hero_image.read_bytes()).decode("ascii")
botanical_art = PROJECT_ROOT / "frontend" / "assets" / "landing-botanical.svg"
botanical_art_data = base64.b64encode(botanical_art.read_bytes()).decode("ascii")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --forest: #14532d;
        --leaf: #16a34a;
        --ink: #0d1c12;
        --muted: #34493a;
        --line: #dce5dc;
        --surface: #fffefa;
        --wash: #f6f7f1;
        --pv-hero-photo: url("data:image/jpeg;base64,__HERO_IMAGE__");
        --pv-botanical-art: url("data:image/svg+xml;base64,__BOTANICAL_ART__");
    }
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }
    [data-testid="stAppViewContainer"] { color: var(--ink); }
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], label { color: var(--ink); }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(155deg, #f2f4ed 0%, #f7f7f1 48%, #edf2e9 100%);
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }
    .project-masthead {
        width: 100vw;
        margin-top: -2.2rem;
        margin-bottom: 0;
        margin-left: calc(50% - 50vw);
        font-family: Arial, "Segoe UI", sans-serif;
    }
    .site-nav {
        min-height: 56px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        margin-top: 44px;
        padding: .55rem max(calc((100vw - 1240px) / 2), 4vw);
        border-bottom: 1px solid #e5dfca;
        background: #fbf7eb;
        color: #172d1b;
    }
    .site-nav-brand {
        display: inline-flex;
        align-items: center;
        gap: .6rem;
        color: #18351f !important;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.45rem;
        font-weight: 700;
        text-decoration: none !important;
        white-space: nowrap;
    }
    .site-nav-brand svg { width: 1.8rem; height: 1.8rem; }
    .site-nav-links { display: flex; align-items: center; gap: clamp(.8rem, 2.5vw, 2.2rem); }
    .site-nav-links a {
        color: #24382a !important;
        font-size: .83rem;
        font-weight: 600;
        text-decoration: none !important;
        white-space: nowrap;
    }
    .site-nav-links a:hover { color: #14532d !important; }
    .site-nav-links .site-nav-cta {
        padding: .65rem 1.25rem;
        border: 1px solid #163f21;
        border-radius: 9px;
        background: #194b26;
        color: #fffdf2 !important;
    }
    .site-nav-links .site-nav-cta:hover { color: #fffdf2 !important; }
    .project-hero {
        position: relative;
        overflow: hidden;
        display: flex;
        min-height: clamp(330px, 23vw, 390px);
        align-items: center;
        padding: 2.6rem max(calc((100vw - 1240px) / 2), 4vw);
        margin: 0;
        background-image: linear-gradient(90deg, rgba(10, 31, 15, .88) 0%, rgba(13, 40, 19, .73) 37%, rgba(17, 46, 23, .12) 74%), var(--pv-hero-photo);
        background-position: center 56%;
        background-size: cover;
        box-shadow: 0 8px 24px rgba(26, 49, 27, .12);
    }
    .project-hero:after {
        content: none;
    }
    .hero-copy {
        position: relative;
        z-index: 1;
        max-width: 550px;
        margin: .85rem 0 0;
        color: #f3f1e8;
        font-size: 1rem;
        line-height: 1.65;
    }
    .hero-project-name {
        margin: 0 0 .45rem;
        color: #f4edc8;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.35rem, 2vw, 1.8rem);
        font-weight: 700;
        letter-spacing: .015em;
        text-shadow: 0 2px 12px rgba(0, 0, 0, .35);
    }
    .hero-content { position: relative; z-index: 1; max-width: 700px; font-family: Arial, "Segoe UI", sans-serif; }
    .hero-title {
        max-width: 690px;
        color: #fffdf2;
        font-family: Georgia, 'Times New Roman', serif;
        margin: 0;
        font-size: clamp(2.8rem, 5vw, 4rem);
        font-weight: 700;
        letter-spacing: -.045em;
        line-height: .99;
        text-wrap: balance;
    }
    .stApp .hero-title,
    .stApp .hero-title [data-heading-text] {
        color: #fffdf2 !important;
        font-family: Georgia, "Times New Roman", serif !important;
    }
    .hero-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem; margin-top: 1.5rem; }
    .hero-cta, .hero-secondary {
        display: inline-flex;
        min-height: 2.9rem;
        align-items: center;
        justify-content: center;
        gap: .65rem;
        padding: .7rem 1.15rem;
        border-radius: 10px;
        font-size: .92rem;
        font-weight: 700;
        text-decoration: none !important;
        transition: transform .15s ease, background .15s ease, box-shadow .15s ease;
    }
    .hero-cta { border: 1px solid #f4edcd; background: #f3edcf; color: #173821 !important; box-shadow: 0 6px 18px rgba(0,0,0,.14); }
    .hero-secondary { border: 1px solid rgba(255,255,255,.62); background: rgba(15,39,20,.22); color: #fffdf2 !important; }
    .hero-cta:hover, .hero-secondary:hover { transform: translateY(-1px); }
    .hero-cta:focus-visible, .hero-secondary:focus-visible { outline: 3px solid #fff; outline-offset: 3px; }
    .workflow-strip {
        position: relative;
        isolation: isolate;
        margin: .5rem 0 1.5rem;
        padding: 1.3rem 0 2rem;
        border: 0;
        background: transparent;
        box-shadow: none;
        color: #162e1e;
        font-family: Arial, "Segoe UI", sans-serif;
    }
    .workflow-strip:before {
        position: absolute;
        z-index: -1;
        top: 0;
        bottom: 0;
        left: 50%;
        width: 100vw;
        transform: translateX(-50%);
        background-color: #fbf7eb;
        background-image: var(--pv-botanical-art);
        background-position: center bottom;
        background-repeat: no-repeat;
        background-size: 100% auto;
        opacity: .18;
        -webkit-mask-image: linear-gradient(90deg, #000 0%, transparent 26%, transparent 74%, #000 100%);
        mask-image: linear-gradient(90deg, #000 0%, transparent 26%, transparent 74%, #000 100%);
        content: "";
        pointer-events: none;
    }
    .workflow-heading { margin: 0 auto 1.4rem; text-align: center; }
    .workflow-eyebrow, .upload-eyebrow {
        margin: 0 0 .35rem;
        color: #73836c;
        font-size: .7rem;
        font-weight: 800;
        letter-spacing: .17em;
        text-transform: uppercase;
    }
    .workflow-main-title {
        margin: 0;
        color: #183b26 !important;
        font-family: Georgia, 'Times New Roman', serif !important;
        font-size: clamp(1.65rem, 3vw, 2.25rem) !important;
        font-weight: 700;
        letter-spacing: -.03em;
    }
    .workflow-steps { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: clamp(1rem, 3vw, 2.5rem); }
    .workflow-step { position: relative; display: flex; align-items: center; gap: .75rem; min-width: 0; padding: .55rem 0; }
    .workflow-step:not(:last-child):after {
        position: absolute;
        top: 50%;
        right: calc(clamp(1rem, 3vw, 2.5rem) * -.72);
        width: clamp(1.25rem, 2.5vw, 2.4rem);
        height: 1px;
        background: #a5b39a;
        content: "";
    }
    .workflow-number {
        display: grid;
        position: absolute;
        z-index: 1;
        top: .25rem;
        left: .2rem;
        flex: 0 0 2.35rem;
        width: 2.35rem;
        height: 2.35rem;
        place-items: center;
        border: 0;
        border-radius: 50%;
        background: #205229;
        color: #fffdf2;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: .9rem;
        font-weight: 700;
    }
    .workflow-art { display: flex; flex: 0 0 7rem; width: 7rem; height: 7rem; align-items: center; justify-content: center; margin-left: .45rem; }
    .workflow-art svg { display: block; width: 100%; height: auto; }
    .workflow-copy { display: block; min-width: 0; }
    .workflow-title { margin: .08rem 0 .28rem; color: #203f2a !important; font-family: Georgia, 'Times New Roman', serif !important; font-size: 1.35rem !important; font-weight: 700; }
    .workflow-note { margin: 0; color: #303c32; font-size: .85rem; line-height: 1.48; }
    .workflow-intro { margin: .25rem 0 0; color: #3f493c; font-family: Georgia, "Times New Roman", serif; font-size: .96rem; }
    .hero-play { display: inline-grid; width: 1.35rem; height: 1.35rem; place-items: center; border-radius: 50%; background: #f4edcf; color: #18351f; font-size: .62rem; }
    .landing-intro { margin: 0 0 .9rem; text-align: center; font-family: Arial, "Segoe UI", sans-serif; }
    .landing-intro .section-heading {
        margin: .25rem 0 .35rem;
        color: #183b26 !important;
        font-family: Georgia, 'Times New Roman', serif !important;
        font-size: clamp(2rem, 3.2vw, 2.55rem) !important;
        letter-spacing: -.03em;
    }
    .st-key-landing_upload {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        left: 50%;
        z-index: 2;
        width: min(1240px, calc(100vw - 2rem));
        box-sizing: border-box;
        transform: translateX(-50%);
        margin-top: -2rem;
        margin-bottom: 1.7rem;
        padding: 1.25rem clamp(1rem, 4vw, 3.25rem) 1.5rem;
        border: 1px solid #e4dcc4 !important;
        border-radius: 25px !important;
        background-color: #fbf7eb !important;
        background-image: none;
        box-shadow: 0 12px 30px rgba(67, 65, 42, .08);
        color: #18351f;
        font-family: Arial, "Segoe UI", sans-serif;
    }
    .st-key-landing_upload:before {
        position: absolute;
        z-index: 0;
        inset: 0;
        background: var(--pv-botanical-art) center bottom / 100% auto no-repeat;
        content: "";
        opacity: .14;
        -webkit-mask-image: linear-gradient(90deg, #000 0%, transparent 29%, transparent 71%, #000 100%);
        mask-image: linear-gradient(90deg, #000 0%, transparent 29%, transparent 71%, #000 100%);
        pointer-events: none;
    }
    .st-key-landing_upload > * { position: relative; z-index: 1; }
    .st-key-landing_upload [class*="css"] { font-family: Arial, "Segoe UI", sans-serif; }
    .st-key-landing_upload :is(h2, h3) { color: #203b27 !important; font-family: Georgia, "Times New Roman", serif !important; }
    .st-key-landing_upload .landing-intro { margin: .25rem auto 1.1rem; text-align: center; }
    .st-key-landing_upload .landing-intro .section-heading { margin: .25rem 0 .35rem; }
    .st-key-landing_upload .landing-intro .upload-eyebrow { color: #526b38; }
    .st-key-landing_upload .landing-intro .section-description { margin: 0 auto; max-width: 760px; color: #3e493b; }
    .landing-field-title { margin: .2rem 0 .35rem; color: #203b27; font-size: .98rem; font-weight: 700; }
    .landing-field-purpose { margin: -.1rem 0 .45rem; color: #687365; font-size: .76rem; line-height: 1.45; }
    .landing-upload-caption { margin: .5rem 0 .1rem; color: #687365; font-size: .78rem; line-height: 1.45; }
    .st-key-landing_upload [data-testid="stFileUploader"] {
        border-color: #dfd7bf;
        border-radius: 13px;
        background: rgba(255, 253, 246, .92);
        box-shadow: none;
    }
    .st-key-landing_upload [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e4deca;
        border-radius: 12px;
        background: rgba(255, 253, 246, .78);
        box-shadow: none;
    }
    .st-key-select_tomato .stButton > button,
    .st-key-select_potato .stButton > button {
        position: relative;
        display: flex;
        min-height: 7.4rem;
        align-items: flex-end;
        justify-content: center;
        overflow: hidden;
        padding: 4.65rem .65rem .65rem;
        border: 1px solid #c9c4b2 !important;
        border-radius: 12px;
        background: rgba(255, 253, 246, .94) !important;
        color: #17351f !important;
        font-family: Arial, "Segoe UI", sans-serif;
        font-size: .92rem;
        font-weight: 650;
        box-shadow: none !important;
    }
    .st-key-select_tomato .stButton > button:before,
    .st-key-select_potato .stButton > button:before {
        position: absolute;
        top: .45rem;
        left: 50%;
        width: 4.1rem;
        height: 4.1rem;
        transform: translateX(-50%);
        border: 1px solid rgba(99, 104, 65, .12);
        border-radius: 50%;
        background-image: var(--pv-hero-photo);
        background-repeat: no-repeat;
        background-size: auto 235%;
        content: "";
        pointer-events: none;
    }
    .st-key-select_tomato .stButton > button:before { background-position: 65% 68%; }
    .st-key-select_potato .stButton > button:before { background-position: 92% 88%; }
    .st-key-select_tomato .stButton > button[kind="primary"],
    .st-key-select_potato .stButton > button[kind="primary"] {
        border: 1.5px solid #205229 !important;
        background: rgba(241, 244, 226, .97) !important;
        color: #17351f !important;
    }
    .st-key-select_tomato .stButton > button[kind="primary"]:after,
    .st-key-select_potato .stButton > button[kind="primary"]:after {
        position: absolute;
        top: .55rem;
        right: .55rem;
        display: grid;
        width: 1.25rem;
        height: 1.25rem;
        place-items: center;
        border-radius: 50%;
        background: #205229;
        color: #fffdf2;
        content: "✓";
        font-size: .75rem;
        font-weight: 800;
    }
    .section-heading {
        margin: 1.25rem 0 .25rem;
        color: #183d27;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -.02em;
    }
    .section-description { max-width: 78ch; margin: 0 0 1rem; color: #53614f; font-size: .94rem; line-height: 1.65; }
    .st-key-farm_location {
        margin: .5rem 0 1.5rem;
        padding: clamp(1rem, 2vw, 1.5rem);
        border: 1px solid #dedfce;
        border-radius: 20px;
        background: linear-gradient(145deg, #fbfaf3 0%, #f4f6ee 100%);
        box-shadow: 0 10px 26px rgba(44, 56, 37, .055);
    }
    .st-key-farm_location .farm-location-eyebrow {
        margin: 0 0 .25rem;
        color: #627449;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .st-key-farm_location .farm-location-heading {
        margin: 0 0 .35rem;
        color: #183d27;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -.02em;
    }
    .st-key-farm_location .farm-location-description {
        max-width: 78ch;
        margin: 0 0 .8rem;
        color: #53614f;
        font-size: .94rem;
        line-height: 1.65;
    }
    .st-key-farm_location [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid #d7e0d2;
        border-radius: 14px;
        background: #fbfaf4;
        box-shadow: 0 5px 16px rgba(42, 56, 34, .035);
    }
    .st-key-farm_location [data-testid="stExpander"] summary {
        padding: .8rem 1rem;
        background: #edf2e7;
        color: #24442d;
    }
    .st-key-farm_location [data-testid="stExpanderDetails"] {
        padding: .4rem 1rem .85rem;
        background: #fbfaf4;
    }
    .stApp [data-testid="stTextInput"] input:focus,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
        border-color: #718b63 !important;
        box-shadow: 0 0 0 3px rgba(113, 139, 99, .16) !important;
    }
    h2, h3 { font-family: Georgia, "Times New Roman", serif !important; color: #1a3926 !important; }
    h2 { font-size: 1.35rem !important; letter-spacing: -.02em; }
    [data-testid="stFileUploader"] {
        padding: .35rem;
        border: 1px solid #e2dfd2;
        border-radius: 16px;
        background: #fbfaf4;
        box-shadow: 0 5px 18px rgba(44, 53, 35, .04);
    }
    [data-testid="stFileUploader"] section {
        border: 1px dashed #a9b79d !important;
        border-radius: 12px !important;
        background: #f6f5ec !important;
        color: #253d2b !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
        color: #253d2b !important;
    }
    [data-testid="stFileUploader"] button {
        border: 1px solid #bdcbb4 !important;
        border-radius: 9px !important;
        background: #fffef9 !important;
        color: #23412c !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #a9b79d !important;
        border-radius: 12px !important;
        background: #f6f5ec !important;
        color: #253d2b !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #253d2b !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        border: 1px solid #bdcbb4 !important;
        background: #fffef9 !important;
        color: #23412c !important;
    }
    [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid #d4dfd2;
        border-radius: 14px;
        background: #f2f6ef;
        box-shadow: 0 4px 14px rgba(29, 63, 38, .035);
        transition: border-color .18s ease, box-shadow .18s ease;
    }
    [data-testid="stExpander"]:hover {
        border-color: #a9c3aa;
        box-shadow: 0 6px 18px rgba(29, 63, 38, .065);
    }
    [data-testid="stExpander"] summary {
        min-height: 3.2rem;
        padding: .25rem .45rem;
        color: #173b27 !important;
        font-weight: 750;
        cursor: pointer;
    }
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg { color: #173b27 !important; }
    [data-testid="stExpander"] summary svg { transition: transform .18s ease; }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: .35rem 1rem 1rem;
        border-top: 1px solid #dfe8dc;
        background: #fbfcf8;
    }
    .stApp :is(
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stAlert"]
    ),
    .stApp :is(
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stAlert"]
    ) * { cursor: default !important; }
    .stApp :is(
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stAlert"]
    ) :is(a, button, input, select, textarea, label, summary, [role="button"], [role="link"]) {
        cursor: pointer !important;
    }
    .stApp [data-testid="stFileUploader"],
    .stApp [data-testid="stFileUploader"] * { cursor: pointer !important; }
    .stApp :is(
        [data-testid="stHeading"],
        [data-testid="stMetric"],
        [data-testid="stImageCaption"]
    ),
    .stApp :is(
        [data-testid="stHeading"],
        [data-testid="stMetric"],
        [data-testid="stImageCaption"]
    ) * { cursor: default !important; }
    .stApp [data-testid="stHeading"] a { cursor: pointer !important; }
    [data-testid="stImage"] img { border-radius: 14px; }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-color: #cbd8c7;
        border-radius: 10px;
        background: #fffef9;
    }
    [data-testid="stWidgetLabel"] p { color: #294631; font-weight: 650; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #dfe5d9;
        border-radius: 15px;
        background: #fbfaf4;
        box-shadow: 0 6px 18px rgba(39, 54, 36, .045);
    }
    .disease-guide-heading { margin-top: 1.8rem; padding: .35rem 0 .65rem; border-bottom: 1px solid #d8e0d3; font-family: Georgia, "Times New Roman", serif; font-size: 1.65rem; }
    .stApp [data-testid="stHeading"] h1,
    .stApp [data-testid="stHeading"] h2,
    .stApp [data-testid="stHeading"] h3 {
        color: #193b27 !important;
        font-family: Georgia, "Times New Roman", serif !important;
        letter-spacing: -.02em;
    }
    .stApp [data-testid="stAlert"] {
        border: 1px solid #d5e1d1;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(42, 56, 34, .035);
    }
    .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
        border: 1px solid #d5e1d1 !important;
        border-radius: 11px !important;
        background: #eef3e9 !important;
        color: #38533b !important;
    }
    .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) svg {
        color: #537451 !important;
        fill: currentColor;
    }
    .stApp [data-testid="stAlertContentInfo"] {
        border-radius: 11px;
        background: transparent !important;
        color: #38533b;
    }
    .stApp [data-testid="stAlertContentInfo"] [data-testid="stMarkdownContainer"] p {
        color: #38533b !important;
    }
    .result-fact { background: rgba(255, 253, 247, .92); }
    .stApp [data-testid="stImage"] {
        padding: .4rem;
        border: 1px solid #e2dfd0;
        border-radius: 16px;
        background: #fbfaf4;
        box-shadow: 0 6px 18px rgba(42, 56, 34, .06);
    }
    .stApp [data-testid="stImage"] img {
        border: 1px solid #e4e0d2;
        border-radius: 11px;
        box-shadow: none;
    }
    [data-testid="stMetric"] {
        padding: 1rem 1.15rem;
        border: 1px solid var(--line);
        border-radius: 15px;
        background: #fff;
        box-shadow: 0 5px 18px rgba(20, 50, 30, .035);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: #174d2d; font-family: 'Manrope', sans-serif; }
    .stButton > button {
        min-height: 2.85rem;
        border-radius: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:not([kind="primary"]) {
        border: 1px solid #bfd1c2 !important;
        background: #f7faf7 !important;
        color: #173b23 !important;
    }
    .stButton > button[kind="primary"] {
        border: 0;
        background: linear-gradient(100deg, #166534, #15803d);
        box-shadow: 0 7px 16px rgba(22, 101, 52, .18);
        color: #ffffff !important;
    }
    [data-testid="stElementContainer"]:has([data-testid="stHeading"] h3) + [data-testid="stElementContainer"] [data-testid="stButton"] > button[kind="primary"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }
    [style*="background-color: black"], [style*="background: black"],
    [style*="background-color: #000"], [style*="background: #000"],
    [style*="background-color: rgb(0, 0, 0)"], [style*="background: rgb(0, 0, 0)"],
    [style*="background-color: rgba(0, 0, 0"], [style*="background: rgba(0, 0, 0"] {
        color: #ffffff !important;
    }
    [style*="background-color: black"] *, [style*="background: black"] *,
    [style*="background-color: #000"] *, [style*="background: #000"] *,
    [style*="background-color: rgb(0, 0, 0)"] *, [style*="background: rgb(0, 0, 0)"] *,
    [style*="background-color: rgba(0, 0, 0"] *, [style*="background: rgba(0, 0, 0"] * {
        color: #ffffff !important;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 9px 20px rgba(22, 101, 52, .15); }
    [data-testid="stProgress"] > div > div { background-color: #16a34a; }
    [data-testid="stAlert"] { border-radius: 13px; }
    .disease-banner {
        margin: .4rem 0 1rem;
        padding: 1.35rem 1.55rem;
        border: 1px solid #cfe1d1;
        border-radius: 18px;
        background-color: #fbf8ec;
        background-image: linear-gradient(115deg, rgba(255, 254, 250, .97) 0%, rgba(237, 244, 235, .92) 66%, rgba(237, 244, 235, .82) 100%), var(--pv-botanical-art);
        background-position: center, right center;
        background-repeat: no-repeat;
        background-size: cover, min(100%, 900px) auto;
        box-shadow: 0 10px 28px rgba(25, 60, 36, .07);
    }
    .disease-eyebrow { color: #3c6847; font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .disease-title { margin: .3rem 0 .8rem; color: #153b23; font-family: Georgia, "Times New Roman", serif; font-size: clamp(1.65rem, 2.4vw, 2rem); font-weight: 700; letter-spacing: -.025em; }
    .result-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: .7rem; margin-top: 1rem; }
    .result-fact { padding: .8rem .95rem; border: 1px solid #dce9de; border-radius: 13px; background: rgba(255,255,255,.82); }
    .result-fact-label { color: #58705e; font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
    .result-fact-value { margin-top: .18rem; color: #173b23; font-family: 'Manrope', sans-serif; font-size: 1rem; font-weight: 800; overflow-wrap: anywhere; }
    .disease-tags { display: flex; flex-wrap: wrap; gap: .5rem; }
    .disease-tag { padding: .35rem .68rem; border: 1px solid #d3e4d5; border-radius: 999px; background: #fff; color: #294b32; font-size: .8rem; font-weight: 700; }
    .disease-list-item { display: flex; gap: .65rem; align-items: flex-start; margin: .5rem 0; color: #23372a; line-height: 1.55; }
    .disease-list-marker { flex: 0 0 1.35rem; color: #16803d; font-weight: 800; }
    .advisory-panel { margin-top: .9rem; padding: 1.1rem 1.35rem; border-radius: 15px; background: #173b25; color: #ffffff !important; box-shadow: 0 8px 22px rgba(20, 59, 37, .14); }
    .advisory-panel * { color: #ffffff !important; }
    .advisory-heading { margin-bottom: .3rem; font-family: 'Manrope', sans-serif; font-size: 1rem; font-weight: 800; }
    .advisory-copy { margin: 0; line-height: 1.65; }
    .guide-intro {
        margin: .75rem 0 1rem;
        padding: 1rem 1.15rem;
        border: 1px solid #dce5da;
        border-left: 3px solid #719277;
        border-radius: 12px;
        background: rgba(255,254,250,.78);
        color: #34493a;
        line-height: 1.7;
    }
    .result-meaning {
        margin: .7rem 0 1rem;
        padding: .85rem 1rem;
        border-left: 3px solid #78967a;
        background: rgba(255,254,250,.72);
        color: #304436;
        line-height: 1.7;
    }
    .result-meaning h3 {
        margin: 0 0 .35rem;
        color: #173b27 !important;
        font-family: 'Manrope', sans-serif;
        font-size: 1.12rem;
    }
    .field-guide {
        margin: 1rem 0 1.2rem;
        padding: 1.15rem clamp(.9rem, 2vw, 1.35rem);
        border: 1px solid #e4dfcf;
        border-left: 3px solid #819467;
        border-radius: 15px;
        background: #fbf8ed;
        box-shadow: 0 6px 18px rgba(54, 65, 38, .035);
        color: #263f30;
    }
    .field-guide-eyebrow, .action-plan-eyebrow {
        margin: 0 0 .4rem;
        color: #6a806d;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .field-guide-title, .action-plan-title {
        margin: 0;
        color: #173b27;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.25rem, 2vw, 1.55rem);
        font-weight: 800;
        letter-spacing: -.025em;
        line-height: 1.25;
    }
    .field-guide-intro, .action-plan-intro {
        margin: .35rem 0 .7rem;
        color: #566658;
        font-size: .92rem;
        line-height: 1.65;
    }
    .guide-list {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .6rem .75rem;
        margin: .35rem 0 0;
    }
    .guide-list-item {
        display: flex;
        align-items: flex-start;
        gap: .65rem;
        min-width: 0;
        padding: .8rem .2rem;
        border: 0;
        border-top: 1px solid #e5e0d2;
        border-radius: 0;
        background: transparent;
        color: #304436;
        font-size: .91rem;
        line-height: 1.6;
    }
    .guide-entry-copy { min-width: 0; }
    .guide-entry-title {
        display: block;
        margin: 0 0 .18rem;
        color: #294b36;
        font-family: 'Manrope', sans-serif;
        font-size: .97rem;
        font-weight: 750;
        line-height: 1.45;
    }
    .guide-marker {
        display: grid;
        flex: 0 0 1.55rem;
        width: 1.55rem;
        height: 1.55rem;
        place-items: center;
        border: 1px solid #cbd8c7;
        border-radius: 999px;
        background: #f0f2e8;
        color: #44664c;
        font-size: .66rem;
        font-weight: 800;
    }
    .action-plan {
        margin: 1rem 0 1.2rem;
        padding: 1.15rem clamp(.95rem, 2vw, 1.4rem) 1.25rem;
        border: 1px solid #dbe2d2;
        border-left: 3px solid #54784d;
        border-radius: 15px;
        background: #f7f7ee;
        box-shadow: 0 6px 18px rgba(42, 56, 34, .04);
        color: #263f30;
    }
    .management-steps {
        position: relative;
        display: grid;
        gap: 0;
        margin: .5rem 0 0;
    }
    .management-steps:before {
        position: absolute;
        top: .75rem;
        bottom: .75rem;
        left: .75rem;
        width: 1px;
        background: #cbd8c8;
        content: "";
    }
    .management-step {
        display: flex;
        align-items: flex-start;
        gap: .75rem;
        padding: .65rem 0;
        border-top: 1px solid #e4e8df;
        color: #304436;
        line-height: 1.65;
    }
    .management-step:first-child {
        margin-bottom: .35rem;
        padding: .75rem 0;
        border: 1px solid #d9e4d6;
        border-radius: 10px;
        background: #edf3e9;
    }
    .management-step:last-child { padding-bottom: .1rem; }
    .management-step-copy { max-width: 76ch; padding-top: .05rem; }
    .management-step-copy strong { color: #355540; font-weight: 700; }
    .management-step:first-child .management-step-copy { color: #203c2b; font-weight: 550; }
    .management-step:first-child .management-step-copy strong { color: #1d482e; font-weight: 800; }
    .step-number {
        display: grid;
        z-index: 1;
        flex: 0 0 1.5rem;
        width: 1.5rem;
        height: 1.5rem;
        place-items: center;
        border: 1px solid #bed0bd;
        border-radius: 50%;
        background: #edf3e9;
        color: #245438;
        font-family: 'Manrope', sans-serif;
        font-size: .72rem;
        font-weight: 800;
    }
    .management-step:not(:first-child) .step-number {
        flex-basis: 1.35rem;
        width: 1.35rem;
        height: 1.35rem;
        margin: .075rem;
        font-size: .66rem;
    }
    .advisory-section {
        margin: 1rem 0;
        padding: 1.15rem 1.2rem 1.25rem;
        border: 1px solid #e6d8b9;
        border-radius: 16px;
        background: linear-gradient(135deg, #fffdf7, #f7f4e9);
        box-shadow: 0 6px 18px rgba(99, 76, 32, .045);
    }
    .advisory-section-title {
        margin: 0 0 .35rem;
        color: #314333;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.08rem;
        font-weight: 800;
    }
    .advisory-section-intro { margin: 0 0 .9rem; color: #586454; line-height: 1.6; }
    .advisory-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .65rem; }
    .advisory-item {
        display: flex;
        align-items: flex-start;
        gap: .7rem;
        padding: .8rem .85rem;
        border: 1px solid #ece2cd;
        border-radius: 12px;
        background: rgba(255,255,255,.68);
        color: #39463a;
        line-height: 1.55;
    }
    .advisory-icon { flex: 0 0 1.35rem; color: #987238; font-size: 1rem; text-align: center; }
    .advisory-item strong { display: block; margin-bottom: .12rem; color: #3d4936; font-size: .9rem; }
    .model-expander { opacity: .9; }
    hr { border-color: #e4ebe5 !important; }
    @media (max-width: 900px) {
        .site-nav { padding-right: 1.5rem; padding-left: 1.5rem; }
        .project-hero { padding-right: 1.5rem; padding-left: 1.5rem; }
    }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 3rem; }
        .st-key-farm_location { padding: 1rem; border-radius: 16px; }
        .st-key-farm_location [data-testid="stHorizontalBlock"] { flex-direction: column; gap: .35rem; }
        .st-key-farm_location [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 0 0 auto !important;
            width: 100% !important;
            max-width: 100%;
        }
        .project-masthead { margin-top: -1rem; }
        .site-nav { min-height: 52px; gap: .5rem; padding: .45rem 1rem; }
        .site-nav-brand { gap: .35rem; font-size: 1.12rem; }
        .site-nav-brand svg { width: 1.45rem; height: 1.45rem; }
        .site-nav-links { gap: .75rem; }
        .site-nav-links a { font-size: .76rem; }
        .site-nav-links .site-nav-home { display: none; }
        .site-nav-links .site-nav-cta { padding: .5rem .75rem; }
        .project-hero { min-height: 340px; padding: 2rem 1.25rem; background-position: 62% center; }
        .hero-title { font-size: clamp(2.35rem, 11vw, 3.4rem); max-width: 530px; }
        .hero-project-name { font-size: 1.35rem; }
        .hero-copy { max-width: 440px; font-size: .92rem; }
        .hero-actions { gap: .55rem; }
        .hero-cta, .hero-secondary { min-height: 2.7rem; padding: .62rem .82rem; font-size: .85rem; }
        .st-key-landing_upload { margin-top: -1.25rem; padding: 1rem; background-image: none; border-radius: 19px !important; }
        .st-key-landing_upload .landing-intro { margin-bottom: .75rem; }
        .st-key-landing_upload .landing-intro .section-heading { font-size: 1.75rem !important; }
        .st-key-landing_upload .stColumn { min-width: 0; }
        .st-key-select_tomato .stButton > button,
        .st-key-select_potato .stButton > button { min-height: 6.8rem; }
        .workflow-strip { padding: 1rem 0 1.5rem; }
        .workflow-heading { text-align: center; }
        .workflow-steps { grid-template-columns: 1fr; gap: .25rem; }
        .workflow-step { gap: .6rem; padding: .6rem 0; }
        .workflow-art { flex-basis: 5.5rem; width: 5.5rem; height: 5.5rem; }
        .workflow-step:not(:last-child):after { top: auto; right: auto; bottom: -.1rem; left: 1.15rem; width: 1px; height: .6rem; }
        .advisory-grid { grid-template-columns: 1fr; }
        .disease-banner { padding: 1.15rem; }
        .result-summary { grid-template-columns: repeat(auto-fit, minmax(115px, 1fr)); }
        .field-guide, .action-plan { border-radius: 12px; }
        .guide-list { grid-template-columns: 1fr; gap: .5rem; }
        .guide-list-item { gap: .65rem; padding: .72rem .75rem; }
        .management-step { gap: .65rem; }
    }
    @media (max-width: 390px) {
        .st-key-landing_upload [data-testid="stHorizontalBlock"]:has(.st-key-leaf_upload):has(.st-key-stem_upload):has(.st-key-flower_upload) {
            flex-direction: column;
            gap: 1rem;
        }
        .st-key-landing_upload [data-testid="stHorizontalBlock"]:has(.st-key-leaf_upload):has(.st-key-stem_upload):has(.st-key-flower_upload) > [data-testid="stColumn"] {
            flex: 0 0 auto !important;
            width: 100% !important;
            max-width: 100%;
        }
    }
    </style>
    """.replace("__HERO_IMAGE__", hero_image_data).replace("__BOTANICAL_ART__", botanical_art_data),
    unsafe_allow_html=True,
)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "gradcam_images" not in st.session_state:
    st.session_state.gradcam_images = {}

st.markdown(
    f"""
    <div class="project-masthead">
    <nav class="site-nav" aria-label="Main navigation">
        <a class="site-nav-brand" href="#home" aria-label="PlantVision AI home">
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <path d="M15.8 28.5c.2-8.7 2.7-15.2 9.8-21.3M15.7 28.5c-.8-7.8-4.7-13.2-11-17.2" fill="none" stroke="#315d32" stroke-width="2.2" stroke-linecap="round"/>
                <path d="M21.4 13.1c-1.1-5 1.1-8.2 6.1-9.6.9 4.8-1.3 8-6.1 9.6ZM14 19.5c-4.7.4-7.5-2-8.5-6.9 4.8-.1 7.6 2.2 8.5 6.9Zm4.8-8.8c-3.6-3.3-3.7-6.8-.5-10.5 3.5 3.2 3.6 6.7.5 10.5Zm-1.9 13.1c-4.6 1.2-7.7-.5-9.7-5.1 4.6-1.1 7.8.6 9.7 5.1Z" fill="#638047" stroke="#315d32" stroke-width=".8"/>
            </svg>
            <span>PlantVision AI</span>
        </a>
        <div class="site-nav-links">
            <a class="site-nav-home" href="#home">Home</a>
            <a href="#how-it-works">How it works</a>
            <a class="site-nav-cta" href="#screening-uploader">Get Started</a>
        </div>
    </nav>
    <header class="project-hero" id="home">
        <div class="hero-content">
            <p class="hero-project-name">PlantVision AI</p>
            <h1 class="hero-title">Know Your Plant.<br>Know Your Harvest.</h1>
            <p class="hero-copy">Screen a leaf and get clear guidance to help protect your harvest.</p>
            <div class="hero-actions">
                <a class="hero-cta" href="#screening-uploader">Analyse a Plant <span aria-hidden="true">&rarr;</span></a>
                <a class="hero-secondary" href="#how-it-works"><span class="hero-play" aria-hidden="true">&#9654;</span> How it works</a>
            </div>
        </div>
    </header>
</div>
    """,
    unsafe_allow_html=True,
)



if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = "Tomato"

leaf_type = ["jpg", "jpeg", "png", "webp", "bmp"]
with st.container(border=True, key="landing_upload"):
    st.markdown(
        """
        <section class="landing-intro" id="screening-uploader">
            <p class="upload-eyebrow">Get started</p>
            <h2 class="section-heading">Analyse a Plant Leaf</h2>
            <p class="section-description">Upload a clear image of a tomato or potato leaf to detect potential diseases and get AI-powered insights.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    upload_columns = st.columns(3, gap="medium")
    upload_specs = (
        ("Leaf image", "Required · used for disease prediction", "Attach leaf image", "leaf_upload"),
        ("Stem image", "Optional · Grad-CAM view only", "Attach stem image", "stem_upload"),
        ("Flower image", "Optional · Grad-CAM view only", "Attach flower image", "flower_upload"),
    )
    uploaded_file = stem_file = flower_file = None
    for column, (label, purpose, widget_label, widget_key) in zip(upload_columns, upload_specs):
        with column:
            st.markdown(
                f'<div class="landing-field-title">{label}</div><p class="landing-field-purpose">{purpose}</p>',
                unsafe_allow_html=True,
            )
            image_file = st.file_uploader(
                widget_label,
                type=leaf_type,
                key=widget_key,
                label_visibility="collapsed",
            )
            if image_file is not None:
                st.image(image_file, caption=f"{label} preview", use_container_width=True)
            if widget_key == "leaf_upload":
                uploaded_file = image_file
            elif widget_key == "stem_upload":
                stem_file = image_file
            else:
                flower_file = image_file

    st.markdown('<div class="landing-field-title">Select crop</div>', unsafe_allow_html=True)
    tomato_col, potato_col = st.columns(2)
    with tomato_col:
        st.button(
            "Tomato",
            type="primary" if st.session_state.selected_crop == "Tomato" else "secondary",
            use_container_width=True,
            key="select_tomato",
            on_click=choose_crop,
            args=("Tomato",),
        )
    with potato_col:
        st.button(
            "Potato",
            type="primary" if st.session_state.selected_crop == "Potato" else "secondary",
            use_container_width=True,
            key="select_potato",
            on_click=choose_crop,
            args=("Potato",),
        )
    st.caption(
        "The leaf image is used for disease prediction. Stem and flower images are sent only to the existing image explanation endpoint."
    )
st.markdown(
    """
    <section class="workflow-strip" id="how-it-works">
        <div class="workflow-heading">
            <p class="workflow-eyebrow">How it works</p>
            <h2 class="workflow-main-title">From image to guidance</h2>
            <p class="workflow-intro">A simple three-step process to help you identify plant diseases and take informed action.</p>
        </div>
        <div class="workflow-steps">
            <article class="workflow-step">
                <span class="workflow-number">1</span>
                <span class="workflow-art" aria-hidden="true"><svg viewBox="0 0 130 110" fill="none"><circle cx="64" cy="57" r="51" fill="#f2eedc"/><path d="M28 87c24-16 37-36 54-65m-37 47c-2-17-10-29-27-37m40 17c3-17 14-28 32-35m-47 48c-14-3-25 1-36 10" stroke="#526c37" stroke-width="3" stroke-linecap="round"/><path d="M45 67c-17-2-25-12-27-27 16 1 26 9 27 27Zm14-20c0-18 10-29 26-35 4 17-5 29-26 35Zm-5 20c-14-6-26-3-35 8 13 9 25 6 35-8Z" fill="#829355" stroke="#526c37" stroke-width="1.5"/><path d="m45 67-18-22m32 2 12-24m-11 48-23 12" stroke="#d6d7a4" stroke-width="1.5"/></svg></span>
                <div class="workflow-copy"><h3 class="workflow-title">Detect</h3><p class="workflow-note">Upload a tomato or potato leaf image. Our AI analyses the image for potential diseases.</p></div></article>
            <article class="workflow-step">
                <span class="workflow-number">2</span>
                <span class="workflow-art" aria-hidden="true"><svg viewBox="0 0 130 110" fill="none"><circle cx="65" cy="57" r="51" fill="#f2eedc"/><rect x="25" y="25" width="80" height="53" rx="5" fill="#31543a" stroke="#263c2d" stroke-width="2"/><rect x="31" y="31" width="68" height="41" rx="2" fill="#c9d7ad"/><path d="M37 63c16-9 23-18 34-27m-24 21c-1-10-7-17-16-22m27 12c2-10 8-16 19-20m-27 30c-8-2-14 1-20 6" stroke="#466941" stroke-width="2"/><path d="M66 43c7-8 15-10 24-5-3 10-10 15-21 13 6 1 11 5 14 12-9 4-18 1-22-8-2-4 0-8 5-12Z" fill="#e1a43b" fill-opacity=".9"/><circle cx="81" cy="50" r="8" fill="#d94a2f" fill-opacity=".82"/><path d="M57 79h16m-8 0v10m-19 0h54" stroke="#405747" stroke-width="3" stroke-linecap="round"/></svg></span>
                <div class="workflow-copy"><h3 class="workflow-title">Explain</h3><p class="workflow-note">See visual explanations using Grad-CAM to understand what the model found.</p></div></article>
            <article class="workflow-step">
                <span class="workflow-number">3</span>
                <span class="workflow-art" aria-hidden="true"><svg viewBox="0 0 130 110" fill="none"><circle cx="65" cy="57" r="51" fill="#f2eedc"/><path d="M45 27h40v62H45z" fill="#d9d2aa" stroke="#465b37" stroke-width="2.5"/><path d="M55 22h20v12H55z" rx="4" fill="#87975c" stroke="#465b37" stroke-width="2"/><path d="m53 49 4 4 7-8m-11 20 4 4 7-8m-11 20 4 4 7-8" stroke="#315b36" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M70 49h9m-9 16h9m-9 16h9" stroke="#62724c" stroke-width="2.5" stroke-linecap="round"/><path d="M39 84c-8-6-12-13-11-23 10 2 16 8 17 18m48 4c8-6 12-13 11-23-10 2-16 8-17 18" fill="#829355" stroke="#526c37" stroke-width="1.5"/></svg></span>
                <div class="workflow-copy"><h3 class="workflow-title">Recommend</h3><p class="workflow-note">Get practical, science-backed guidance to manage the issue and protect your crops.</p></div></article>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

def _sanitize_farm_pincode():
    value = str(st.session_state.get("farm_location_pincode", ""))
    st.session_state.farm_location_pincode = "".join(
        character for character in value if character in "0123456789"
    )[:6]


with st.container(key="farm_location"):
    st.markdown(
        '<div class="farm-location-eyebrow">Farm details</div>'
        '<h2 class="farm-location-heading">Farm location in India</h2>'
        '<p class="farm-location-description">Add a location to keep your screening record grounded in its growing context.</p>',
        unsafe_allow_html=True,
    )

    india_states_and_uts = [
        "Select State / Union Territory",
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
        "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
        "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
        "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi (NCT)",
        "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
    ]

    location_col1, location_col2 = st.columns(2, gap="large")
    with location_col1:
        st.selectbox(
            "State / Union Territory",
            india_states_and_uts,
            key="farm_location_state",
        )
        st.text_input(
            "City or district",
            placeholder="e.g., Lucknow",
            key="farm_location_city_district",
        )
    with location_col2:
        st.text_input(
            "PIN code (optional)",
            placeholder="6-digit PIN code",
            max_chars=6,
            key="farm_location_pincode",
            on_change=_sanitize_farm_pincode,
        )
        st.text_input(
            "GPS coordinates (optional)",
            placeholder="Latitude, longitude",
            key="farm_location_coordinates",
        )

    with st.expander("Additional growing conditions (optional)", expanded=False):
        context_col1, context_col2 = st.columns(2, gap="large")
        with context_col1:
            st.text_input(
                "Soil type (optional)",
                placeholder="e.g., loamy, sandy, clay",
                key="farm_location_soil_type",
            )
        with context_col2:
            st.selectbox(
                "Irrigation routine (optional)",
                ["Not specified", "Rain-fed", "Drip", "Sprinkler", "Furrow / flood", "Other"],
                key="farm_location_irrigation_routine",
            )
        st.selectbox(
            "Crop growth stage (optional)",
            ["Not specified", "Seedling", "Vegetative", "Flowering", "Fruiting / tuber development", "Maturity"],
            key="farm_location_crop_stage",
        )
        st.info(
            "The current app does not perform a weather lookup. Farm location and growing-condition details are collected for context only and do not affect the live prediction."
        )


if uploaded_file is not None:
    leaf_key = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    if st.session_state.get("leaf_key") != leaf_key:
        st.session_state.leaf_key = leaf_key
        st.session_state.analysis_result = None
        st.session_state.gradcam_images = {}




    st.subheader("Ready to analyze")
    analyze = st.button(
        "Analyze Images",
        type="primary",
        use_container_width=True,
    )

    if analyze:

            with st.spinner(
                "Analyzing leaf image..."
            ):

                try:

                    files = leaf_request_files(uploaded_file)

                    response = requests.post(
                        f"{API_URL}/predict",
                        files=files,
                        timeout=60,
                    )

                except requests.RequestException as exc:

                    st.error(
                        "Could not connect to the "
                        "FastAPI backend."
                    )

                    st.code(
                        str(exc)
                    )

                    st.stop()

                if response.status_code != 200:

                    st.error(
                        f"API request failed "
                        f"(HTTP {response.status_code})."
                    )

                    try:
                        st.json(
                            response.json()
                        )

                    except Exception:
                        st.write(
                            response.text
                        )

                    st.stop()

                st.session_state.analysis_result = (
                    response.json()["result"]
                )


            st.success(
                "Analysis completed."
            )


    result = (
        st.session_state.analysis_result
    )


    if result is not None:
        st.markdown(
            '<div class="section-heading">Screening results</div>'
            '<p class="section-description">A visual screening result and practical guidance based on the available disease record.</p>',
            unsafe_allow_html=True,
        )

        prediction = result.get("prediction") or {}
        disease = result.get("disease") or {}
        crop = disease.get("crop")
        disease_name = disease.get("disease") or prediction.get("class")
        confidence = prediction.get("confidence")
        severity = disease.get("severity")

        severity_label = str(severity).replace("_", " ").title() if severity is not None else None
        facts = [("Crop", crop), ("Severity", severity_label), ("Confidence", f"{confidence:.1%}" if isinstance(confidence, (int, float)) else None)]
        fact_html = "".join(
            f"<div class='result-fact'><div class='result-fact-label'>{escape(label)}</div><div class='result-fact-value'>{escape(str(value))}</div></div>"
            for label, value in facts if value is not None
        )
        st.markdown(
            f'<div class="disease-banner"><div class="disease-eyebrow">Plant screening</div>'
            f'<div class="disease-title">{escape(str(disease_name or "Result unavailable"))}</div>'
            f'<div class="result-summary">{fact_html}</div></div>',
            unsafe_allow_html=True,
        )
        st.caption("Use this as a screening aid. A prediction is not a confirmed diagnosis.")

        st.markdown("#### Uploaded plant images")
        image_inputs = [
            ("Leaf", uploaded_file),
            ("Stem", stem_file),
            ("Flower", flower_file),
        ]
        image_inputs = [(label, image) for label, image in image_inputs if image is not None]
        if image_inputs:
            image_columns = st.columns(len(image_inputs), gap="medium")
            for column, (label, image) in zip(image_columns, image_inputs):
                with column:
                    with st.container(border=True):
                        image_hash = hashlib.sha256(image.getvalue()).hexdigest()
                        cache_key = f"{label}:{image_hash}"
                        st.markdown(f"**{label}**")
                        st.image(image.getvalue(), use_container_width=True)
                        if st.button(f"Generate Grad-CAM", key=f"gradcam_{label.lower().replace(' ', '_')}", use_container_width=True):
                            with st.spinner(f"Generating Grad-CAM for {label.lower()} image…"):
                                try:
                                    explain_response = requests.post(
                                        f"{API_URL}/explain",
                                        files=image_request_files(image),
                                        timeout=60,
                                    )
                                    if explain_response.status_code == 200:
                                        st.session_state.gradcam_images[cache_key] = explain_response.content
                                        st.rerun()
                                    else:
                                        st.error(f"Grad-CAM request failed (HTTP {explain_response.status_code}).")
                                except requests.RequestException as exc:
                                    st.error("Could not connect to the backend to generate Grad-CAM.")
                                    st.caption(str(exc))
                        if cache_key in st.session_state.gradcam_images:
                            st.image(
                                st.session_state.gradcam_images[cache_key],
                                caption="Grad-CAM overlay",
                                use_container_width=True,
                            )
        else:
            st.info("No uploaded plant images are available in this session.")

        quality = result.get("image_quality") or {}
        if quality:
            with st.expander("Image quality details", expanded=False):
                score = quality.get("score")
                status = quality.get("status")
                if isinstance(score, (int, float)):
                    st.metric("Quality score", f"{score:.0f}/100")
                if status:
                    st.write(f"Status: **{str(status).replace('_', ' ').title()}**")
                    if status == "good":
                        st.success("Image quality is suitable for analysis.")
                    elif status == "warning":
                        st.warning("Image quality has some limitations. A clearer image may help.")
                    else:
                        st.warning("Image quality is limited. Consider uploading a clearer image.")
                for warning in quality.get("warnings") or []:
                    st.caption(f"⚠️ {warning}")

        st.markdown('<div class="section-heading disease-guide-heading">Disease guide</div>', unsafe_allow_html=True)
        symptoms = disease.get("symptoms") or []
        management = disease.get("general_management") or []
        if disease.get("description"):
            st.markdown('<h3 class="guide-section-heading">What this disease is</h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="guide-intro">{escape(str(disease["description"]))}</div>', unsafe_allow_html=True)
        elif disease_name:
            st.markdown(
                f'<section class="result-meaning"><h3>What this result means</h3>The image was matched to <strong>{escape(str(disease_name))}</strong> in the current screening model. This is a screening result, not a confirmed diagnosis.</section>',
                unsafe_allow_html=True,
            )

        symptom_items = []
        title_separators = (" may ", " can ", " are ", " is ", " was ", " were ", " show ", " develop ")
        for index, symptom in enumerate(symptoms, 1):
            symptom_text = str(symptom).strip()
            title = ""
            explanation = symptom_text
            for separator in title_separators:
                if separator in symptom_text:
                    title, remainder = symptom_text.split(separator, 1)
                    explanation = f"{separator.strip()} {remainder}"
                    break
            title_html = f'<strong class="guide-entry-title">{escape(title)}</strong>' if title else ""
            symptom_items.append(
                f'<div class="guide-list-item"><span class="guide-marker" aria-hidden="true">{index:02d}</span>'
                f'<span class="guide-entry-copy">{title_html}{escape(explanation)}</span></div>'
            )
        if symptoms:
            st.markdown(
                '<section class="field-guide" aria-labelledby="field-guide-title">'
                '<p class="field-guide-eyebrow">Symptoms to look for · Field notes</p>'
                '<h3 class="field-guide-title" id="field-guide-title">Recognise the signs</h3>'
                '<p class="field-guide-intro">Compare the plant with the visible signs listed in this screening record.</p>'
                f'<div class="guide-list">{"".join(symptom_items)}</div></section>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No symptom notes are available for this result.")

        if management:
            action_items = "".join(
                f'<div class="management-step"><span class="step-number" aria-hidden="true">{index}</span>'
                f'<span class="management-step-copy"><strong>Step {index}</strong><br>{escape(str(action))}</span></div>'
                for index, action in enumerate(management, 1)
            )
            st.markdown(
                '<section class="action-plan" aria-labelledby="action-plan-title">'
                '<p class="action-plan-eyebrow">Curated management plan</p>'
                '<h3 class="action-plan-title" id="action-plan-title">What to do first</h3>'
                '<p class="action-plan-intro">Start with the first action, then work through the remaining guidance in order.</p>'
                f'<div class="management-steps">{action_items}</div></section>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No management guidance is available for this result. Avoid applying a treatment based only on this screening.")

        advisory = disease.get("advisory")
        advisory_items = [
            ("↗", "Rapid spread", "If spots are spreading quickly or several plants are becoming affected, seek advice promptly."),
            ("✳", "Severe damage", "If leaves, stems, or fruit are being damaged extensively, get the plant assessed."),
            ("⌕", "Uncertain diagnosis", "If the symptoms do not match the description or the prediction seems incorrect, ask an agricultural expert to verify it."),
            ("＋", "Treatment uncertainty", "Before applying pesticides or other chemical treatments, confirm that the product is appropriate for the crop and disease and follow local label instructions."),
        ]
        advisory_html = "".join(
            f'<div class="advisory-item"><span class="advisory-icon" aria-hidden="true">{icon}</span>'
            f'<span><strong>{escape(title)}</strong>{escape(copy)}</span></div>'
            for icon, title, copy in advisory_items
        )
        advisory_intro = (
            f'<p class="advisory-section-intro">{escape(str(advisory))}</p>'
            if advisory else
            '<p class="advisory-section-intro">A screening result can be uncertain. Consider expert advice in these situations.</p>'
        )
        st.markdown(
            '<section class="advisory-section"><h3 class="advisory-section-title">When to consult an agricultural expert</h3>'
            f'{advisory_intro}<div class="advisory-grid">{advisory_html}</div></section>',
            unsafe_allow_html=True,
        )

        sources = disease.get("sources") or result.get("sources") or []
        if sources:
            st.markdown('<h3 class="guide-section-heading">Supporting sources</h3>', unsafe_allow_html=True)
            for source in sources:
                if isinstance(source, dict) and source.get("url"):
                    st.markdown(f"- [{source.get('title') or source['url']}]({source['url']})")
                elif isinstance(source, str):
                    st.markdown(f"- {source}")

        with st.expander("Model details", expanded=False):
            if result.get("model"):
                st.caption(f"Model: {result['model']}")
            temperature = result.get("temperature")
            if isinstance(temperature, (int, float)):
                st.caption(f"Calibration temperature: {temperature:.4f}")

else:

    st.info(
        "Upload a clear leaf image to enable the live screening. "
        "Additional plant images and farm context are optional."
    )
