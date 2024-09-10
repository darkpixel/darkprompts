__version__ = "0.0.7"


import logging
from .utils.darkdata import DarkFolderBase

logger = logging.getLogger(__name__)


# AnyType trick taken from here: https://github.com/comfyanonymous/ComfyUI/discussions/4830
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


any_typ = AnyType("*")


class DarkAnyToString(object):
    """
    Convert anything to a string
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "anything": (
                    any_typ,
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "any_to_string"

    CATEGORY = "DarkPrompt"

    def any_to_string(self, anything):
        return (str(anything),)
