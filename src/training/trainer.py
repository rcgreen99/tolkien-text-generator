import torch
import torch.nn as nn
from torch.optim import AdamW

from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

"""
NOTE: THIS CLASS IS NOT BEING USED AT THE MOMENT

Instead, I'm using the transformers.Trainer class
in src/training/training_session.py

This class has not been tested and doesn't work
as a substitute.
"""


class Trainer:
    def __init__(
        self,
        model,
        train_dataloader,
        val_dataloader,
        learning_rate,
        epochs,
    ):
        self.model = model
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.learning_rate = learning_rate
        self.epochs = epochs

        self.criterion = nn.CrossEntropyLoss()  # look into this
        self.optimizer = AdamW(
            self.model.parameters(), lr=self.learning_rate
        )  # use AdamW?

        use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if use_cuda else "cpu")
        if use_cuda:
            self.model = self.model.cuda()
            self.criterion = self.criterion.cuda()

    def fit(self):
        """
        Train and validate the model for self.epochs
        """
        print("Training...")
        for epoch in range(self.epochs):
            print(f"Epoch {epoch + 1}/{self.epochs}")
            self.train()
            self.evaluate()
            self.save_model_state(f"models/model_e{epoch}.pth")

    def train(self):
        """
        Train the model for one epoch
        """
        self.model.train()

        progress = self.create_progress_bar()
        with progress:
            task = progress.add_task(
                "Training",
                loop_type="Train",
                loss=0,
                # accuracy=0,
                total=len(self.train_dataloader),
            )

            # training loop
            running_loss = 0
            for batch_idx, batch in enumerate(self.train_dataloader):
                input_ids, attention_mask, targets = self.unpack_batch(batch)

                # forward and backward passes
                self.optimizer.zero_grad()
                # outputs = self.model(input_ids, attention_mask=attention_mask)
                outputs = self.model(
                    input_ids=input_ids, attention_mask=attention_mask, labels=targets
                )
                print(type(outputs))
                loss, running_loss = self.calculate_loss(outputs, targets, running_loss)
                loss.backward()
                self.optimizer.step()

                # update progress bar
                progress.update(
                    task,
                    advance=1,
                    description=f"Training   {batch_idx+1}/{len(self.train_dataloader)}",
                    loss=running_loss / (batch_idx + 1),
                )

    def evaluate(self):
        """
        Evaluate the model on the validation set
        """
        self.model.eval()

        progress = self.create_progress_bar()
        with progress:
            task = progress.add_task(
                "Validating",
                loop_type="Val",
                loss=0,
                # accuracy=0,
                total=len(self.val_dataloader),
            )
            with torch.no_grad():
                # validation loop
                running_loss = 0
                for batch_idx, batch in enumerate(self.val_dataloader):
                    input_ids, attention_mask, targets = self.unpack_batch(batch)

                    outputs = self.model(input_ids, attention_mask)

                    loss, running_loss = self.calculate_loss(
                        outputs, targets, running_loss
                    )

                    progress.update(
                        task,
                        advance=1,
                        description=f"Validating {batch_idx+1}/{len(self.val_dataloader)}",
                        loss=running_loss / (batch_idx + 1),
                        # accuracy=running_accuracy,
                    )

    def save_model_state(self, path):
        """
        Save model state to path
        """
        torch.save(self.model.state_dict(), path)

    def create_progress_bar(self):
        """
        Create a progress bar object
        Returns progress bar
        """
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TimeRemainingColumn(),
            "|",
            TextColumn("[red]{task.fields[loop_type]} Loss: {task.fields[loss]:.2f}"),
            "•",
            # TextColumn(
            #     "[yellow]{task.fields[loop_type]} Accuracy: {task.fields[accuracy]:.2f}"
            # ),
        )
        return progress

    def unpack_batch(self, batch):
        """
        Unpack batch into input_ids, attention_mask, and targets
        loads batch to device
        Return input_ids, attention_mask, and targets
        """
        input_ids = batch["input_ids"].to(self.device)
        attention_mask = batch["attention_mask"].to(self.device)
        # targets = batch["target"].to(self.device)
        targets = batch["input_ids"].to(self.device)
        return input_ids, attention_mask, targets

    def calculate_loss(self, outputs, targets, running_loss):
        """
        Calculate loss and running loss
        Return loss and running loss
        """
        # need to change this line =======================================
        loss = self.criterion(outputs, targets)
        running_loss = loss.item()
        return loss, running_loss

    # def calculate_accuracy(self, outputs, targets, batch_size, num_correct, i):
    #     """
    #     Calculate num_correct and running accuracy based on number of batches so far
    #     Return accuracy and num_correct
    #     """
    #     outputs = torch.round(outputs)
    #     num_correct += (outputs == targets.reshape(-1, 1)).float().sum()
    #     return 100 * num_correct / ((i + 1) * batch_size), num_correct
