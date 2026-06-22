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

@st.cache_resource
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
                <div class="hero-floating-card">
                    Análisis orientativo<br>
                    <strong>no diagnóstico</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="hero-visual">
                <div class="brain-icon">🧠</div>
                <div class="hero-floating-card">
                    Análisis orientativo<br>
                    <strong>no diagnóstico</strong>
                </div>
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

clinical_col, genetic_col = st.columns([1.2, 1])

with clinical_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="small-label">Variables clínicas</div>
        """,
        unsafe_allow_html=True
    )

    age = st.number_input(
        "Edad",
        min_value=0,
        max_value=120,
        value=65,
        help="Edad del paciente en años."
    )

    mmse = st.number_input(
        "Puntuación MMSE",
        min_value=0,
        max_value=30,
        value=25,
        help="Puntuación del Mini-Mental State Examination. Valores más bajos suelen indicar mayor deterioro cognitivo."
    )

    hippocampus_volume = st.number_input(
        "Volumen total del hipocampo (mm³, ambos hemisferios)",
        min_value=5000,
        max_value=8000,
        value=7000,
        step=50,
        help="Volumen total aproximado del hipocampo expresado en milímetros cúbicos."
    )

    st.markdown("</div>", unsafe_allow_html=True)


with genetic_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="small-label">Factores genéticos</div>
        """,
        unsafe_allow_html=True
    )

    apoe4_copies = st.selectbox(
        "Copias APOE e4",
        [0, 1, 2],
        help="Número de copias del alelo APOE e4 introducidas como variable del modelo."
    )

    app_mutation = st.selectbox(
        "Mutación APP",
        [0, 1],
        help="0 indica ausencia y 1 indica presencia de mutación APP."
    )

    psen1_mutation = st.selectbox(
        "Mutación PSEN1",
        [0, 1],
        help="0 indica ausencia y 1 indica presencia de mutación PSEN1."
    )

    psen2_mutation = st.selectbox(
        "Mutación PSEN2",
        [0, 1],
        help="0 indica ausencia y 1 indica presencia de mutación PSEN2."
    )

    st.markdown("</div>", unsafe_allow_html=True)


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

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Probabilidades por clase</div>
            <div class="section-subtitle">
                Distribución de probabilidades generada por el modelo para cada clase.
            </div>
        """,
        unsafe_allow_html=True
    )

    for stage, probability in probability_dict.items():
        percentage = probability * 100
        st.write(f"**{stage}** · {percentage:.2f}%")
        st.progress(float(probability))

    st.markdown("</div>", unsafe_allow_html=True)


    # ========================================================
    # ANÁLISIS DE IMAGEN OPCIONAL
    # ========================================================

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Análisis visual complementario</div>
            <div class="section-subtitle">
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

            image_metric_1, image_metric_2 = st.columns(2)

            with image_metric_1:
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

            with image_metric_2:
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
                <div class="soft-info">
                    <strong>Interpretación del análisis:</strong><br>
                    {image_result["comment"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="soft-warning">
                    El porcentaje de zonas oscuras no representa un porcentaje de Alzheimer
                    ni un porcentaje directo de atrofia. Solo indica qué parte de la región
                    útil presenta valores de gris bajos según el umbral aplicado.
                </div>
                """,
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
            <div class="soft-info">
                No se ha adjuntado imagen cerebral, por lo que no se realiza análisis visual.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # ========================================================
    # OBSERVACIONES FINALES
    # ========================================================

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Observaciones clínicas</div>
            <div class="section-subtitle">
                Información adicional generada por la aplicación a partir de los datos introducidos.
            </div>
        """,
        unsafe_allow_html=True
    )

    if reduction > 0:
        st.markdown(
            f"""
            <div class="soft-info">
                <strong>Reducción estimada del hipocampo por edad:</strong><br>
                Para la edad introducida se estima una reducción del {reduction}% a partir de los 60 años,
                según la lógica implementada en el sistema.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="soft-info">
                <strong>Reducción estimada del hipocampo por edad:</strong><br>
                No se aplica reducción por edad antes de los 60 años según la lógica implementada.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="soft-warning">
            <strong>Aviso médico:</strong><br>
            Este resultado es orientativo y no sustituye un diagnóstico médico.
            La aplicación tiene finalidad académica y experimental.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


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