from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


class ModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=500,
            max_depth=10,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced"
        )

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        print(f"Precisión del modelo: {accuracy * 100:.2f}%")

        return self.model