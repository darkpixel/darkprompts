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
                "strip_blank_lines": ("BOOLEAN", {"default": True}),
                "strip_comments": ("BOOLEAN", {"default": True}),
                "randomly_disable": ("BOOLEAN", {"default": True}),
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
                "filename": ("STRING", {"default": ""}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
                "text": ("STRING", {"default": "", "multiline": True}),
                "combine_with": (
                    "STRING",
                    {"default": "", "multiline": True, "forceInput": True},
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
        seed,
        strip_blank_lines=True,
        strip_comments=True,
        randomly_disable=False,
        filename=None,
        text=None,
        prefix=None,
        suffix=None,
        combine_with=None,
        combine_with_delimiter="\n",
    ):
        logger.debug("DarkPrompt called with filename %s" % (filename))

        lines = []

        # Check to see if we have an escaped character.  Probably need to
        # handle this better for other escaped characters
        if combine_with_delimiter == "\\n":
            combine_with_delimiter = "\n"

        # If there is not text and no filename, error out.
        # We might want to just return nothing because crashing a workflow is
        # annoying...but then again, not spotting the problem can be
        # frustrating.
        if not text and not filename:
            raise ValueError("DarkPrompt text and filename can not both be blank")

        # If a filename was provided, load all the lines
        if filename:
            try:
                f = open(filename, "r")
                file_lines = f.read().splitlines()
                for line in file_lines:
                    lines.append(line)
            except FileNotFoundError:
                raise FileNotFoundError("DarkPrompt unable to load: %s" % (filename))

        # If text was provided, load those lines too
        if text:
            for text_line in text.splitlines():
                lines.append(text_line)

        # Strip out comments
        if strip_comments:
            lines = strip_comments_from_lines(lines)

        # Strip out blank lines
        if strip_blank_lines:
            lines = strip_blanks_from_lines(lines)

        # Preseed the python random library with the seed we were fed initially
        # to randomly choose a line
        random.seed(seed)
        try:
            # Pick a random line from the list of available lines
            ret = str(random.choice(lines)).strip()
        except IndexError:
            # An IndexError gets thrown if there are no choices
            logger.info(
                "No choices available for file: %s, skipping it..." % (filename)
            )
            # This means we need to abort, but there may be multiple
            # DarkPrompt objects chained together, so we can't just return an
            # empty string in all cases
            # Check to see if combine_with contains data and that data is not
            # the text 'undefined' from javascript.
            if combine_with and not combine_with == "undefined":
                return (combine_with,)
            else:
                return ""

        # If we are set to randomly disable, we do *NOT* want to use the seed
        # variable.  This will lead to *all* DarkPrompt objects being disabled
        # at the same time, or *all* DarkPrompt objects being enabled at the
        # same time.  So generate a new random seed for each DarkPrompt object.
        if randomly_disable:
            random.seed()

        # Check to see if we are randomly disabled or not and if our choice to
        # randomly disable is True or False
        if not randomly_disable or (randomly_disable and random.choice([True, False])):
            # If we aren't randomly disabled, take the randomly chosen line and
            # add the prefix and/or suffix if they were provided
            logger.debug("chose line: %s from %s lines" % (ret, len(lines)))
            if prefix:
                ret = prefix + ret

            if suffix:
                ret = ret + suffix
        else:
            # If we are randomly disabled, let people know what they're missing
            logger.debug("Randomly disabled line: %s" % (ret))
            ret = ""

        # Check if we have combine_with data from previous DarkPrompt instances
        # and that it isn't 'undefined' and that the stripped length is greater
        # than 0
        if (
            combine_with
            and not combine_with == "undefined"
            and not len(combine_with.strip()) == 0
        ):
            if combine_with_delimiter and len(ret) > 0:
                # Check if we have a delimiter and something to return and join
                # them
                ret = combine_with + combine_with_delimiter + ret
            elif len(ret) > 0:
                # If we just have data to return with no delimiter, combine it
                ret = combine_with + ret
            else:
                # If we have no data to return and no combine_with delimiter,
                # just return the data we were fed initially.
                ret = combine_with

        return (ret,)
