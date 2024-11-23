from comfy.utils import load_torch_file
from comfy.sd import load_lora_for_models
import folder_paths
import logging
import os
import os.path
import random
import re

logger = logging.getLogger(__name__)


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
    Optionally strips the LoRAs out of the string it empts
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
            },
            "optional": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
            },
        }

    @classmethod
    def IS_CHANGED(s, string_in):
        return random.randint(-9999999999, 9999999999)

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

    def load_loras_from_string(self, string_in, model=None, clip=None):
        lora_pattern = r"\<lora\:(?P<lora_name>[0-9a-zA-Z\_\-\.\s\/\(\)]+)\:(?P<model_weight>[\d\.]+):?(?P<clip_weight>[\d\.]*)\>"
        lora_stack = list()
        lora_folder = folder_paths.get_folder_paths("loras")[0]
        lora_to_load = []

        for lora in re.findall(lora_pattern, string_in):
            lora_to_load.append(
                {
                    "name": lora[0]
                    if ".safetensors" in lora[0]
                    else "%s.safetensors" % (lora[0]),
                    "path": os.path.join(
                        lora_folder,
                        lora[0]
                        if ".safetensors" in lora[0]
                        else "%s.safetensors" % (lora[0]),
                    ),
                    "model_weight": lora[1],
                    "clip_weight": lora[2] if len(lora[2]) > 0 else lora[1],
                }
            )

        for lora in lora_to_load:
            # If a model and clip were passed, load the LoRA, otherwise just
            # extend the set
            if not os.path.isfile(lora["path"]):
                print(
                    "SKIP LOADING LOADING LoRA THAT DOES NOT EXIST: %s" % (lora["path"])
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
                    lora["model_weight"],
                    lora["clip_weight"],
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
            model,
            clip,
            string_in,
            lora_stack,
        )
