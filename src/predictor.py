class Predictor:
    def __init__(self, model):
        self.model = model

    def predict_stage(self, patient):
        data = patient.to_dataframe()

        prediction = self.model.predict(data)[0]
        probabilities = self.model.predict_proba(data)[0]
        classes = self.model.classes_

        probability_dict = dict(zip(classes, probabilities))
        max_probability = max(probabilities) * 100

        return prediction, max_probability, probability_dict