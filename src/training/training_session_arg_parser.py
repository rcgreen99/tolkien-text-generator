from argparse import ArgumentParser


class TrainingSessionArgParser:
    def __init__(self):
        self.parser = ArgumentParser()
        self.add_args()

    def add_args(self):
        self.parser.add_argument(
            "--filename",
            type=str,
            default="data/lotr-paragraphs.json",
            help="Path to the dataset",
        )
        self.parser.add_argument(
            "--model_name",
            type=str,
            default="facebook/opt-350m",
            help="HuggingFace CausalLM pre-trained model to be fine tuned",
        )
        self.parser.add_argument(
            "--epochs",
            type=int,
            default=3,
            help="Number of epochs to train the model",
        )
        self.parser.add_argument(
            "--batch_size",
            type=int,
            default=32,
            help="Batch size to use for training",
        )
        self.parser.add_argument(
            "--learning_rate",
            type=float,
            default=2e-5,
            help="Learning rate to use for training",
        )

    def parse_args(self):
        return self.parser.parse_args()
