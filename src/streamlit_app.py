import streamlit as st
from data_loader import DataLoader
from model_trainer import ModelTrainer
from predictor import Predictor
from patient import Patient


# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Detección de Alzheimer",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Detección temprana de Alzheimer")

st.write(
    "Introduce los datos clínicos del paciente para estimar una predicción orientativa."
)

# =========================
# CARGA Y ENTRENAMIENTO
# =========================
loader = DataLoader("alzheimer_data.csv")
data = loader.load_data()

X, y = loader.split_features_and_target(data)

trainer = ModelTrainer()
model = trainer.train_model(X, y)

predictor = Predictor(model)

# =========================
# INPUTS
# =========================
st.subheader("Datos del paciente")

age = st.number_input(
    "Edad",
    min_value=0,
    max_value=120,
    value=65
)

mmse = st.number_input(
    "Puntuación MMSE",
    min_value=0,
    max_value=30,
    value=25
)

hippocampus_volume = st.number_input(
    "Volumen total del hipocampo (mm³, ambos hemisferios)",
    min_value=5000,
    max_value=8000,
    value=7000,
    step=50
)

apoe4_copies = st.selectbox(
    "Copias APOE e4",
    [0, 1, 2]
)

app_mutation = st.selectbox(
    "Mutación APP",
    [0, 1]
)

psen1_mutation = st.selectbox(
    "Mutación PSEN1",
    [0, 1]
)

psen2_mutation = st.selectbox(
    "Mutación PSEN2",
    [0, 1]
)

# =========================
# BOTÓN DE PREDICCIÓN
# =========================
if st.button("Calcular probabilidad"):

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

    # =========================
    # RESULTADOS
    # =========================
    st.success(f"Etapa estimada: {prediction}")
    st.metric("Probabilidad principal", f"{max_probability:.2f}%")

    st.subheader("Probabilidades por clase")

    for stage, probability in probability_dict.items():
        st.write(f"{stage}: {probability * 100:.2f}%")
        st.progress(float(probability))

    # =========================
    # REDUCCIÓN POR EDAD (CORRECTO)
    # =========================
    age_value = int(age)
    reduction = max(age_value - 60, 0)

    st.write(f"Edad introducida: {age_value}")
    
    if reduction > 0:
        st.info(
            f"Reducción estimada del hipocampo por edad: {reduction}% "
            f"(a partir de los 60 años)."
        )
    else:
        st.info(
            "Reducción estimada del hipocampo por edad: 0% "
            "(no se aplica antes de los 60 años)."
        )

    # =========================
    # AVISO MÉDICO
    # =========================
    st.warning(
        "Este resultado es orientativo y no sustituye un diagnóstico médico."
    )