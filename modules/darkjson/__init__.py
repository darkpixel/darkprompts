from . import loader, loras
from copy import deepcopy
import logging
import json

logger = logging.getLogger(__name__)


class DarkStringToJSON(object):
    """Convert string input data to JSON."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_in": (
                    "STRING",
                    {"ForceInput": True},
                ),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, string_in):
        return (json.loads(string_in),)


class DarkTextToJSON(object):
    """Convert text input to JSON."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_in": (
                    "TEXT",
                    {"ForceInput": True},
                ),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, text_in):
        return (json.loads(text_in),)
