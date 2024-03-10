__version__ = "0.0.7"

from folder_paths import get_output_directory
import glob
import logging
import os
import os.path
import random
import re

logger = logging.getLogger(__name__)


def get_full_path(prefix):
    """Normalize the prefix into a full path"""
    print("Checking prefix: %s" % (prefix))
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
    print("Folder %s has a count of %s" % (path, count))
    return count


def get_existing_folder_numbers_matching_prefix(prefix):
    """Return a sorted list of integers that match the prefix."""
    prefix_matches = glob.glob(get_full_path(prefix) + "*")
    used = []
    for m in prefix_matches:
        if os.path.isdir(m):
            used.append(int(m.replace(get_full_path(prefix), "")))
            used.sort()
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
                    ["Fill Gaps", "Highest Not Full", "New Every Generation"],
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prefix"

    CATEGORY = "DarkPrompt"

    def get_prefix(self, seed, folder_prefix, folder_size, selection_method):
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
            print("Using selection method: %s" % (selection_method))
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

            print(
                "The highest folder number with items in it is: %s"
                % (highest_used_number)
            )

            for i in range(highest_used_number, highest_used_number + 100):
                fldr = "%s%s" % (folder_prefix, i)
                size = get_count_from_path(fldr)
                if size < folder_size:
                    print("Using folder prefix: %s" % (fldr))
                    prefix_to_use = fldr
                    break
        elif selection_method == "New Every Generation":
            prefix_to_use = folder_prefix + str(
                existing_folder_numbers.pop() + 1 if existing_folder_numbers else 0
            )
            pass
        else:
            raise Exception("Unknown selection method: %s" % (selection_method))

        print("Using prefix: %s" % (prefix_to_use))

        return (prefix_to_use,)
