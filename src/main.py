from data_loader import DataLoader
from model_trainer import ModelTrainer
from predictor import Predictor
from interface import AlzheimerInterface


def main():
    loader = DataLoader("alzheimer_data.csv")
    data = loader.load_data()

    X, y = loader.split_features_and_target(data)

    trainer = ModelTrainer()
    model = trainer.train_model(X, y)

    predictor = Predictor(model)

    interface = AlzheimerInterface(predictor)
    interface.run()


if __name__ == "__main__":
    main()