from typing import Dict

from rich.console import Group
from rich.live import Live
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn
from rich.rule import Rule
from rich.text import Text

from modalities.logging_broker.messages import BatchProgressUpdate, ExperimentStatus, Message
from modalities.logging_broker.subscriber import MessageSubscriberIF


class DummyProgressSubscriber(MessageSubscriberIF[BatchProgressUpdate]):
    def consume_message(self, message: Message[BatchProgressUpdate]):
        pass


class RichProgressSubscriber(MessageSubscriberIF[BatchProgressUpdate]):
    """A subscriber object for the RichProgress observable."""

    def __init__(
        self,
        num_ranks: int,
        train_split_num_samples: Dict[str, int],
        eval_splits_num_samples: Dict[str, int],
    ) -> None:
        self.num_ranks = num_ranks

        # train split progress bar
        self.train_splits_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )
        self.train_split_task_ids = {}
        for split_key, split_num_samples in train_split_num_samples.items():
            task_id = self.train_splits_progress.add_task(description=split_key, total=split_num_samples)
            self.train_split_task_ids[split_key] = task_id

        # eval split progress bars
        self.eval_splits_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )
        self.eval_split_task_ids = {}
        for split_key, split_num_samples in eval_splits_num_samples.items():
            task_id = self.eval_splits_progress.add_task(description=split_key, total=split_num_samples)
            self.eval_split_task_ids[split_key] = task_id

        group = Group(
            Text(text="\n\n\n"),
            Rule(style="#AAAAAA"),
            Text(text="Training", style="blue"),
            self.train_splits_progress,
            Rule(style="#AAAAAA"),
            Text(text="Evaluation", style="blue"),
            self.eval_splits_progress,
        )

        live = Live(group)
        live.start()

    def consume_message(self, message: Message[BatchProgressUpdate]):
        """Consumes a message from a message broker."""
        batch_progress = message.payload

        if batch_progress.experiment_status == ExperimentStatus.TRAIN:
            task_id = self.train_split_task_ids[batch_progress.dataloader_tag]
            self.train_splits_progress.update(
                task_id=task_id,
                completed=batch_progress.global_train_sample_id + 1,
            )
        else:
            task_id = self.eval_split_task_ids[batch_progress.dataloader_tag]
            self.eval_splits_progress.update(
                task_id=task_id,
                completed=batch_progress.global_dataset_sample_id + 1,
            )
