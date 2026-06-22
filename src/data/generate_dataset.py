import os
import random

import pandas as pd


def calculate_stage(
    age,
    mmse,
    hippocampus,
    apoe4,
    app,
    psen1,
    psen2
):
    score = 0

    # =========================
    # MMSE
    # =========================

    if mmse >= 27:
        score += 0
    elif mmse >= 24:
        score += 0.5
    elif mmse >= 12:
        score += 1.5
    elif mmse >= 9:
        score += 2.5
    else:
        score += 3.5

    # =========================
    # VOLUMEN DEL HIPOCAMPO
    # =========================

    if hippocampus >= 7000:
        score += 0
    elif hippocampus >= 6200:
        score += 1
    elif hippocampus >= 5500:
        score += 2
    else:
        score += 3

    # =========================
    # EDAD
    # =========================

    if age < 60:
        score += 0
    elif age < 70:
        score += 1
    elif age < 80:
        score += 2
    else:
        score += 3

    # =========================
    # GENÉTICA
    # =========================

    genetic_score = 0

    if apoe4 == 1:
        genetic_score += 0.8
    elif apoe4 == 2:
        genetic_score += 1.8

    if app == 1:
        genetic_score += 1.2

    if psen1 == 1:
        genetic_score += 1.0

    if psen2 == 1:
        genetic_score += 0.8

    gene_count = 0

    if apoe4 > 0:
        gene_count += 1

    if app == 1:
        gene_count += 1

    if psen1 == 1:
        gene_count += 1

    if psen2 == 1:
        gene_count += 1

    if gene_count >= 3:
        genetic_score += 1.0

    if gene_count == 4:
        genetic_score += 1.5

    score += genetic_score

    # =========================
    # CLASIFICACIÓN FINAL
    # =========================

    if score < 3:
        return "No Alzheimer"

    if score < 5:
        return "Early"

    if score < 7:
        return "Moderate"

    return "Severe"


def generate_mmse(age):
    mmse_random = random.random()

    if age < 50:
        if mmse_random < 0.90:
            return random.randint(27, 30)

        return random.randint(24, 26)

    if age < 70:
        if mmse_random < 0.60:
            return random.randint(27, 30)

        if mmse_random < 0.85:
            return random.randint(24, 26)

        return random.randint(12, 24)

    if mmse_random < 0.30:
        return random.randint(27, 30)

    if mmse_random < 0.60:
        return random.randint(24, 26)

    if mmse_random < 0.85:
        return random.randint(12, 24)

    if mmse_random < 0.95:
        return random.randint(9, 12)

    return random.randint(5, 8)


def generate_genes():
    apoe4_random = random.random()

    if apoe4_random < 0.75:
        apoe4 = 0
    elif apoe4_random < 0.95:
        apoe4 = 1
    else:
        apoe4 = 2

    app = 1 if random.random() < 0.12 else 0
    psen1 = 1 if random.random() < 0.10 else 0
    psen2 = 1 if random.random() < 0.08 else 0

    return apoe4, app, psen1, psen2


def generate_hippocampus(age):
    hippocampus = random.randint(5000, 8000)

    if age > 60:
        reduction = (age - 60) * random.randint(20, 45)
        hippocampus -= reduction

    return max(5000, min(8000, hippocampus))


def create_patient_record(
    age,
    mmse,
    hippocampus_volume,
    apoe4_copies,
    app_mutation,
    psen1_mutation,
    psen2_mutation
):
    """
    Crea un paciente y calcula siempre su diagnóstico
    utilizando calculate_stage().
    """

    diagnosis_stage = calculate_stage(
        age,
        mmse,
        hippocampus_volume,
        apoe4_copies,
        app_mutation,
        psen1_mutation,
        psen2_mutation
    )

    return {
        "age": age,
        "mmse": mmse,
        "hippocampus_volume": hippocampus_volume,
        "apoe4_copies": apoe4_copies,
        "app_mutation": app_mutation,
        "psen1_mutation": psen1_mutation,
        "psen2_mutation": psen2_mutation,
        "diagnosis_stage": diagnosis_stage
    }


def generate_patient():
    age = random.randint(35, 90)

    mmse = generate_mmse(age)
    hippocampus = generate_hippocampus(age)
    apoe4, app, psen1, psen2 = generate_genes()

    return create_patient_record(
        age=age,
        mmse=mmse,
        hippocampus_volume=hippocampus,
        apoe4_copies=apoe4,
        app_mutation=app,
        psen1_mutation=psen1,
        psen2_mutation=psen2
    )


def generate_dataset(
    output_path,
    number_of_patients=5000,
    forced_repetitions=80,
    random_seed=42
):
    """
    Genera el dataset completo y lo guarda en output_path.

    Devuelve también el DataFrame generado.
    """

    # Permite generar siempre el mismo dataset.
    # Esto es recomendable para que los resultados del TFG
    # sean reproducibles.
    random.seed(random_seed)

    patients = []

    # =========================
    # PACIENTES GENERALES
    # =========================

    for _ in range(number_of_patients):
        patients.append(generate_patient())

    # =========================
    # CASOS FORZADOS
    # =========================

    forced_profiles = [
        {
            "age": 35,
            "mmse": 25,
            "hippocampus_volume": 6500,
            "apoe4_copies": 2,
            "app_mutation": 1,
            "psen1_mutation": 1,
            "psen2_mutation": 1
        },
        {
            "age": 35,
            "mmse": 24,
            "hippocampus_volume": 6400,
            "apoe4_copies": 2,
            "app_mutation": 1,
            "psen1_mutation": 1,
            "psen2_mutation": 1
        },
        {
            "age": 40,
            "mmse": 23,
            "hippocampus_volume": 6300,
            "apoe4_copies": 2,
            "app_mutation": 1,
            "psen1_mutation": 1,
            "psen2_mutation": 1
        },
        {
            "age": 45,
            "mmse": 22,
            "hippocampus_volume": 6200,
            "apoe4_copies": 2,
            "app_mutation": 1,
            "psen1_mutation": 1,
            "psen2_mutation": 1
        },
        {
            "age": 35,
            "mmse": 25,
            "hippocampus_volume": 6500,
            "apoe4_copies": 1,
            "app_mutation": 1,
            "psen1_mutation": 1,
            "psen2_mutation": 0
        },
        {
            "age": 35,
            "mmse": 25,
            "hippocampus_volume": 6500,
            "apoe4_copies": 1,
            "app_mutation": 1,
            "psen1_mutation": 0,
            "psen2_mutation": 1
        },
        {
            "age": 35,
            "mmse": 25,
            "hippocampus_volume": 6500,
            "apoe4_copies": 1,
            "app_mutation": 1,
            "psen1_mutation": 0,
            "psen2_mutation": 0
        }
    ]

    for _ in range(forced_repetitions):
        for profile in forced_profiles:
            patients.append(
                create_patient_record(**profile)
            )

    dataframe = pd.DataFrame(patients)

    # Convierte la ruta en absoluta y crea la carpeta si fuera necesario.
    absolute_output_path = os.path.abspath(output_path)
    output_directory = os.path.dirname(absolute_output_path)

    os.makedirs(output_directory, exist_ok=True)

    dataframe.to_csv(
        absolute_output_path,
        index=False
    )

    print(
        f"Dataset generado correctamente: "
        f"{absolute_output_path}"
    )

    print("\nDistribución de clases:")
    print(dataframe["diagnosis_stage"].value_counts())

    return dataframe


if __name__ == "__main__":
    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    default_dataset_path = os.path.join(
        project_root,
        "alzheimer_data.csv"
    )

    generate_dataset(default_dataset_path)