import logging
import random
import re
from .gpl3 import DarkLoraTagLoader
from .modules import faces, prompts, files, checkpoints, convert, loras

logger = logging.getLogger(__name__)


NODE_CLASS_MAPPINGS = {
    "DarkFolders": files.DarkFolders,
    "DarkCombine": prompts.DarkCombine,
    "DarkPrompt": prompts.DarkPrompt,
    "DarkLoRALoader": DarkLoraTagLoader,
    "DarkFaceIndexShuffle": faces.DarkFaceIndexShuffle,
    "DarkFaceIndexGenerator": faces.DarkFaceIndexGenerator,
    "DarkCheckpointRandomizer": checkpoints.DarkCheckpointRandomizer,
    "DarkCheckpointSwitcher": checkpoints.DarkCheckpointSwitcher,
    "DarkAnyToString": convert.DarkAnyToString,
    "DarkLoraStackFromString": loras.DarkLoraStackFromString,
    "DarkPopLoraFromStack": loras.DarkPopLoraFromStack,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DarkFolders": "Dark Folders",
    "DarkCombine": "Dark Combiner",
    "DarkPrompt": "Dark Prompt",
    "DarkLoRALoader": "Dark LoRA Loader",
    "DarkFaceIndexShuffle": "Dark Face Index Shuffle",
    "DarkFaceIndexGenerator": "Dark Face Index Generator",
    "DarkCheckpointRandomizer": "Dark Checkpoint Randomizer",
    "DarkCheckpointSwitcher": "Dark Checkpoint Switcher",
    "DarkAnyToString": "Dark Any to String",
    "DarkLoraStackFromString": "Dark LoRA Stack from String",
    "DarkPopLoraFromStack": "Dark LoRA Pop LoRA string from LORA_STACK",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
