__version__ = "0.0.7"


import logging
from .utils.darkdata import DarkFolderBase

logger = logging.getLogger(__name__)


# AnyType trick taken from here: https://github.com/comfyanonymous/ComfyUI/discussions/4830
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


any_typ = AnyType("*")


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
                    any_typ,
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

        with DarkFolderBase(
            filename="darkpromptfolder.json", prefix=folder_prefix
        ) as df:
            prefix_to_use = folder_prefix

            if selection_method == "Fill Gaps":
                prefix_to_use = df.get_first_available(folder_size)
            elif selection_method == "Highest Not Full":
                prefix_to_use = df.get_highest_not_full(folder_size)
            elif selection_method == "New Every Generation":
                prefix_to_use = df.get_new()
            elif selection_method == "Change On Input Change":
                prefix_to_use = df.get_new_on_input_change(folder_size, change_on_input)
            else:
                logger.warn("Unknown selection method: %s" % (selection_method))
                prefix_to_use = df.get_new()

        logger.info("Using folder: %s" % (prefix_to_use))

        return (prefix_to_use,)
