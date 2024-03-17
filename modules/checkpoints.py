__version__ = "0.0.7"

from pathlib import Path
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
                "checkpoint_names": ("STRING", {"default": None, "multiline": True}),
            },
        }

    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),)
    RETURN_NAMES = ("ckpt_name",)
    FUNCTION = "get_checkpoint"

    CATEGORY = "DarkPrompt"

    def get_checkpoint(self, seed, use_for_iterations, checkpoint_names):
        data = {}
        try:
            with open(
                os.path.join(
                    folder_paths.temp_directory,
                    "darkpromptcheckpointrandomizer.json",
                ),
                "r",
            ) as data_file:
                data = json.loads(data_file.read())
        except FileNotFoundError:
            # Probably the first run
            pass

        if not "iteration" in data:
            data.update({"iteration": 0})

        if (
            data["iteration"] >= use_for_iterations
            or not "checkpoint" in data
            or not data["checkpoint"] in checkpoint_names.splitlines()
        ):
            data.update({"iteration": 0})
            random.seed(seed)
            # BUG: Do better here.  Read all the lines in individually, strip
            # them, remove empties, maybe even ditch comments like DarkPrompt
            # does
            data.update({"checkpoint": random.choice(checkpoint_names.splitlines())})

        data.update({"iteration": data["iteration"] + 1})

        # There appears to be a bug in ComfyUI when you pass the arg
        # --temp-directory /some/folder
        # folder_paths.temp_directory will actually contain /some/folder/temp
        # so just make sure it exists before trying to write to it
        Path(folder_paths.temp_directory).mkdir(parents=True, exist_ok=True)
        data_file = open(
            os.path.join(
                folder_paths.temp_directory, "darkpromptcheckpointrandomizer.json"
            ),
            "w",
        )
        data_file.write(json.dumps(data))
        print(data)

        return (data["checkpoint"],)
