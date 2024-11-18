from comfy.utils import load_torch_file
from comfy.sd import load_lora_for_models
import folder_paths
import logging
import os
import random
import re

logger = logging.getLogger(__name__)


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

        for lora in re.findall(lora_pattern, string_in):
            lora_folder = folder_paths.get_folder_paths("loras")[0]
            lora_path = os.path.join(
                lora_folder,
                lora[0] if ".safetensors" in lora[0] else "%s.safetensors" % (lora[0]),
            )
            if model and clip:
                lora_torch = load_torch_file(
                    lora_path,
                    safe_load=True,
                )

                this_lora_model, this_lora_clip = load_lora_for_models(
                    model,
                    clip,
                    lora_torch,
                    lora[1],
                    lora[1] if lora[2] == "" else lora[1],
                )

            lora_stack.extend(
                [
                    (
                        lora[0]
                        if ".safetensors" in lora[0]
                        else "%s.safetensors" % (lora[0]),
                        float(lora[1]),
                        float(lora[2]) if lora[2] and lora[2] == 0 else float(lora[1]),
                    )
                ]
            )

        string_in = re.sub(lora_pattern, "", string_in)

        return (
            model,
            clip,
            string_in,
            lora_stack,
        )
