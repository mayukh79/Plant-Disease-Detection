import hashlib
from html import escape
from pathlib import Path
import sys

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.uploads import (
    leaf_request_files,
)
from src.utils.config import (
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

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --forest: #14532d;
        --leaf: #16a34a;
        --ink: #0d1c12;
        --muted: #34493a;
        --line: #e4ebe5;
        --surface: #ffffff;
        --wash: #f5f8f5;
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
        background: linear-gradient(155deg, #e0ebe1 0%, #edf3ed 48%, #e5eee6 100%);
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }
    .project-hero {
        position: relative;
        overflow: hidden;
        padding: 2.25rem 2.6rem;
        margin: 0 0 1.7rem;
        border: 1px solid #dce9de;
        border-radius: 24px;
        background: linear-gradient(115deg, #ffffff 0%, #f0f8f1 62%, #e5f3e7 100%);
        box-shadow: 0 12px 36px rgba(25, 67, 39, .07);
    }
    .project-hero:after {
        content: "";
        position: absolute;
        width: 270px;
        height: 270px;
        right: -70px;
        top: -125px;
        border: 1px solid rgba(22, 163, 74, .13);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(22, 163, 74, .035), 0 0 0 58px rgba(22, 163, 74, .025);
        pointer-events: none;
    }
    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        margin-bottom: .85rem;
        padding: .38rem .75rem;
        border: 1px solid #cfe5d2;
        border-radius: 999px;
        background: rgba(255,255,255,.78);
        color: var(--forest);
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .09em;
        text-transform: uppercase;
    }
    .hero-title {
        position: relative;
        z-index: 1;
        margin: 0;
        color: #163b25;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 4vw, 3.15rem);
        font-weight: 800;
        letter-spacing: -.045em;
        line-height: 1.12;
    }
    .hero-copy {
        position: relative;
        z-index: 1;
        max-width: 720px;
        margin: .75rem 0 0;
        color: #344b3a;
        font-size: 1.02rem;
        line-height: 1.65;
    }
    .workflow-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin: 0 0 2rem;
    }
    .workflow-step {
        display: flex;
        align-items: center;
        gap: .8rem;
        padding: .9rem 1rem;
        border: 1px solid #e2eae3;
        border-radius: 14px;
        background: rgba(255,255,255,.82);
    }
    .workflow-number {
        display: grid;
        flex: 0 0 2rem;
        width: 2rem;
        height: 2rem;
        place-items: center;
        border-radius: 10px;
        background: #e8f5eb;
        color: #166534;
        font-family: 'Manrope', sans-serif;
        font-size: .82rem;
        font-weight: 800;
    }
    .workflow-title { color: #244331; font-size: .88rem; font-weight: 700; }
    .workflow-note { margin-top: .12rem; color: #435747; font-size: .75rem; }
    .section-heading {
        margin: 1.25rem 0 .25rem;
        color: #183d27;
        font-family: 'Manrope', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -.025em;
    }
    .section-description { margin: 0 0 .9rem; color: #435547; font-size: .92rem; }
    h2, h3 { font-family: 'Manrope', sans-serif !important; color: #1a3926 !important; }
    h2 { font-size: 1.35rem !important; letter-spacing: -.02em; }
    [data-testid="stFileUploader"], [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 5px 18px rgba(20, 50, 30, .035);
    }
    [data-testid="stFileUploader"] { padding: .35rem; }
    [data-testid="stFileUploader"] section {
        border: 1px dashed #9bb8a0 !important;
        border-radius: 12px !important;
        background: #f5f8f5 !important;
        color: #17291c !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
        color: #17291c !important;
    }
    [data-testid="stFileUploader"] button {
        border: 1px solid #bdd0c0 !important;
        border-radius: 9px !important;
        background: #ffffff !important;
        color: #173b23 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #82948a !important;
        border-radius: 12px !important;
        background: #24272f !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        border: 1px solid #737d89 !important;
        background: #373c46 !important;
        color: #ffffff !important;
    }
    [data-testid="stExpander"] { overflow: hidden; }
    [data-testid="stImage"] img { border-radius: 14px; }
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
        background: linear-gradient(110deg, #ffffff 0%, #eef7ef 100%);
        box-shadow: 0 8px 24px rgba(20, 70, 35, .06);
    }
    .disease-eyebrow { color: #3c6847; font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .disease-title { margin: .3rem 0 .8rem; color: #153b23; font-family: 'Manrope', sans-serif; font-size: 1.55rem; font-weight: 800; }
    .disease-tags { display: flex; flex-wrap: wrap; gap: .5rem; }
    .disease-tag { padding: .35rem .68rem; border: 1px solid #d3e4d5; border-radius: 999px; background: #fff; color: #294b32; font-size: .8rem; font-weight: 700; }
    .disease-list-item { display: flex; gap: .65rem; align-items: flex-start; margin: .5rem 0; color: #23372a; line-height: 1.55; }
    .disease-list-marker { flex: 0 0 1.35rem; color: #16803d; font-weight: 800; }
    .advisory-panel { margin-top: .9rem; padding: 1.1rem 1.35rem; border-radius: 15px; background: #173b25; color: #ffffff !important; box-shadow: 0 8px 22px rgba(20, 59, 37, .14); }
    .advisory-panel * { color: #ffffff !important; }
    .advisory-heading { margin-bottom: .3rem; font-family: 'Manrope', sans-serif; font-size: 1rem; font-weight: 800; }
    .advisory-copy { margin: 0; line-height: 1.65; }
    hr { border-color: #e4ebe5 !important; }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 3rem; }
        .project-hero { padding: 1.5rem 1.35rem; border-radius: 18px; }
        .hero-copy { font-size: .94rem; }
        .workflow-strip { grid-template-columns: 1fr; gap: .5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

st.markdown(
    f"""
    <header class="project-hero">
        <div class="hero-kicker">🌱 PlantVision AI · B.Tech CSE (AI-ML)</div>
        <h1 class="hero-title">Detect. Explain. Recommend.</h1>
        <p class="hero-copy">A plant disease decision-support dashboard for Potato and Tomato. The current screening flow uses {MODEL_NAME} on leaf images, visualizes model activations with Grad-CAM, and connects predictions to curated disease guidance.</p>
    </header>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow-strip">
        <div class="workflow-step"><div class="workflow-number">01</div><div><div class="workflow-title">Detect</div><div class="workflow-note">Screen a Potato or Tomato leaf image</div></div></div>
        <div class="workflow-step"><div class="workflow-number">02</div><div><div class="workflow-title">Explain</div><div class="workflow-note">Explore Grad-CAM visual activation</div></div></div>
        <div class="workflow-step"><div class="workflow-number">03</div><div><div class="workflow-title">Recommend</div><div class="workflow-note">Review curated disease guidance</div></div></div>
    </div>
    <div class="section-heading">Start a screening</div>
    <p class="section-description">Upload the leaf for screening. Stem and fruit/tuber uploads can each receive a separate Grad-CAM view; farm details remain context-only.</p>
    """,
    unsafe_allow_html=True,
)

if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = "Tomato"

st.markdown("### Select the crop you are uploading")
tomato_col, potato_col = st.columns(2)
with tomato_col:
    st.button(
        "🍅  Tomato",
        type="primary" if st.session_state.selected_crop == "Tomato" else "secondary",
        use_container_width=True,
        key="select_tomato",
        on_click=choose_crop,
        args=("Tomato",),
    )
with potato_col:
    st.button(
        "🥔  Potato",
        type="primary" if st.session_state.selected_crop == "Potato" else "secondary",
        use_container_width=True,
        key="select_potato",
        on_click=choose_crop,
        args=("Potato",),
    )

selected_crop = st.session_state.selected_crop

st.caption(
    "Crop selection labels the fruit/tuber input. Prediction uses the leaf; "
    "Grad-CAM can be generated separately for each uploaded image."
)

leaf_type = ["jpg", "jpeg", "png", "webp", "bmp"]
leaf_col, stem_col, fruit_col = st.columns([1.15, 1, 1])

with leaf_col:
    with st.container(border=True):
        st.markdown("#### 🌿 Leaf image")
        st.caption("Required · Used for screening")
        uploaded_file = st.file_uploader(
            "Attach leaf image",
            type=leaf_type,
            key="leaf_upload",
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Leaf preview", width=220)

with stem_col:
    with st.container(border=True):
        st.markdown("#### 🌱 Stem image")
        st.caption("Optional · Grad-CAM available")
        stem_file = st.file_uploader(
            "Attach stem image",
            type=leaf_type,
            key="stem_upload",
            label_visibility="collapsed",
        )
        if stem_file is not None:
            st.image(stem_file, caption="Stem preview", width=220)

with fruit_col:
    fruit_label = "Tuber image" if selected_crop == "Potato" else "Fruit image"
    with st.container(border=True):
        st.markdown(f"#### 🍅 {fruit_label}")
        st.caption("Optional · Grad-CAM available")
        fruit_file = st.file_uploader(
            f"Attach {fruit_label.lower()}",
            type=leaf_type,
            key="fruit_tuber_upload",
            label_visibility="collapsed",
        )
        if fruit_file is not None:
            st.image(fruit_file, caption=f"{fruit_label} preview", width=220)

st.markdown(
    '<div class="section-heading">Farm location in India</div>'
    '<p class="section-description">Select a State or Union Territory, then enter a city, district, PIN code, or GPS coordinates.</p>',
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

location_col1, location_col2 = st.columns(2)
with location_col1:
    st.selectbox(
        "State / Union Territory",
        india_states_and_uts,
        key="india_state",
    )
    st.text_input(
        "City or district",
        placeholder="e.g., Lucknow",
        key="farm_city_district",
    )
with location_col2:
    st.text_input(
        "PIN code (optional)",
        placeholder="6-digit PIN code",
        max_chars=6,
        key="farm_pincode",
    )
    st.text_input(
        "GPS coordinates (optional)",
        placeholder="Latitude, longitude",
        key="farm_coordinates",
    )

with st.expander("Additional growing conditions (optional)"):
    st.caption(
        "These fields are collected for interface context only. They are not "
        "sent to or used by the current prediction pipeline."
    )

    context_col1, context_col2 = st.columns(2)
    with context_col1:
        st.text_input(
            "Soil type (optional)",
            placeholder="e.g., loamy, sandy, clay",
            key="soil_type",
        )
    with context_col2:
        st.selectbox(
            "Irrigation routine (optional)",
            ["Not specified", "Rain-fed", "Drip", "Sprinkler", "Furrow / flood", "Other"],
            key="irrigation_routine",
        )
    st.selectbox(
        "Crop growth stage (optional)",
        ["Not specified", "Seedling", "Vegetative", "Flowering", "Fruiting / tuber development", "Maturity"],
        key="crop_stage",
    )
    st.info(
        "The proposed methodology derives temperature from the farm location. "
        "The current app does not perform a weather lookup, and location does "
        "not affect the live prediction."
    )


if uploaded_file is not None:
    leaf_key = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    if st.session_state.get("leaf_key") != leaf_key:
        st.session_state.leaf_key = leaf_key
        st.session_state.analysis_result = None

    st.subheader("Ready to analyze")
    analyze = st.button(
        "🔍 Analyze Leaf Image",
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
            '<p class="section-description">Review the predicted condition, confidence, and image quality guidance.</p>',
            unsafe_allow_html=True,
        )

        prediction = result[
            "prediction"
        ]

        disease = result[
            "disease"
        ]

        st.divider()

        st.subheader("Image quality")

        quality = result.get(
            "image_quality"
        )

        if quality is not None:

            quality_col1, quality_col2 = (
                st.columns(2)
            )

            with quality_col1:
                st.metric(
                    "Quality Score",
                    f"{quality['score']:.0f}/100",
                )

            with quality_col2:
                st.metric(
                    "Status",
                    quality["status"].title(),
                )

            if quality["status"] == "good":
                st.success(
                    "Image quality is suitable for analysis."
                )

            elif quality["status"] == "warning":
                st.warning(
                    "Image quality has some limitations. "
                    "Consider uploading a clearer image."
                )

            else:
                st.error(
                    "Image quality is poor. "
                    "A clearer image is recommended."
                )

            for warning in quality["warnings"]:
                st.caption(
                    f"⚠️ {warning}"
                )

        st.divider()

        st.subheader("Predicted condition")

        metric1, metric2, metric3 = (
            st.columns(3)
        )

        with metric1:

            st.metric(
                "Crop",
                disease["crop"],
            )

        with metric2:

            st.metric(
                "Disease",
                disease["disease"],
            )

        with metric3:

            st.metric(
                "Confidence",
                f"{prediction['confidence']:.2%}",
            )

        st.divider()

        st.markdown(
            '<div class="section-heading">Disease guide</div>'
            '<p class="section-description">A concise overview of the predicted condition, visible signs, and general next steps.</p>',
            unsafe_allow_html=True,
        )

        status_text = escape(str(disease["status"]))
        severity_text = escape(str(disease["severity"]))
        crop_text = escape(str(disease["crop"]))
        disease_text = escape(str(disease["disease"]))
        st.markdown(
            f"""
            <div class="disease-banner">
                <div class="disease-eyebrow">Condition overview</div>
                <div class="disease-title">{disease_text}</div>
                <div class="disease-tags">
                    <span class="disease-tag">Crop · {crop_text}</span>
                    <span class="disease-tag">Status · {status_text}</span>
                    <span class="disease-tag">Severity · {severity_text}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        symptoms_html = "".join(
            "<div class='disease-list-item'>"
            "<span class='disease-list-marker'>●</span>"
            f"<span>{escape(str(symptom))}</span></div>"
            for symptom in disease["symptoms"]
        )
        management_html = "".join(
            "<div class='disease-list-item'>"
            f"<span class='disease-list-marker'>{index:02d}</span>"
            f"<span>{escape(str(action))}</span></div>"
            for index, action in enumerate(disease["general_management"], 1)
        )

        symptoms_col, management_col = st.columns(2)
        with symptoms_col:
            with st.container(border=True):
                st.markdown("#### 🔎 Symptoms to look for")
                st.markdown(symptoms_html, unsafe_allow_html=True)

        with management_col:
            with st.container(border=True):
                st.markdown("#### 🌱 General management")
                st.markdown(management_html, unsafe_allow_html=True)

        advisory_text = escape(str(disease["advisory"]))
        st.markdown(
            f"""
            <div class="advisory-panel">
                <div class="advisory-heading">ℹ️ Advisory</div>
                <p class="advisory-copy">{advisory_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


        st.caption(
            f"Model: {result['model']} | "
            f"Calibration temperature: "
            f"{result['temperature']:.4f}"
        )

else:

    st.info(
        "Upload a clear leaf image to enable the live screening. "
        "Additional plant images and farm context are optional."
    )
