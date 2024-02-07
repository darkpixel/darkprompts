from pathlib import Path
import comfy.sd
import comfy.utils
import logging
import os
import random
import re
import server
import sys
import folder_paths

# DarkLoraTagLoader is a modified version of LoraTagLoader from
# https://github.com/badjeff/comfyui_lora_tag_loader that also outputs a
# LORA_STACK.
# LoraTagLoader is licensed under the GPL v3 license which is incompatible with
# freedom.


sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))


class DarkLoraTagLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "LORA_STACK")
    RETURN_NAMES = ("MODEL", "CLIP", "STRING", "LORA_STACK")
    FUNCTION = "load_lora"

    CATEGORY = "loaders"

    def __init__(self):
        self.loaded_lora = None
        self.tag_pattern = "\<[0-9a-zA-Z\:\_\-\.\s\/\(\)]+\>"

    def load_lora(self, model, clip, text):
        # print(f"\nLoraTagLoader input text: { text }")

        founds = re.findall(self.tag_pattern, text)
        # print(f"\nfound lora tags: { founds }")

        if len(founds) < 1:
            return (model, clip, text)

        model_lora = model
        clip_lora = clip
        lora_stack = list()

        lora_files = folder_paths.get_filename_list("loras")
        for f in founds:
            tag = f[1:-1]
            pak = tag.split(":")
            (type, name, wModel) = pak[:3]
            wClip = wModel
            if len(pak) > 3:
                wClip = pak[3]
            if type != "lora":
                continue
            lora_name = None
            for lora_file in lora_files:
                if Path(lora_file).name.startswith(name) or lora_file.startswith(name):
                    lora_name = lora_file
                    break
            if lora_name == None:
                print(
                    f"Unable to load LoRA from tag:: { (type, name, wModel, wClip) } >> { lora_name }"
                )
                continue
            # print(f"Found LoRA tag: { (type, name, wModel, wClip) } >> { lora_name }")

            lora_path = folder_paths.get_full_path("loras", lora_name)
            lora = None
            if self.loaded_lora is not None:
                if self.loaded_lora[0] == lora_path:
                    lora = self.loaded_lora[1]
                else:
                    temp = self.loaded_lora
                    self.loaded_lora = None
                    del temp

            if lora is None:
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                self.loaded_lora = (lora_path, lora)

            strength_model = float(wModel)
            strength_clip = float(wClip)
            model_lora, clip_lora = comfy.sd.load_lora_for_models(
                model_lora, clip_lora, lora, strength_model, strength_clip
            )
            lora_stack.extend([(lora_name, strength_model, strength_clip)])

        plain_prompt = re.sub(self.tag_pattern, "", text)
        return (
            model_lora,
            clip_lora,
            plain_prompt,
            lora_stack,
        )
