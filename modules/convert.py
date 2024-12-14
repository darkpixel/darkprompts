import logging
from .utils.darkdata import DarkFolderBase
from .utils import any_typ

logger = logging.getLogger(__name__)


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
