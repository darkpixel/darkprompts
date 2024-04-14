__version__ = "0.0.7"

from folder_paths import get_output_directory
from pathlib import Path
import folder_paths
import glob
import json
import logging
import os
import os.path
import random
import re

logger = logging.getLogger(__name__)


def get_full_path(prefix):
    """Normalize the prefix into a full path"""
    if not os.path.isabs(prefix):
        path = os.path.join(get_output_directory(), prefix)
    else:
        path = prefix
    return path


def get_count_from_path(path):
    """Given an absolute path, return the number of items in that folder."""
    path = get_full_path(path)
    try:
        count = len(
            [
                name
                for name in os.listdir(path)
                if os.path.isfile(os.path.join(path, name))
            ]
        )
    except FileNotFoundError:
        # Folder does not exist yet, give it a zero count
        count = 0
    logger.info("Folder %s has a count of %s" % (path, count))
    return count


def get_existing_folder_numbers_matching_prefix(prefix):
    """Return a sorted list of integers that match the prefix."""
    prefix_matches = glob.glob(get_full_path(prefix) + "*")
    used = []
    for m in prefix_matches:
        if os.path.isdir(m):
            try:
                used.append(int(m.replace(get_full_path(prefix), "")))
                used.sort()
            except ValueError:
                logger.info(
                    "DarkFolders found a folder that matches the prefix, but there is no suffix or the suffix is not an integer: %s"
                    % (get_full_path(prefix))
                )
    return used


class DarkFolders(object):
    """
    Calculate a folder prefix for saving based on a maximum number of files in the folder.
    This allows creating folder names that 'roll over' when they reach a certain number of images.
    Since this is executed once per batch, it is possible to end up with slightly more images in a folder when the folder is under the maximum number of images and the batch size will cause it to go over the maximum number of images.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # For some dumb reason the module doesn't get called every time a
        # batch is run unless some of the data changes.  Because of this, we
        # require a seed input even though we don't do anything with it.
        # When the seed changes, DarkFolders is re-evaluated.
        # There is probably a better way of dealing with this, I just haven't
        # bothered to dig for it yet.

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
                "folder_prefix": ("STRING", {"default": "batch-"}),
                "folder_size": (
                    "INT",
                    {
                        "default": 500,
                        "min": 1,
                    },
                ),
                "selection_method": (
                    [
                        "Fill Gaps",
                        "Highest Not Full",
                        "New Every Generation",
                        "Change On Input Change",
                    ],
                ),
            },
            "optional": {
                "change_on_input": (
                    "*",
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prefix"

    CATEGORY = "DarkPrompt"

    def get_prefix(
        self, seed, folder_prefix, folder_size, selection_method, change_on_input=None
    ):
        prefix_to_use = folder_prefix

        existing_folder_numbers = get_existing_folder_numbers_matching_prefix(
            folder_prefix
        )

        if selection_method == "Fill Gaps":
            # Find the first available
            for i in range(0, 100000):
                item_count = get_count_from_path(get_full_path(folder_prefix + str(i)))
                if item_count < folder_size:
                    prefix_to_use = folder_prefix + str(i)
                    break
        elif selection_method == "Highest Not Full":
            logger.debug("Using selection method: %s" % (selection_method))
            highest_used_number = 0
            # Loop through all existing folders
            try:
                while existing_folder_numbers:
                    # Grab the highest number from the list and pop it
                    i = existing_folder_numbers.pop()
                    # If the folder number is greater than the highest_used_number AND
                    # it has files in it, update the highest_used_number
                    if (
                        i > highest_used_number
                        and get_count_from_path(get_full_path(folder_prefix + str(i)))
                        > 0
                    ):
                        if (
                            get_count_from_path(get_full_path(folder_prefix + str(i)))
                            >= folder_size
                        ):
                            highest_used_number = i + 1
                        else:
                            highest_used_number = i
            except IndexError:
                # The list of folders is empty
                pass

            logger.debug(
                "The highest folder number with items in it is: %s"
                % (highest_used_number)
            )

            for i in range(highest_used_number, highest_used_number + 100):
                fldr = "%s%s" % (folder_prefix, i)
                size = get_count_from_path(fldr)
                if size < folder_size:
                    logger.debug("Using folder prefix: %s" % (fldr))
                    prefix_to_use = fldr
                    break
        elif selection_method == "New Every Generation":
            prefix_to_use = folder_prefix + str(
                existing_folder_numbers.pop() + 1 if existing_folder_numbers else 0
            )
            pass
        elif selection_method == "Change On Input Change":
            data = {}
            try:
                with open(
                    os.path.join(
                        folder_paths.temp_directory,
                        "darkpromptdarkfolder.json",
                    ),
                    "r",
                ) as data_file:
                    data = json.loads(data_file.read())
            except FileNotFoundError:
                # Probably the first run
                logger.info("darkpromptfolder.json does not exist, probably first run")
                pass

            if not "input_data" in data:
                data.update({"input_data": change_on_input})

            if "input_data" in data and not str(change_on_input) == data["input_data"]:
                prefix_to_use = folder_prefix + str(
                    existing_folder_numbers.pop() + 1 if existing_folder_numbers else 0
                )
                data.update({"input_data": str(change_on_input)})
            else:
                prefix_to_use = folder_prefix + str(
                    existing_folder_numbers.pop() if existing_folder_numbers else 0
                )

            # There appears to be a bug in ComfyUI when you pass the arg
            # --temp-directory /some/folder
            # folder_paths.temp_directory will actually contain /some/folder/temp
            # so just make sure it exists before trying to write to it
            Path(folder_paths.temp_directory).mkdir(parents=True, exist_ok=True)
            data_file = open(
                os.path.join(folder_paths.temp_directory, "darkpromptdarkfolder.json"),
                "w",
            )
            data_file.write(json.dumps(data))
            print(data)

        else:
            raise Exception("Unknown selection method: %s" % (selection_method))

        logger.info("Using prefix: %s" % (prefix_to_use))

        return (prefix_to_use,)
