# AnyType trick taken from here: https://github.com/comfyanonymous/ComfyUI/discussions/4830
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


any_typ = AnyType("*")
