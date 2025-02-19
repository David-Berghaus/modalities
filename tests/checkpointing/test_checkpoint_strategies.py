from typing import List

import pytest

from src.modalities.checkpointing.checkpointing_strategies import SaveKMostRecentCheckpointsStrategy


@pytest.mark.parametrize(
    "k, saved_batch_id_checkpoints, checkpoints_to_delete, save_current",
    [
        # k value is 2. New checkpoint is created and the last one (in the example: [2]) is deleted.
        (2, [1, 2], [2], True),
        # k value is 0. No deletion of checkpoints.
        (0, [], [], False),
        # k value is 2, but there are currently only one checkpoint. Hence, no deletion.
        (2, [1], [], True),
        # k value is -1, therefore we want to keep all checkpoints without any deletion
        (-1, [3, 2, 1], [], True),
    ],
)
def test_checkpoint_strategy_k(
    k: int, saved_batch_id_checkpoints: List[int], checkpoints_to_delete: List[int], save_current: bool
) -> None:
    global_train_sample_id = 100
    checkpoint_strategy = SaveKMostRecentCheckpointsStrategy(k=k)
    checkpoint_strategy.saved_sample_id_checkpoints = saved_batch_id_checkpoints
    checkpoint_instruction = checkpoint_strategy.get_checkpoint_instruction(
        global_train_sample_id=global_train_sample_id
    )

    assert checkpoint_instruction.checkpoints_to_delete == checkpoints_to_delete
    assert checkpoint_instruction.save_current == save_current
