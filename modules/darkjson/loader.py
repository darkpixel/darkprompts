from comfy.utils import load_torch_file
from comfy.sd import load_lora_for_models
from copy import deepcopy
from jsonschema import validate
from deepdiff import DeepDiff
from . import schema
from .utils import clean_name, apply_schema_defaults, merge_dicts
import folder_paths
import glob
import hashlib
import logging
import os
import os.path
import random
import re
import json

logger = logging.getLogger(__name__)


class DarkJSONLoader(object):
    """Loads a JSON file and validates it."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filename": (
                    "STRING",
                    {
                        "default": "lora.json",
                    },
                ),
            }
        }

    @classmethod
    def IS_CHANGED(cls, filename):
        file_path = os.path.join(folder_paths.get_input_directory(), filename)
        m = hashlib.sha256()
        with open(file_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "load_json"

    CATEGORY = "DarkPrompt"

    def load_json(self, filename="lora.json"):
        json_data = {}

        try:
            print("re-reading file...")
            file_path = os.path.join(folder_paths.get_input_directory(), filename)

            with open(file_path, "r") as f:
                try:
                    json_data = json.loads(f.read())
                    validate(instance=json_data, schema=schema.file_schema)
                    json_data = apply_schema_defaults(json_data, schema.file_schema)
                except json.decoder.JSONDecodeError:
                    raise Exception(
                        "DarkJSONLoader: Your %s JSON file is corrupt and cannot be loaded."
                        % (file_path)
                    )
        except FileNotFoundError:
            raise Exception(
                "DarkJSONLoader: Unable to find the JSON file you specified: %s"
                % (file_path)
            )

        return (json_data,)


class DarkJSONSaver(object):
    """Validate a JSON file and validate it."""

    OUTPUT_NODE = True

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": (
                    "JSON",
                    {
                        "forceInput": True,
                    },
                ),
                "filename": (
                    "STRING",
                    {
                        "default": "lora.json",
                    },
                ),
            }
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "save_json"

    CATEGORY = "DarkPrompt"

    def save_json(self, json_in, filename):
        if json_in:
            validate(instance=json_in, schema=schema.file_schema)
            file_path = os.path.join(folder_paths.get_input_directory(), filename)

            with open(file_path, "w") as f:
                f.write(
                    schema.custom_json_format(json_in, indent=4, max_indent_level=2)
                )
            return (json_in,)
        else:
            print("No JSON to save")
            return ({},)


class DarkJSONUpdateLoRA(object):
    """Updates a LoRA definition with provided data.  If there is no difference, return None"""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": (
                    "JSON",
                    {},
                ),
                "lora_json": (
                    "JSON",
                    {},
                ),
                "checkpoint_name": (
                    folder_paths.get_filename_list("checkpoints"),
                    {
                        "forceInput": True,
                    },
                ),
                "lora_name": (
                    "STRING",
                    {
                        "forceInput": True,
                    },
                ),
            }
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, json_in, lora_json, checkpoint_name, lora_name):
        json_out = deepcopy(json_in)
        lora_name = clean_name(lora_name)
        checkpoint_name = clean_name(checkpoint_name)
        json_work = {}

        json_work.update({lora_name: {checkpoint_name: lora_json}})
        json_work = apply_schema_defaults(json_work, schema.file_schema)
        print(json_work)

        validate(instance=json_work, schema=schema.file_schema)

        json_out = merge_dicts(json_out, json_work)
        if DeepDiff(json_in, json_out):
            validate(instance=json_out, schema=schema.file_schema)
            return (json_out,)
        else:
            return ({},)
