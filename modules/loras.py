from comfy.utils import load_torch_file
from comfy.sd import load_lora_for_models
from copy import deepcopy
import folder_paths
import glob
import logging
import os
import os.path
import random
import re
import json

logger = logging.getLogger(__name__)


class DarkLoRANameFromString(object):
    """
    Takes a string in and extracts the LoRA.  Returns the original string, a string with the LoRA information stripped, a LORA_STACK, and a list of LoRA names found.
    Optionally allows adjusting the extracted LoRA weights before returning.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_in": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                    },
                ),
                "adjust_model_weight_by": (
                    "FLOAT",
                    {
                        "min": -1,
                        "max": 1,
                        "default": 0,
                        "step": 0.01,
                        "round": 0.01,
                    },
                ),
                "adjust_clip_weight_by": (
                    "FLOAT",
                    {
                        "min": -1,
                        "max": 1,
                        "default": 0,
                        "step": 0.01,
                        "round": 0.01,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "LORA_STACK", "LORA_NAME_LIST")
    RETURN_NAMES = (
        "ORIGINAL_STRING",
        "STRIPPED_STRING",
        "LORA_STACK",
        "LORA_NAME_LIST",
    )
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(
        self,
        string_in,
        adjust_model_weight_by,
        adjust_clip_weight_by,
    ):

        lora_pattern = r"\<lora\:(?P<lora_name>[0-9a-zA-Z\_\-\.\s\/\(\)]+)\:(?P<model_weight>[\d\.]+):?(?P<clip_weight>[\d\.]*)\>"
        lora_stack = list()
        lora_names = []

        for lora in re.findall(lora_pattern, string_in):
            try:
                lora_stack.extend(
                    [
                        (
                            (
                                lora[0]
                                if ".safetensors" in lora[0]
                                else "%s.safetensors" % (lora[0])
                            ),
                            (
                                float(lora[1]) + float(adjust_model_weight_by)
                                if lora[1]
                                else 0
                            ),
                            (
                                float(lora[2]) + float(adjust_clip_weight_by)
                                if lora[2]
                                else 0
                            ),
                        )
                    ]
                )
                lora_names.append(
                    lora[0]
                    if ".safetensors" in lora[0]
                    else "%s.safetensors" % (lora[0])
                )
            except ValueError:
                logger.warning(
                    "DarkLoRANameFromString: This line appears to have an invalid LoRA weight somewhere: %s"
                    % (string_in)
                )
                continue

        return (
            string_in,
            re.sub(lora_pattern, "", string_in),
            lora_stack,
            lora_names,
        )


class DarkLoRACombineStacks(object):
    """
    Accepts two LoRA stacks and combined them
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "STACK1": (
                    "LORA_STACK",
                    {
                        "forceInput": True,
                    },
                ),
                "STACK2": (
                    "LORA_STACK",
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "action"

    CATEGORY = "DarkPrompt"

    def action(self, STACK1, STACK2):
        return (STACK1 + STACK2,)


class DarkPopLoraFromStack(object):
    """
    Accepts a LoRA stack and extracts the first LoRA it finds, removing it from the stack
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LORA_STACK": (
                    "LORA_STACK",
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("LORA_STACK", "STRING")
    RETURN_NAMES = ("LORA_STACK", "EXTRACTED_LORA")
    FUNCTION = "extract_lora_from_stack"

    CATEGORY = "DarkPrompt"

    def extract_lora_from_stack(self, LORA_STACK):
        popped_lora = ""
        if LORA_STACK:
            popped_lora = LORA_STACK.pop(0)
            popped_lora = popped_lora[0]

        return (LORA_STACK, popped_lora)


class DarkLoraStackFromString(object):
    """
    Takes in a string (prompt), scans it for LoRA tags in the format <lora:somelora:x:y> and creates a LoRA stack from the string
    Optionally strips the LoRAs out of the string it emits
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_in": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                    },
                ),
                "adjust_model_weight_by": (
                    "FLOAT",
                    {
                        "min": -1,
                        "max": 1,
                        "default": 0,
                        "step": 0.01,
                        "round": 0.01,
                    },
                ),
                "adjust_clip_weight_by": (
                    "FLOAT",
                    {
                        "min": -1,
                        "max": 1,
                        "default": 0,
                        "step": 0.01,
                        "round": 0.01,
                    },
                ),
            },
            "optional": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
            },
        }

    RETURN_TYPES = (
        "MODEL",
        "CLIP",
        "STRING",
        "LORA_STACK",
    )
    RETURN_NAMES = (
        "MODEL",
        "CLIP",
        "string_out",
        "LORA_STACK",
    )
    FUNCTION = "load_loras_from_string"

    CATEGORY = "DarkPrompt"

    def load_loras_from_string(
        self,
        string_in,
        adjust_model_weight_by,
        adjust_clip_weight_by,
        model=None,
        clip=None,
    ):
        lora_pattern = r"\<lora\:(?P<lora_name>[0-9a-zA-Z\_\-\.\s\/\(\)]+)\:(?P<model_weight>[\d\.]+):?(?P<clip_weight>[\d\.]*)\>"
        lora_stack = list()
        lora_folder = folder_paths.get_folder_paths("loras")[0]
        lora_to_load = []

        for lora in re.findall(lora_pattern, string_in):
            try:
                lora_to_load.append(
                    {
                        "name": (
                            lora[0]
                            if ".safetensors" in lora[0]
                            else "%s.safetensors" % (lora[0])
                        ),
                        "path": os.path.join(
                            lora_folder,
                            (
                                lora[0]
                                if ".safetensors" in lora[0]
                                else "%s.safetensors" % (lora[0])
                            ),
                        ),
                        "model_weight": float(lora[1]) + float(adjust_model_weight_by),
                        "clip_weight": (
                            float(lora[2])
                            if len(lora[2]) > 0
                            else float(lora[1]) + float(adjust_clip_weight_by)
                        ),
                    }
                )
            except ValueError:
                logger.warning(
                    "This line appears to have an invalid LoRA weight: %s" % (string_in)
                )
                continue

        this_lora_model = model
        this_lora_clip = clip

        for lora in lora_to_load:
            # If a model and clip were passed, load the LoRA, otherwise just
            # extend the set
            if not os.path.isfile(lora["path"]):
                logger.warning(
                    "UNABLE TO LOAD, LoRA DOES NOT EXIST: %s" % (lora["path"])
                )
                continue
            if model and clip:
                lora_torch = load_torch_file(
                    lora["path"],
                    safe_load=True,
                )

                this_lora_model, this_lora_clip = load_lora_for_models(
                    model,
                    clip,
                    lora_torch,
                    float(lora["model_weight"]),
                    float(lora["clip_weight"]),
                )

            lora_stack.extend(
                [
                    (
                        lora["name"],
                        float(lora["model_weight"]),
                        float(lora["clip_weight"]),
                    )
                ]
            )

        # Remove the LoRA tags from the string so a clean string can be passed
        # to the sampler
        string_in = re.sub(lora_pattern, "", string_in)

        return (
            this_lora_model,
            this_lora_clip,
            string_in,
            list(lora_stack),
        )


class DarkLoraStringOverride(object):
    """
    Takes in a string (prompt), scans it for LoRA tags in the format <lora:somelora:x:y> and looks in a JSON file to override them.
    Outputs a string with the overriden LoRA weights, a string with the LoRAs stripped, and a LoRA stack
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_in": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                    },
                ),
                "checkpoint": (
                    folder_paths.get_filename_list("checkpoints"),
                    {
                        "forceInput": True,
                    },
                ),
                "override_file": (
                    "STRING",
                    {"default": "lora.json"},
                ),
                "update_file_if_missing": (
                    "BOOLEAN",
                    {"default": False},
                ),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "LORA_STACK",
    )
    RETURN_NAMES = (
        "STRING_ADJUSTED",
        "STRING_STRIPPED",
        "LORA_STACK",
    )
    FUNCTION = "lora_string_override"

    CATEGORY = "DarkPrompt"

    def lora_string_override(
        self,
        prompt_in,
        checkpoint,
        override_file,
        update_file_if_missing,
    ):
        lora_pattern = r"\<lora\:(?P<lora_name>[0-9a-zA-Z\_\-\.\s\/\(\)]+)\:(?P<model_weight>[\d\.]+):?(?P<clip_weight>[\d\.]*)\>"
        prompt_out = prompt_in
        lora_stack = list()

        original_override_data = {}
        override_data = {}

        if checkpoint and override_file:
            checkpoint_name_part = os.path.basename(checkpoint).replace(
                ".safetensors", ""
            )

            print(
                "DarkLoRA: Checking for overrides for %s in %s"
                % (checkpoint_name_part, override_file)
            )
            try:
                override_path = os.path.join(
                    folder_paths.get_input_directory(), override_file
                )

                with open(override_path, "r") as f:
                    try:
                        original_override_data = json.loads(f.read())
                        override_data = deepcopy(original_override_data)

                    except json.decoder.JSONDecodeError:
                        raise Exception(
                            "DarkLoRA: Your %s JSON file is corrupt and cannot be loaded."
                            % (override_path)
                        )
            except FileNotFoundError:
                raise Exception(
                    "DarkLoRA: Unable to load json override file %s" % (override_path)
                )

        for lora in re.findall(lora_pattern, prompt_in):
            try:
                lora_name = (
                    lora[0]
                    if lora[0].endswith(".safetensors")
                    else "%s.safetensors" % (lora[0])
                )

                lora_name_part = os.path.basename(lora_name).replace(".safetensors", "")
                lora_model_weight = float(lora[1])
                lora_clip_weight = float(lora[2])

                if not checkpoint_name_part in override_data:
                    logger.info(
                        "DarkLoRA: Creating checkpoint %s" % (checkpoint_name_part)
                    )
                    override_data[checkpoint_name_part] = {}

                if lora_name_part not in override_data[checkpoint_name_part]:
                    logger.info("DarkLoRA: Creating LoRA: %s" % (lora_name_part))
                    override_data[checkpoint_name_part][lora_name_part] = {}

                if (
                    not "model_weight"
                    in override_data[checkpoint_name_part][lora_name_part]
                ):
                    logger.info(
                        "DarkLoRA: Missing model weight for %s, setting to %s"
                        % (lora_name_part, lora_model_weight)
                    )
                    override_data[checkpoint_name_part][lora_name_part][
                        "model_weight"
                    ] = lora_model_weight

                if (
                    not "clip_weight"
                    in override_data[checkpoint_name_part][lora_name_part]
                ):
                    logger.info(
                        "DarkLoRA: Missing clip weight for %s, setting to %s"
                        % (lora_name_part, lora_model_weight)
                    )
                    override_data[checkpoint_name_part][lora_name_part][
                        "clip_weight"
                    ] = lora_clip_weight

                if (
                    not "balanced"
                    in override_data[checkpoint_name_part][lora_name_part]
                ):
                    override_data[checkpoint_name_part][lora_name_part][
                        "balanced"
                    ] = False

                lora_model_weight = override_data[checkpoint_name_part][lora_name_part][
                    "model_weight"
                ]
                lora_clip_weight = override_data[checkpoint_name_part][lora_name_part][
                    "clip_weight"
                ]

                lora_stack.extend(
                    [
                        (
                            lora_name,
                            float(lora_model_weight),
                            float(lora_clip_weight),
                        )
                    ]
                )

                prompt_out = re.sub(
                    lora_pattern,
                    "<lora:%s:%s:%s>" % (lora[0], lora_model_weight, lora_clip_weight),
                    prompt_in,
                )

                if (
                    update_file_if_missing
                    and not original_override_data == override_data
                ):
                    logger.info("Saving changes to %s" % (override_file))

                    with open(override_path, "w") as f:
                        f.write(json.dumps(override_data, indent=4, sort_keys=True))

            except ValueError:
                logger.warning(
                    "This line appears to have an invalid LoRA weight: %s" % (prompt_in)
                )
                continue

        return (prompt_out, re.sub(lora_pattern, "", prompt_in), lora_stack)
