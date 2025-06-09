import logging
import random
import re
from .gpl3 import DarkLoraTagLoader
from .modules import faces, prompts, files, checkpoints, convert, loras, utils, darkjson

logger = logging.getLogger(__name__)


NODE_CLASS_MAPPINGS = {
    "DarkFolders": files.DarkFolders,
    "DarkCombine": prompts.DarkCombine,
    "DarkPrompt": prompts.DarkPrompt,
    "DarkLoRALoader": DarkLoraTagLoader,
    "DarkFaceIndexShuffle": faces.DarkFaceIndexShuffle,
    "DarkFaceIndexGenerator": faces.DarkFaceIndexGenerator,
    "DarkCheckpointRandomizer": checkpoints.DarkCheckpointRandomizer,
    "DarkCheckpointRotator": checkpoints.DarkCheckpointRotator,
    "DarkCheckpointSwitcher": checkpoints.DarkCheckpointSwitcher,
    "DarkCheckpointRotatorIterations": checkpoints.DarkCheckpointRotatorIterations,
    "DarkAnyToString": convert.DarkAnyToString,
    "DarkLoraStackFromString": loras.DarkLoraStackFromString,
    "DarkPopLoraFromStack": loras.DarkPopLoraFromStack,
    "DarkLoRANameFromString": loras.DarkLoRANameFromString,
    "DarkLoRACombineStacks": loras.DarkLoRACombineStacks,
    "DarkJSONLoader": darkjson.loader.DarkJSONLoader,
    "DarkJSONSaver": darkjson.loader.DarkJSONSaver,
    "DarkJSONGetLoRASettings": darkjson.loras.DarkJSONGetLoRASettings,
    "DarkJSONGetLoRACheckpointSettings": darkjson.loras.DarkJSONGetLoRACheckpointSettings,
    "DarkJSONLoRAStackFromJSON": darkjson.loras.DarkLoraStackFromJSON,
    "DarkJSONUpdateLoRA": darkjson.loader.DarkJSONUpdateLoRA,
    "DarkStringToJSON": darkjson.DarkStringToJSON,
    "DarkTextToJSON": darkjson.DarkTextToJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DarkFolders": "Dark Folders",
    "DarkCombine": "Dark Combiner",
    "DarkPrompt": "Dark Prompt",
    "DarkLoRALoader": "Dark LoRA Loader",
    "DarkFaceIndexShuffle": "Dark Face Index Shuffle",
    "DarkFaceIndexGenerator": "Dark Face Index Generator",
    "DarkCheckpointRandomizer": "Dark Checkpoint Randomizer",
    "DarkCheckpointRotator": "Dark Checkpoint Rotator",
    "DarkCheckpointRotatorIterations": "Dark Checkpoint Rotator with Iterations",
    "DarkCheckpointSwitcher": "Dark Checkpoint Switcher",
    "DarkAnyToString": "Dark Any to String",
    "DarkLoraStackFromString": "Dark LoRA Stack from String",
    "DarkPopLoraFromStack": "Dark LoRA Pop LoRA string from LORA_STACK",
    "DarkLoRANameFromString": "Extracts LoRAs from strings and provides various outputs",
    "DarkLoRACombineStacks": "Dark LoRA Combine Stacks",
    "DarkJSONLoader": "Dark JSON Loader",
    "DarkJSONSaver": "Dark JSON Saver",
    "DarkJSONGetLoRASettings": "Dark JSON Get LoRA Settings",
    "DarkJSONGetLoRACheckpointSettings": "Dark JSON Get LoRA Checkpoint Settings",
    "DarkJSONLoRAStackFromJSON": "Dark JSON Get LoRA Stack from JSON",
    "DarkJSONUpdateLoRA": "Dark JSON Update LoRA Data",
    "DarkStringToJSON": "Dark JSON convert string to JSON",
    "DarkTextToJSON": "Dark JSON convert text to JSON",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
