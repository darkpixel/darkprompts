from comfy.utils import load_torch_file
from comfy.sd import load_lora_for_models
from copy import deepcopy
from jsonschema import validate
from . import schema
from .utils import clean_name, apply_schema_defaults, unclean_name
import folder_paths
import glob
import logging
import os
import os.path
import random
import re
import json

logger = logging.getLogger(__name__)


class DarkJSONGetLoRASettings(object):
    """Gets LoRA Settings based on the LoRA Name."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": (
                    "JSON",
                    {"ForceInput": True},
                ),
                "lora_name": (
                    "STRING",
                    {"ForceInput": True},
                ),
            },
        }

    RETURN_TYPES = ("JSON", "float", "float")
    RETURN_NAMES = (
        "json_out",
        "default_model_weight",
        "default_clip_weight",
    )
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(
        self,
        json_in,
        lora_name,
    ):

        if lora_name:
            lora_name = clean_name(lora_name)
            print("Looking up %s" % (lora_name))

            try:
                logger.info(
                    "Found LoRA settings for %s: %s" % (lora_name, json_in[lora_name])
                )
                return (
                    json_in[lora_name],
                    json_in[lora_name].get("default_model_weight", 0.8),
                    json_in[lora_name].get("default_clip_weight", 0),
                )
            except KeyError:
                logger.info("Settings do not exist for LoRA: %s" % (lora_name))
                return (
                    apply_schema_defaults({lora_name: {}}, schema.lora_settings_schema),
                    json_in[lora_name].get("default_model_weight", 0.8),
                    json_in[lora_name].get("default_clip_weight", 0),
                )
        else:
            return (
                {},
                0.8,
                0,
            )


class DarkJSONGetLoRACheckpointSettings(object):
    """Gets LoRA Settings based on a checkpoint name."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": (
                    "JSON",
                    {"ForceInput": True},
                ),
                "checkpoint": (
                    folder_paths.get_filename_list("checkpoints"),
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_out",)
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, json_in, checkpoint):
        checkpoint_name = clean_name(checkpoint)
        print("json_in: %s" % (json_in))

        if json_in:
            try:
                return (
                    apply_schema_defaults(
                        json_in[checkpoint_name],
                        schema.lora_settings_checkpoint_schema,
                    ),
                )
            except KeyError as e:
                print(
                    "Data does not exist for checkpoint %s: %s" % (checkpoint_name, e)
                )
                return (
                    apply_schema_defaults({}, schema.lora_settings_checkpoint_schema),
                )
        else:
            return {}


class DarkLoraStackFromJSON(object):
    """
    Takes a checkpoint name and a LoRA JSON object and creates a LoRA stack with the proper attributes
    """

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
                "lora_name": (
                    "STRING",
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "LORA_STACK",
        "STRING",
    )
    RETURN_NAMES = ("LORA_STACK", "AS_STRING")
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, json_in, lora_name):
        lora_stack = []
        logger.info(json_in)

        if json_in and lora_name:
            lora_stack.append(
                (
                    unclean_name(lora_name),
                    float(json_in.get("model_weight", 0.8)),
                    float(json_in.get("clip_weight", 0)),
                )
            )
            as_string = "<lora:%s:%s:%s>" % (
                clean_name(lora_name),
                json_in.get("model_weight", 0.8),
                json_in.get("clip_weight", 0),
            )

            return (
                lora_stack,
                as_string,
            )
        else:
            return (
                [],
                "",
            )
