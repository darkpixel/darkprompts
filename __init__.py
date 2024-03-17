__version__ = "0.0.8"

import logging
import random
import re
from .gpl3 import DarkLoraTagLoader
from .modules import faces
from .modules import prompts
from .modules import files
from .modules import checkpoints

logger = logging.getLogger(__name__)


NODE_CLASS_MAPPINGS = {
    "DarkFolders": files.DarkFolders,
    "DarkCombine": prompts.DarkCombine,
    "DarkPrompt": prompts.DarkPrompt,
    "DarkLoRALoader": DarkLoraTagLoader,
    "DarkFaceIndexShuffle": faces.DarkFaceIndexShuffle,
    "DarkFaceIndexGenerator": faces.DarkFaceIndexGenerator,
    "DarkCheckpointRandomizer": checkpoints.DarkCheckpointRandomizer,
    "DarkCheckopintSwitcher": checkpoints.DarkCheckpointSwitcher,
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
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
