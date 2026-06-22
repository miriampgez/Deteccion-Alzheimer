from pathlib import Path

from data.data_loader import DataLoader
from data.generate_dataset import generate_dataset
from model.model_trainer import ModelTrainer
from model.predictor import Predictor


# Carpeta src
SRC_DIR = Path(__file__).resolve().parent

# Ruta absoluta del dataset
DATASET_PATH = SRC_DIR / "data" / "alzheimer_data.csv"


def build_predictor(regenerate_dataset=True):
    """
    Genera el dataset, entrena el modelo y devuelve el predictor.
    """

    if regenerate_dataset or not DATASET_PATH.exists():
        generate_dataset(
            output_path=DATASET_PATH,
            number_of_patients=5000,
            forced_repetitions=80,
            random_seed=42
        )

    loader = DataLoader(DATASET_PATH)

    data = loader.load_data()

    X, y = loader.split_features_and_target(data)

    trainer = ModelTrainer()
    model = trainer.train_model(X, y)

    return Predictor(model)


def main():
    build_predictor(regenerate_dataset=True)
    print("Sistema preparado correctamente.")


if __name__ == "__main__":
    main()