__version__ = "0.0.5"

import logging
import random
import re

logger = logging.getLogger(__name__)


def strip_blanks_from_lines(lines):
    cleaned = []
    for line in lines:
        if len(str(line).strip()) == 0:
            pass
        else:
            cleaned.append(line.strip())
    return cleaned


def strip_comments_from_lines(lines):
    cleaned = []
    for line in lines:
        if "#" in line:
            cleaned.append(re.sub(r"#.*$|//.*$", "", str(line)))
        else:
            cleaned.append(line)
    return cleaned


class DarkCombine(object):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "delimiter": ("STRING", {"default": "\n"}),
                "text_a": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_b": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_c": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_d": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_e": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_f": (
                    "STRING",
                    {"forceInput": True},
                ),
                "text_g": (
                    "STRING",
                    {"forceInput": True},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "concatenate_inputs"

    CATEGORY = "DarkPrompt"

    def concatenate_inputs(self, delimiter="\n", **kwargs):
        text = []
        if delimiter == "\\n":
            delimiter = "\n"

        for key in sorted(kwargs.keys()):
            val = kwargs[key]
            if len(val.strip()) > 0:
                text.append(val)

        return (delimiter.join(text),)


class DarkPrompt(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("darkloader init")

    @classmethod
    def INPUT_TYPES(s):
        """
        Return a dictionary which contains config for all input fields.
        Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
        Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
        The type can be a list for selection.

        Returns: `dict`:
            - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
            - Value input_fields (`dict`): Contains input fields config:
                * Key field_name (`string`): Name of a entry-point method's argument
                * Value field_config (`tuple`):
                    + First value is a string indicate the type of field or a list for selection.
                    + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "strip_blank_lines": ("BOOLEAN", {"default": 1}),
                "strip_comments": ("BOOLEAN", {"default": 1}),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "forceInput": True,
                    },
                ),
            },
            "optional": {
                "filename": ("STRING", {"default": None}),
                "prefix": ("STRING", {"default": None}),
                "suffix": ("STRING", {"default": None}),
                "text": ("STRING", {"default": None, "multiline": True}),
                "combine_with": (
                    "STRING",
                    {"default": None, "multiline": True, "forceInput": True},
                ),
                "combine_with_delimiter": ("STRING", {"default": "\n"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "dark_prompt"
    # OUTPUT_NODE = False
    CATEGORY = "DarkPrompt"

    def dark_prompt(
        self,
        strip_blank_lines,
        strip_comments,
        seed,
        filename=None,
        text=None,
        prefix=None,
        suffix=None,
        combine_with=None,
        combine_with_delimiter="\n",
    ):
        logger.info("DarkPrompt called with filename %s" % (filename))

        lines = []

        if not text and not filename:
            raise ValueError("DarkPrompt text and filename can not both be blank")

        if filename:
            try:
                f = open(filename, "r")
                file_lines = f.read().splitlines()
                for line in file_lines:
                    lines.append(line)
                print("Successfully read %s" % (filename))
            except FileNotFoundError:
                raise FileNotFoundError("DarkPrompt unable to load: %s" % (filename))

        if text:
            for text_line in text.splitlines():
                lines.append(text_line)

        if strip_comments:
            lines = strip_comments_from_lines(lines)

        if strip_blank_lines:
            lines = strip_blanks_from_lines(lines)

        random.seed(seed)
        ret = str(random.choice(lines))

        if prefix:
            ret = prefix + ret

        if suffix:
            ret = ret + suffix

        if combine_with and not combine_with == "undefined":
            if combine_with_delimiter:
                if combine_with_delimiter == "\\n":
                    combine_with_delimiter = "\n"
                ret = combine_with + combine_with_delimiter + ret
            else:
                ret = combine_with + ret

        return (ret,)


NODE_CLASS_MAPPINGS = {
    "DarkCombine": DarkCombine,
    "DarkPrompt": DarkPrompt,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DarkCombine": "Dark Combiner",
    "DarkPrompt": "Dark Prompt",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]
