from pathlib import Path

import pandas as pd


class DataLoader:

    REQUIRED_COLUMNS = {
        "age",
        "mmse",
        "hippocampus_volume",
        "apoe4_copies",
        "app_mutation",
        "psen1_mutation",
        "psen2_mutation",
        "diagnosis_stage"
    }

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def load_data(self):
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"No se ha encontrado el dataset: "
                f"{self.file_path}"
            )

        data = pd.read_csv(self.file_path)

        missing_columns = (
            self.REQUIRED_COLUMNS.difference(data.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas obligatorias en el dataset: "
                + ", ".join(sorted(missing_columns))
            )

        data["hippocampus_age_reduction"] = (
            data["age"] - 60
        ).clip(lower=0)

        return data

    def split_features_and_target(self, data):
        feature_columns = [
            "age",
            "mmse",
            "hippocampus_volume",
            "hippocampus_age_reduction",
            "apoe4_copies",
            "app_mutation",
            "psen1_mutation",
            "psen2_mutation"
        ]

        X = data[feature_columns].copy()
        y = data["diagnosis_stage"].copy()

        return X, y