import pandas as pd


class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        data = pd.read_csv(self.file_path)

        data["hippocampus_age_reduction"] = data["age"].apply(
            lambda age: 0 if age <= 60 else age - 60
        )

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

        X = data[feature_columns]
        y = data["diagnosis_stage"]

        return X, y