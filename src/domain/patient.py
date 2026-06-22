import pandas as pd


class Patient:
    def __init__(
        self,
        age,
        mmse,
        hippocampus_volume,
        apoe4_copies,
        app_mutation,
        psen1_mutation,
        psen2_mutation
    ):
        self.age = age
        self.mmse = mmse
        self.hippocampus_volume = hippocampus_volume
        self.apoe4_copies = apoe4_copies
        self.app_mutation = app_mutation
        self.psen1_mutation = psen1_mutation
        self.psen2_mutation = psen2_mutation

    def calculate_age_reduction(self):
        if self.age <= 60:
            return 0
        return self.age - 60

    def to_dataframe(self):
        return pd.DataFrame([[
            self.age,
            self.mmse,
            self.hippocampus_volume,
            self.calculate_age_reduction(),
            self.apoe4_copies,
            self.app_mutation,
            self.psen1_mutation,
            self.psen2_mutation
        ]], columns=[
            "age",
            "mmse",
            "hippocampus_volume",
            "hippocampus_age_reduction",
            "apoe4_copies",
            "app_mutation",
            "psen1_mutation",
            "psen2_mutation"
        ])