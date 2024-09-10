import logging
import random

logger = logging.getLogger(__name__)


class DarkFaceIndexGenerator(object):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "pad_to": (
                    "INT",
                    {"forceInput": True},
                ),
            },
            "required": {
                "number_of_faces": (
                    "INT",
                    {"forceInput": True},
                ),
                "randomize": (
                    "BOOLEAN",
                    {"default": True},
                ),
                "randomize_after_padding": (
                    "BOOLEAN",
                    {"default": True},
                ),
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
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "face_index_generator"

    CATEGORY = "DarkPrompt"

    def face_index_generator(
        self,
        number_of_faces,
        randomize=True,
        randomize_after_padding=True,
        seed=1,
        pad_to=None,
        **kwargs
    ):
        faces = []
        for i in range(0, number_of_faces):
            faces.append(str(i))

        if randomize and not randomize_after_padding:
            random.seed(seed)
            random.shuffle(faces)

        # ReActor is pretty dumb with faces, so we need to ensure every source
        # face also has an input face even if they don't exist, otherwise it
        # won't swap any faces

        if pad_to and number_of_faces < pad_to:
            for i in range(number_of_faces, pad_to):
                faces.append(str(i))

        if randomize and randomize_after_padding:
            random.seed(seed)
            random.shuffle(faces)

        return (",".join(faces),)


class DarkFaceIndexShuffle(object):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {},
            "required": {
                "faces_index_csv": (
                    "STRING",
                    {},
                ),
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
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "face_index_shuffle"

    CATEGORY = "DarkPrompt"

    def face_index_shuffle(self, faces_index_csv, seed=1, **kwargs):
        face_index = faces_index_csv.split(",")

        random.seed(seed)
        random.shuffle(face_index)
        return (",".join(face_index),)
