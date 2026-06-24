import base64
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st


# ============================================================
# RUTAS E IMPORTS DEL PROYECTO
# ============================================================

# streamlit_app.py se encuentra en src/app.
APP_DIR = Path(__file__).resolve().parent
SRC_DIR = APP_DIR.parent

# Añade src al sistema de imports para poder acceder a main.py,
# domain, imaging, model y data.
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import build_predictor
from domain.patient import Patient
from imaging.brain_image import BrainImage
from imaging.brain_images_analyzer import BrainImageAnalyzer
from imaging.brain_image_processor import BrainImagePreprocessor


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Detección temprana de Alzheimer",
    page_icon="🧠",
    layout="wide"
)

BRAIN_IMAGE_PATH = SRC_DIR / "assets" / "brain_hero.png"

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================

st.markdown(
    """
    <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #F5F7FA 0%, #EEF3F8 45%, #F8FAFC 100%);
            color: #1F2937;
        }

        /* Ocultar menú y footer de Streamlit */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        /* Contenedor principal */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        /* Hero principal */
        
        .hero-kicker {
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #4F6EF7;
            margin-bottom: 12px;
        }

        .hero-title {
            font-size: 3.1rem;
            line-height: 1.05;
            font-weight: 800;
            color: #111827;
            margin-bottom: 16px;
        }

        .hero-title span {
            color: #4F6EF7;
        }

        .hero-subtitle {
            font-size: 1.08rem;
            color: #4B5563;
            line-height: 1.65;
            max-width: 720px;
            margin-bottom: 24px;
        }

        .hero-badge {
            display: inline-block;
            padding: 10px 16px;
            background: #E8EEFF;
            color: #2E4DA7;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.88rem;
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .hero-brain-image {
            max-width: 72%;
            max-height: 260px;
            object-fit: contain;
            display: block;
            margin: 0 auto;
            box-shadow: none;
            border-radius: 22px;
            position: relative;
            z-index: 2;
        }

        .hero-floating-card {
            z-index: 3;
        }

        .hero-visual::after {
            content: "";
            position: absolute;
            inset: -35%;
            background:
                conic-gradient(
                    from 180deg,
                    rgba(139, 92, 246, 0.18),
                    rgba(0, 229, 255, 0.16),
                    rgba(255, 99, 180, 0.16),
                    rgba(139, 92, 246, 0.18)
                );
            filter: blur(42px);
            opacity: 0.75;
            pointer-events: none;
        }

        .hero-visual {
            min-height: 260px;
            background:
                radial-gradient(circle at 45% 45%, rgba(139, 92, 246, 0.16), transparent 34%),
                radial-gradient(circle at 60% 42%, rgba(0, 229, 255, 0.14), transparent 36%),
                radial-gradient(circle at 52% 62%, rgba(255, 99, 180, 0.13), transparent 38%),
                linear-gradient(
                    135deg,
                    #FFFFFF 0%,
                    #F8FAFF 35%,
                    #F4FBFF 58%,
                    #FFF7FC 78%,
                    #FFFFFF 100%
                );
            border-radius: 28px;
            border: 1px solid rgba(196, 181, 253, 0.55);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
            box-shadow:
                0px 22px 55px rgba(79, 110, 247, 0.12),
                inset 0px 0px 80px rgba(255, 255, 255, 0.86);
        }

        .hero-visual::before {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: 28px;
            padding: 1.5px;
            background: linear-gradient(
                135deg,
                rgba(139, 92, 246, 0.75),
                rgba(0, 229, 255, 0.55),
                rgba(255, 99, 180, 0.60)
            );
            -webkit-mask:
                linear-gradient(#fff 0 0) content-box,
                linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }

        .hero-visual img {
            max-width: 72%;
            margin: 0 auto;
            display: block;
            box-shadow: none;
            border-radius: 24px;
        }

        .brain-icon {
            font-size: 7.5rem;
            filter: drop-shadow(0px 20px 25px rgba(79, 110, 247, 0.18));
        }

        .hero-floating-card {
            position: absolute;
            bottom: 22px;
            right: 22px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0px 12px 30px rgba(31, 41, 55, 0.08);
            font-size: 0.82rem;
            color: #4B5563;
        }


        /* Tarjetas */
        .section-card {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 26px;
            padding: 28px 30px;
            box-shadow: 0px 14px 36px rgba(31, 41, 55, 0.06);
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 1.55rem;
            font-weight: 800;
            color: #111827;
            margin-bottom: 6px;
        }

        .section-subtitle {
            font-size: 0.98rem;
            color: #6B7280;
            line-height: 1.55;
            margin-bottom: 22px;
        }

        .small-label {
            font-size: 0.82rem;
            color: #6B7280;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 6px;
        }


        /* Tarjetas de variables clínicas y factores genéticos */
        .st-key-patient_cards {
            margin-top: 0.4rem;
            margin-bottom: 1.8rem;
        }

        .st-key-patient_cards div[data-testid="stHorizontalBlock"] {
            gap: 1.5rem;
            align-items: stretch;
        }

        .st-key-patient_cards
        div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"] {
            box-sizing: border-box;
            min-height: 555px;
            height: auto;
            padding: 1.45rem 1.5rem 1.65rem;
            border: 2px solid transparent;
            border-radius: 28px;
            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.96) 0%,
                    rgba(247, 248, 255, 0.94) 55%,
                    rgba(249, 252, 255, 0.96) 100%
                ) padding-box,
                linear-gradient(
                    135deg,
                    #8B5CF6 0%,
                    #38BDF8 48%,
                    #F472B6 100%
                ) border-box;
            box-shadow: none;
            transition: none;
        }

        .st-key-patient_cards
        div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"]:hover {
            transform: none;
            box-shadow: none;
        }

        .patient-card-title {
            display: flex;
            align-items: center;
            min-height: 82px;
            margin-bottom: 1.35rem;
            padding: 1.15rem 1.35rem;
            border: 1px solid rgba(139, 92, 246, 0.10);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: none;
            color: #61697A;
            font-size: 0.96rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .patient-card-title::before {
            content: "";
            flex: 0 0 auto;
            width: 12px;
            height: 12px;
            margin-right: 12px;
            border-radius: 999px;
            background: linear-gradient(
                135deg,
                #8B5CF6 0%,
                #38BDF8 50%,
                #F472B6 100%
            );
            box-shadow:
                0 0 12px rgba(139, 92, 246, 0.42),
                0 0 18px rgba(56, 189, 248, 0.22);
        }

        .st-key-patient_cards div[data-testid="stNumberInput"],
        .st-key-patient_cards div[data-testid="stSelectbox"] {
            margin-bottom: 0.45rem;
        }

        .st-key-patient_cards div[data-baseweb="input"],
        .st-key-patient_cards div[data-baseweb="select"] > div {
            background-color: rgba(246, 248, 252, 0.94);
            border-radius: 15px;
        }

        @media (max-width: 768px) {
            .st-key-patient_cards
            div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"] {
                min-height: auto;
            }
        }

        /* Métricas propias */
        .metric-card {
            background: linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%);
            border: 1px solid #E5E7EB;
            border-radius: 22px;
            padding: 22px 22px;
            box-shadow: 0px 12px 28px rgba(31, 41, 55, 0.055);
            min-height: 130px;
        }

        .metric-label {
            color: #6B7280;
            font-size: 0.86rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #111827;
            font-size: 1.85rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .metric-help {
            color: #6B7280;
            font-size: 0.82rem;
            margin-top: 8px;
            line-height: 1.4;
        }

        .accent-blue {
            color: #4F6EF7;
        }

        .accent-purple {
            color: #7C5CFC;
        }

        .accent-cyan {
            color: #00AFC6;
        }


        /* Distribución visual de probabilidades */
        .probability-panel {
            position: relative;
            overflow: hidden;
            margin: 0.35rem 0 1.8rem;
            padding: 2rem 2.1rem 2.15rem;
            border: 1px solid rgba(203, 213, 225, 0.82);
            border-radius: 28px;
            background:
                radial-gradient(
                    circle at 92% 8%,
                    rgba(244, 114, 182, 0.11),
                    transparent 24%
                ),
                radial-gradient(
                    circle at 7% 6%,
                    rgba(56, 189, 248, 0.10),
                    transparent 25%
                ),
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98) 0%,
                    rgba(248, 250, 255, 0.96) 100%
                );
            box-shadow:
                0 18px 44px rgba(31, 41, 55, 0.07),
                0 8px 22px rgba(79, 70, 229, 0.05);
        }

        .probability-panel::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(
                90deg,
                #8B5CF6 0%,
                #38BDF8 50%,
                #F472B6 100%
            );
        }

        .probability-kicker {
            margin-bottom: 0.45rem;
            color: #7C5CFC;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .probability-intro {
            max-width: 870px;
            margin: 0.72rem 0 1.65rem;
            color: #5F697B;
            font-size: 1.06rem;
            line-height: 1.62;
        }

        .probability-list {
            display: grid;
            gap: 0.95rem;
        }

        .probability-item {
            padding: 1.05rem 1.15rem 1.15rem;
            border: 1px solid rgba(226, 232, 240, 0.95);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 8px 20px rgba(31, 41, 55, 0.035);
        }

        .probability-item.is-main {
            border-color: rgba(139, 92, 246, 0.34);
            background:
                linear-gradient(
                    135deg,
                    rgba(139, 92, 246, 0.075),
                    rgba(56, 189, 248, 0.045),
                    rgba(244, 114, 182, 0.06)
                ),
                rgba(255, 255, 255, 0.92);
            box-shadow:
                0 12px 26px rgba(109, 74, 255, 0.08),
                inset 0 0 0 1px rgba(255, 255, 255, 0.7);
        }

        .probability-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.82rem;
        }

        .probability-name-wrap {
            min-width: 0;
        }

        .probability-name-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
        }

        .probability-name {
            color: #172033;
            font-size: 1.02rem;
            font-weight: 820;
        }

        .probability-description {
            margin-top: 0.2rem;
            color: #778195;
            font-size: 0.84rem;
            line-height: 1.4;
        }

        .probability-main-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.55rem;
            border: 1px solid rgba(139, 92, 246, 0.18);
            border-radius: 999px;
            background: rgba(139, 92, 246, 0.09);
            color: #7048D7;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .probability-value {
            flex: 0 0 auto;
            min-width: 86px;
            text-align: right;
            color: #111827;
            font-size: 1.28rem;
            font-weight: 850;
            letter-spacing: -0.02em;
        }

        .probability-track {
            position: relative;
            height: 14px;
            overflow: hidden;
            border: 1px solid rgba(226, 232, 240, 0.92);
            border-radius: 999px;
            background: rgba(235, 239, 246, 0.88);
            box-shadow: inset 0 2px 4px rgba(100, 116, 139, 0.08);
        }

        .probability-fill {
            position: relative;
            height: 100%;
            min-width: 5px;
            border-radius: inherit;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.18);
        }

        .probability-fill::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.05),
                rgba(255, 255, 255, 0.34),
                rgba(255, 255, 255, 0.08)
            );
        }

        .probability-fill.no-alzheimer {
            background: linear-gradient(90deg, #38BDF8, #60A5FA);
        }

        .probability-fill.early {
            background: linear-gradient(90deg, #5B78F6, #8B5CF6);
        }

        .probability-fill.moderate {
            background: linear-gradient(90deg, #8B5CF6, #D946EF);
        }

        .probability-fill.severe {
            background: linear-gradient(90deg, #D946EF, #F472B6);
        }

        .probability-fill.other {
            background: linear-gradient(90deg, #8B5CF6, #38BDF8, #F472B6);
        }

        .probability-note {
            margin-top: 1.3rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(226, 232, 240, 0.86);
            color: #7A8496;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        @media (max-width: 640px) {
            .probability-panel {
                padding: 1.55rem 1.15rem 1.5rem;
            }

            .probability-heading {
                font-size: 1.55rem;
            }

            .probability-intro {
                font-size: 0.98rem;
            }

            .probability-topline {
                align-items: flex-start;
            }

            .probability-value {
                min-width: 72px;
                font-size: 1.12rem;
            }
        }


        /* Panel unificado del análisis de imagen */
        .st-key-image_analysis_panel {
            margin-top: 0.4rem;
            margin-bottom: 1.6rem;
            padding: 1.9rem 2rem 2rem;
            border: 1px solid rgba(203, 213, 225, 0.88);
            border-radius: 28px;
            background:
                radial-gradient(
                    circle at 92% 8%,
                    rgba(244, 114, 182, 0.10),
                    transparent 24%
                ),
                radial-gradient(
                    circle at 7% 6%,
                    rgba(56, 189, 248, 0.09),
                    transparent 25%
                ),
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98) 0%,
                    rgba(248, 250, 255, 0.96) 100%
                );
            box-shadow:
                0 18px 44px rgba(31, 41, 55, 0.07),
                0 8px 22px rgba(79, 70, 229, 0.05);
        }

        .analysis-kicker {
            margin-bottom: 0.45rem;
            color: #7C5CFC;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .analysis-heading {
            margin: 0;
            color: #14213A;
            font-size: 1.75rem;
            font-weight: 850;
            line-height: 1.18;
        }

        .analysis-intro {
            margin: 0.72rem 0 1.45rem;
            color: #5F697B;
            font-size: 1.03rem;
            line-height: 1.62;
        }

        .analysis-divider {
            height: 1px;
            margin: 1.15rem 0 1.35rem;
            background: linear-gradient(90deg, transparent, #D5DEEA, transparent);
        }

        .analysis-note-card {
            border-radius: 20px;
            padding: 1rem 1.1rem;
            margin-top: 1rem;
            line-height: 1.6;
            font-size: 0.98rem;
        }

        .analysis-note-card.info {
            background: rgba(238, 244, 255, 0.95);
            border: 1px solid #D7E3FF;
            color: #2E4DA7;
        }

        .analysis-note-card.warning {
            background: rgba(255, 248, 230, 0.95);
            border: 1px solid #F5D98B;
            color: #7A5600;
        }

        /* Avisos */
        .soft-warning {
            background: #FFF8E6;
            border: 1px solid #F5D98B;
            color: #6B4E00;
            border-radius: 18px;
            padding: 16px 18px;
            font-size: 0.95rem;
            line-height: 1.55;
            margin-top: 12px;
        }

        .soft-info {
            background: #EEF4FF;
            border: 1px solid #D7E3FF;
            color: #2E4DA7;
            border-radius: 18px;
            padding: 16px 18px;
            font-size: 0.95rem;
            line-height: 1.55;
            margin-top: 12px;
        }

        .soft-success {
            background: #EAFBF8;
            border: 1px solid #B7EFE6;
            color: #056C61;
            border-radius: 18px;
            padding: 16px 18px;
            font-size: 0.95rem;
            line-height: 1.55;
            margin-top: 12px;
        }

        /* Botón principal */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #4F6EF7 0%, #35C6D9 100%);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 0.9rem 1.6rem;
            font-size: 1rem;
            font-weight: 800;
            box-shadow: 0px 12px 28px rgba(79, 110, 247, 0.28);
            transition: all 0.2s ease;
            width: 100%;
        }

        div.stButton > button:first-child:hover {
            transform: translateY(-1px);
            box-shadow: 0px 16px 34px rgba(79, 110, 247, 0.35);
        }

        /* Inputs */
        div[data-baseweb="input"] input {
            border-radius: 14px;
        }

        div[data-baseweb="select"] {
            border-radius: 14px;
        }

        /* Separador */
        .thin-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #CBD5E1, transparent);
            margin: 24px 0px;
        }

        /* Aviso médico final */
        .medical-notice-panel {
            position: relative;
            overflow: hidden;
            margin-top: 1.1rem;
            margin-bottom: 0.8rem;
            padding: 1.85rem 2rem 1.95rem;

            /* Borde rojo pastel */
            border: 1px solid rgba(248, 180, 180, 0.95);

            border-radius: 28px;

            /* Fondo rojo pastel muy suave */
            background:
                radial-gradient(
                    circle at 95% 10%,
                    rgba(248, 113, 113, 0.10),
                    transparent 24%
                ),
                linear-gradient(
                    145deg,
                    rgba(255, 247, 247, 0.98) 0%,
                    rgba(255, 235, 235, 0.98) 100%
                );

            box-shadow: 0 12px 30px rgba(185, 70, 70, 0.06);
        }

        .medical-notice-panel::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;

            /* Línea superior roja */
            background: linear-gradient(
                90deg,
                #F8B4B4 0%,
                #F08080 50%,
                #E96B6B 100%
            );
        }

        .medical-notice-kicker {
            margin-bottom: 0.45rem;
            color: #B54747;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .medical-notice-title {
            margin: 0 0 0.7rem 0;
            color: #8F3030;
            font-size: 1.55rem;
            font-weight: 850;
            line-height: 1.18;
        }

        .medical-notice-text {
            color: #9E4040;
            font-size: 1.03rem;
            line-height: 1.68;
            max-width: 1020px;
        }
        /* Footer */
        .footer-note {
            text-align: center;
            color: #6B7280;
            font-size: 0.88rem;
            margin-top: 34px;
        }

        /* Ajustes imágenes */
        img {
            border-radius: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARGA Y ENTRENAMIENTO DEL MODELO
# ============================================================

@st.cache_resource(show_spinner=False)
def load_predictor():
    """
    Genera el dataset, entrena el modelo y devuelve el predictor.

    Streamlit guarda el resultado en caché para evitar repetir todo el
    proceso cada vez que el usuario modifica un campo del formulario.
    """
    return build_predictor(regenerate_dataset=True)


predictor = load_predictor()


# ============================================================
# HERO SUPERIOR
# ============================================================

def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return None

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    extension = os.path.splitext(image_path)[1].lower().replace(".", "")

    if extension == "jpg":
        extension = "jpeg"

    return f"data:image/{extension};base64,{encoded}"

brain_image_src = get_image_base64(BRAIN_IMAGE_PATH)

hero_left, hero_right = st.columns([1.55, 1])

with hero_left:
    st.markdown(
        """
        <div class="hero-kicker">Sistema predictivo experimental</div>
        <div class="hero-title">
            Detección temprana de <span>Alzheimer</span>
        </div>
        <div class="hero-subtitle">
            Aplicación orientativa basada en biomarcadores clínicos, factores genéticos
            y análisis visual complementario de imagen cerebral. El sistema estima una
            etapa probable mediante Machine Learning y permite adjuntar una imagen
            para obtener un comentario visual adicional.
        </div>
        <span class="hero-badge">Machine Learning</span>
        <span class="hero-badge">Biomarcadores</span>
        <span class="hero-badge">Imagen cerebral opcional</span>
        """,
        unsafe_allow_html=True
    )

with hero_right:
    if brain_image_src:
        st.markdown(
            f"""
            <div class="hero-visual">
                <img src="{brain_image_src}" class="hero-brain-image">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="hero-visual">
                <div class="brain-icon">🧠</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# DATOS DEL PACIENTE
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Datos del paciente</div>
        <div class="section-subtitle">
            Introduce las variables utilizadas por el modelo predictivo. Estos datos
            constituyen la base principal de la estimación.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.container(key="patient_cards"):
    clinical_col, genetic_col = st.columns(2, gap="large")

    with clinical_col:
        st.markdown(
            """
            <div class="patient-card-title">Variables clínicas</div>
            """,
            unsafe_allow_html=True
        )

        age = st.number_input(
            "Edad",
            min_value=0,
            max_value=120,
            value=65,
            help="Edad del paciente en años.",
            key="patient_age"
        )

        mmse = st.number_input(
            "Puntuación MMSE",
            min_value=0,
            max_value=30,
            value=25,
            help=(
                "Puntuación del Mini-Mental State Examination. "
                "Valores más bajos suelen indicar mayor deterioro cognitivo."
            ),
            key="patient_mmse"
        )

        hippocampus_volume = st.number_input(
            "Volumen total del hipocampo (mm³, ambos hemisferios)",
            min_value=5000,
            max_value=8000,
            value=7000,
            step=50,
            help=(
                "Volumen total aproximado del hipocampo expresado "
                "en milímetros cúbicos."
            ),
            key="patient_hippocampus"
        )

    with genetic_col:
        st.markdown(
            """
            <div class="patient-card-title">Factores genéticos</div>
            """,
            unsafe_allow_html=True
        )

        apoe4_copies = st.selectbox(
            "Copias APOE e4",
            [0, 1, 2],
            help=(
                "Número de copias del alelo APOE e4 introducidas "
                "como variable del modelo."
            ),
            key="patient_apoe4"
        )

        app_mutation = st.selectbox(
            "Mutación APP",
            [0, 1],
            format_func=lambda value: "No" if value == 0 else "Sí",
            help="Indica si existe una mutación APP.",
            key="patient_app"
        )

        psen1_mutation = st.selectbox(
            "Mutación PSEN1",
            [0, 1],
            format_func=lambda value: "No" if value == 0 else "Sí",
            help="Indica si existe una mutación PSEN1.",
            key="patient_psen1"
        )

        psen2_mutation = st.selectbox(
            "Mutación PSEN2",
            [0, 1],
            format_func=lambda value: "No" if value == 0 else "Sí",
            help="Indica si existe una mutación PSEN2.",
            key="patient_psen2"
        )


# ============================================================
# IMAGEN CEREBRAL OPCIONAL
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Imagen cerebral opcional</div>
        <div class="section-subtitle">
            Puedes adjuntar una imagen cerebral en formato JPG, JPEG o PNG. La imagen
            no modifica todavía la probabilidad principal del modelo; se utiliza para
            generar un comentario visual complementario basado en zonas oscuras.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

image_col, image_info_col = st.columns([1.15, 1])

with image_col:
    uploaded_image = st.file_uploader(
        "Adjuntar TAC / MRI cerebral",
        type=["jpg", "jpeg", "png"],
        help="La imagen es opcional. Si no se adjunta, la app calculará la predicción solo con los datos clínicos."
    )

    if uploaded_image is not None:
        st.image(
            uploaded_image,
            caption="Imagen cerebral adjuntada",
            use_container_width=True
        )

with image_info_col:
    if uploaded_image is None:
        st.markdown(
            """
            <div class="soft-info">
                <strong>No se ha adjuntado ninguna imagen.</strong><br>
                El sistema realizará la predicción únicamente con los datos clínicos
                y genéticos introducidos.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="soft-success">
                <strong>Imagen cargada correctamente.</strong><br>
                Al calcular, se aplicará un preprocesamiento para eliminar el fondo
                negro exterior y analizar zonas oscuras dentro de la región útil.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="soft-warning">
            <strong>Nota importante:</strong><br>
            El análisis de imagen es experimental y orientativo. No equivale a un
            diagnóstico médico ni a una medición clínica de atrofia.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ACCIÓN PRINCIPAL
# ============================================================

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

button_col_1, button_col_2, button_col_3 = st.columns([1, 1.4, 1])

with button_col_2:
    calculate = st.button("Calcular probabilidad")


# ============================================================
# RESULTADOS
# ============================================================

if calculate:

    patient = Patient(
        age,
        mmse,
        hippocampus_volume,
        apoe4_copies,
        app_mutation,
        psen1_mutation,
        psen2_mutation
    )

    prediction, max_probability, probability_dict = predictor.predict_stage(patient)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Resultado de la predicción</div>
            <div class="section-subtitle">
                Resultado obtenido a partir de las variables clínicas y genéticas
                introducidas en el formulario.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    age_value = int(age)
    reduction = max(age_value - 60, 0)

    with metric_1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Etapa estimada</div>
                <div class="metric-value accent-blue">{prediction}</div>
                <div class="metric-help">Clase principal devuelta por el modelo.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Probabilidad principal</div>
                <div class="metric-value accent-purple">{max_probability:.2f}%</div>
                <div class="metric-help">Probabilidad asociada a la clase estimada.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Edad introducida</div>
                <div class="metric-value">{age_value}</div>
                <div class="metric-help">Valor utilizado por el modelo predictivo.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Reducción estimada por edad</div>
                <div class="metric-value accent-cyan">{reduction}%</div>
                <div class="metric-help">A partir de los 60 años según la lógica implementada.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # PROBABILIDADES POR CLASE
    # ========================================================

    stage_display = {
        "No Alzheimer": {
            "label": "Sin indicios de Alzheimer",
            "description": "Perfil más compatible con ausencia de deterioro asociado.",
            "css_class": "no-alzheimer",
            "order": 0,
        },
        "Early": {
            "label": "Etapa inicial",
            "description": "Compatibilidad con cambios tempranos o leves.",
            "css_class": "early",
            "order": 1,
        },
        "Moderate": {
            "label": "Etapa moderada",
            "description": "Compatibilidad con un nivel intermedio de alteración.",
            "css_class": "moderate",
            "order": 2,
        },
        "Severe": {
            "label": "Etapa avanzada",
            "description": "Compatibilidad con un perfil de alteración más pronunciada.",
            "css_class": "severe",
            "order": 3,
        },
    }

    probability_rows = []

    for stage, probability in probability_dict.items():
        stage_name = str(stage)
        stage_info = stage_display.get(
            stage_name,
            {
                "label": stage_name,
                "description": "Clase adicional contemplada por el modelo.",
                "css_class": "other",
                "order": 99,
            }
        )

        percentage = max(0.0, min(float(probability) * 100, 100.0))

        probability_rows.append(
            {
                "label": stage_info["label"],
                "description": stage_info["description"],
                "css_class": stage_info["css_class"],
                "order": stage_info["order"],
                "percentage": percentage,
                "is_main": stage_name == str(prediction),
            }
        )

    probability_rows.sort(key=lambda row: row["order"])

    probability_items_html = ""

    for row in probability_rows:
        item_class = (
            "probability-item is-main"
            if row["is_main"]
            else "probability-item"
        )

        badge_html = (
            '<span class="probability-main-badge">Resultado principal</span>'
            if row["is_main"]
            else ""
        )

        probability_items_html += (
            f'<div class="{item_class}">'
            '<div class="probability-topline">'
            '<div class="probability-name-wrap">'
            '<div class="probability-name-row">'
            f'<span class="probability-name">{row["label"]}</span>'
            f'{badge_html}'
            '</div>'
            f'<div class="probability-description">{row["description"]}</div>'
            '</div>'
            f'<div class="probability-value">{row["percentage"]:.2f}%</div>'
            '</div>'
            '<div class="probability-track" '
            'role="progressbar" '
            f'aria-valuenow="{row["percentage"]:.2f}" '
            'aria-valuemin="0" '
            'aria-valuemax="100" '
            f'aria-label="{row["label"]}">'
            f'<div class="probability-fill {row["css_class"]}" '
            f'style="width: {row["percentage"]:.2f}%;"></div>'
            '</div>'
            '</div>'
        )

    probability_panel_html = (
        '<section class="probability-panel">'
        '<div class="probability-kicker">Comparación del modelo</div>'
        '<div class="section-title">Probabilidad estimada por etapa</div>'
        '<p class="probability-intro">'
        'Distribución de probabilidades generada por el modelo para cada clase.'
        '</p>'
        '<div class="probability-list">'
        f'{probability_items_html}'
        '</div>'
        '<div class="probability-note">'
        'Estos porcentajes representan la confianza relativa del modelo entre sus '
        'clases y no equivalen a una probabilidad clínica real ni a un diagnóstico.'
        '</div>'
        '</section>'
    )   

    st.markdown(
        probability_panel_html,
        unsafe_allow_html=True
    )


    # ========================================================
    # ANÁLISIS DE IMAGEN OPCIONAL
    # ========================================================

    with st.container(key="image_analysis_panel"):
        st.markdown(
            """
            <div class="analysis-kicker">Análisis complementario</div>
            <div class="analysis-heading">Análisis visual complementario</div>
            <div class="analysis-intro">
                Esta sección solo utiliza la imagen adjuntada, si existe. El resultado
                no modifica la predicción principal del modelo.
            </div>
            """,
            unsafe_allow_html=True
        )

        if uploaded_image is not None:
            temp_image_path = None

            try:
                file_extension = os.path.splitext(uploaded_image.name)[1]

                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                    temp_file.write(uploaded_image.getbuffer())
                    temp_image_path = temp_file.name

                # 1. Cargar imagen
                brain_image = BrainImage(temp_image_path)
                brain_image.load()

                # 2. Eliminar fondo exterior conservando zonas oscuras internas
                preprocessor = BrainImagePreprocessor(brain_image)
                preprocessed_result = preprocessor.preprocess(black_threshold=10)

                brain_mask = preprocessed_result["brain_mask"]

                # 3. Analizar zonas oscuras dentro de la región útil
                analyzer = BrainImageAnalyzer(
                    brain_image=brain_image,
                    brain_mask=brain_mask
                )

                image_result = analyzer.analyze_dark_areas(threshold=50)

                analysis_metric_1, analysis_metric_2 = st.columns(2)

                with analysis_metric_1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Zonas oscuras detectadas</div>
                            <div class="metric-value accent-blue">{image_result['dark_percentage']}%</div>
                            <div class="metric-help">
                                Porcentaje calculado dentro de la región útil de la imagen.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with analysis_metric_2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Píxeles analizados</div>
                            <div class="metric-value">{image_result['total_pixels_analyzed']}</div>
                            <div class="metric-help">
                                Píxeles incluidos tras eliminar el fondo exterior.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"""
                    <div class="analysis-note-card info">
                        <strong>Interpretación del análisis:</strong><br>
                        {image_result["comment"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <div class="analysis-note-card warning">
                        El porcentaje de zonas oscuras no representa un porcentaje de Alzheimer
                        ni un porcentaje directo de atrofia. Solo indica qué parte de la región
                        útil presenta valores de gris bajos según el umbral aplicado.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="analysis-divider"></div>',
                    unsafe_allow_html=True
                )

                with st.expander("Ver preprocesamiento de la imagen"):
                    pre_col_1, pre_col_2, pre_col_3 = st.columns(3)

                    with pre_col_1:
                        st.image(
                            preprocessed_result["background_mask"],
                            caption="Fondo negro exterior detectado",
                            use_container_width=True,
                            clamp=True
                        )

                    with pre_col_2:
                        st.image(
                            preprocessed_result["brain_mask"],
                            caption="Región útil conservada",
                            use_container_width=True,
                            clamp=True
                        )

                    with pre_col_3:
                        st.image(
                            preprocessed_result["cleaned_image"],
                            caption="Imagen sin fondo exterior",
                            use_container_width=True,
                            clamp=True
                        )

            except Exception as e:
                st.error(f"No se pudo analizar la imagen: {str(e)}")

            finally:
                if temp_image_path and os.path.exists(temp_image_path):
                    os.remove(temp_image_path)

        else:
            st.markdown(
                """
                <div class="analysis-note-card info">
                    No se ha adjuntado imagen cerebral, por lo que no se realiza análisis visual.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # AVISO MÉDICO FINAL
    # ========================================================

    st.markdown(
        """
        <section class="medical-notice-panel">
            <div class="medical-notice-kicker">Importante</div>
            <div class="medical-notice-title">Aviso médico</div>
            <div class="medical-notice-text">
                Este resultado es únicamente <strong>orientativo</strong> y no sustituye en ningún caso
                una valoración médica profesional, un diagnóstico clínico ni una prueba especializada.
                La aplicación ha sido desarrollada con <strong>finalidad académica y experimental</strong>,
                por lo que sus resultados deben interpretarse solo como apoyo informativo.
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        Trabajo Fin de Grado · Informática aplicada a la neurociencia · Modelo predictivo para Alzheimer
    </div>
    """,
    unsafe_allow_html=True
)