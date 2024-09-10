__version__ = "0.0.7"

from pathlib import Path
from .utils.darkdata import DarkData
import folder_paths
import glob
import logging
import os
import os.path
import random
import re
import json

logger = logging.getLogger(__name__)


class DarkCheckpointSwitcher(object):
    """
    Takes checkpoints as an input and allows you to manually switch between them
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint1": (
                    folder_paths.get_filename_list("checkpoints"),
                    {
                        "forceInput": True,
                    },
                ),
                "checkpoint2": (
                    folder_paths.get_filename_list("checkpoints"),
                    {
                        "forceInput": True,
                    },
                ),
                "use_checkpoint": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 2,
                    },
                ),
            },
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),)
    RETURN_NAMES = ("ckpt_name",)
    FUNCTION = "get_switched_checkpoint"

    CATEGORY = "DarkPrompt"

    def get_switched_checkpoint(self, checkpoint1, checkpoint2, use_checkpoint):
        if use_checkpoint == 1:
            return (checkpoint1,)
        else:
            return (checkpoint2,)


class DarkCheckpointRandomizer(object):
    """
    Handles randomizing checkpoints
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "forceInput": True,
                    },
                ),
                "use_for_iterations": ("INT", {"default": 10, "min": 1}),
                "checkpoint_names": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),)
    RETURN_NAMES = ("ckpt_name",)
    FUNCTION = "get_checkpoint"

    CATEGORY = "DarkPrompt"

    def get_checkpoint(self, seed, use_for_iterations, checkpoint_names):
        # In order to avoid random crashes, we need to validate that every file
        # exists.  This prevents someone from adding 'doesnotexist.safetensors'
        # in to the random list queueing up a bunch of jobs and coming back the
        # next morning to find that at some point we tried to use
        # doesnotexist.safetensors and everything crashed.
        checkpoints = []
        checkpoint = None
        for cpn in checkpoint_names.splitlines():
            if cpn.strip():
                if cpn.strip() in folder_paths.get_filename_list("checkpoints"):
                    checkpoints.append(cpn.strip())
                else:
                    logger.warn(
                        "%s is in your DarkCheckpointRandomizer but it does not exist in your checkpoints directory"
                        % (cpn)
                    )

        if not checkpoints:
            raise Exception(
                "You have no checkpoints that exist listed in your DarkCheckpointRandomizer"
            )

        with DarkData(filename="darkcheckpointrandomizer.json") as DFB:
            random.seed(seed)
            # make sure we have a checkpoint from the file or if it doesn't
            # exist from the random function
            checkpoint = DFB.get_key("checkpoint", random.choice(checkpoints))

            if (
                DFB.get_key("iteration", 0) >= use_for_iterations
                or checkpoint not in checkpoints
            ):
                # If we are over our iteration count or the checkpoint no
                # longer exists in the list due to the user removing it, set
                # the iteration back to 1, get a new checkpoint, and save it
                DFB.set_key("iteration", 1)
                checkpoint = random.choice(checkpoints)
            else:
                # If we aren't over our iteration count (or maybe this is our
                # first iteration, increment the iteration counter
                DFB.set_key("iteration", DFB.get_key("iteration", 0) + 1)

            # Set our current checkpoint as it may have changed
            DFB.set_key("checkpoint", checkpoint)

        print("Checkpoint: %s" % (checkpoint))

        return (checkpoint,)
