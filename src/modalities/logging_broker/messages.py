from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar


class MessageTypes(Enum):
    HIGH_LEVEL_PROGRESS_UPDATE = "HIGH_LEVEL_PROGRESS_UPDATE"
    BATCH_PROGRESS_UPDATE = "PROGRESS_UPDATE"
    ERROR_MESSAGE = "ERROR_MESSAGE"
    EVALUATION_RESULT = "EVALUATION_RESULT"


T = TypeVar("T")


@dataclass
class Message(Generic[T]):
    """An object representing a message."""

    message_type: MessageTypes
    payload: T
    global_rank: int = 0
    local_rank: int = 0


class ExperimentStatus(Enum):
    TRAIN = "TRAIN"
    EVALUATION = "EVALUATION"


@dataclass
class BatchProgressUpdate:
    """Object holding the state of the current batch computation progress."""

    global_train_sample_id: int  # current sample id in the training dataloader (summed over all ranks).
    global_dataset_sample_id: int  # current sample id in the respective dataloader (summed over all ranks).
    # Note: in case of ExperimentState.TRAIN, dataset_batch_id=global_train_batch_id
    experiment_status: ExperimentStatus
    dataloader_tag: str
