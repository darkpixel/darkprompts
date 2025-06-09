import json
from io import StringIO
from copy import deepcopy


weights = {
    "type": "number",
    "minimum": 0.0,
    "maximum": 2.0,
    "default": 0.0,
}

step_range = {
    "type": "number",
    "minimum": 1,
    "maximum": 200,
    "default": 50,
}

cfg_range = {
    "type": "number",
    "minimum": 0,
    "maximum": 25,
    "default": 7,
}

model_weights = deepcopy(weights)
model_weights.update({"default": 0.8})

checkpoint_settings = {
    "type": "object",
    "properties": {
        "clip_skip": {"type": "number", "minimum": -5, "maximum": 5, "default": -2},
        "sampler": {"type": "string", "default": "euler_ancestral"},
        "scheduler": {"type": "string", "default": "normal"},
        "step_range": step_range,
        "cfg_range": cfg_range,
    },
    "required": [],
}

checkpoint_schema = {
    "type": "object",
    "patternProperties": {
        ".*": checkpoint_settings,
    },
    "required": [],
}

lora_settings_checkpoint_schema = {
    "type": "object",
    "properties": {
        "balanced": {"type": "boolean", "default": False},
        "model_weight": model_weights,
        "clip_weight": weights,
        "comment": {"type": "string", "default": ""},
    },
    "required": [],
}

lora_settings_schema = {
    "type": "object",
    "patternProperties": {
        ".*": lora_settings_checkpoint_schema,
    },
    #    "properties": {
    #        "default_model_weight": model_weights,
    #        "default_clip_weight": weights,
    #    },
}

file_schema = {
    "type": "object",
    "patternProperties": {
        ".*": lora_settings_schema,
    },
    "required": [],
}


def custom_json_format(obj, indent=4, max_indent_level=2):
    def _format_level(data, level=0):
        if isinstance(data, (dict, list)):
            # Convert to string with full indentation initially
            io = StringIO()
            json.dump(data, io, indent=indent, sort_keys=True)

            if level >= max_indent_level:
                # For levels beyond max_indent_level, return compact form
                return json.dumps(data, separators=(",", ":"), sort_keys=True)
            else:
                # Process this level with indentation, but compact deeper levels
                if isinstance(data, dict):
                    result = "{\n"
                    indent_str = " " * indent * (level + 1)
                    items = []
                    for key, value in sorted(data.items()):
                        formatted_value = _format_level(value, level + 1)
                        items.append(
                            f"{indent_str}{json.dumps(key)}: {formatted_value}"
                        )
                    result += ",\n".join(items) + "\n" + " " * indent * level + "}"
                    return result
                elif isinstance(data, list):
                    if not data:
                        return "[]"
                    result = "[\n"
                    indent_str = " " * indent * (level + 1)
                    items = [_format_level(item, level + 1) for item in data]
                    result += (
                        ",\n".join(f"{indent_str}{item}" for item in items)
                        + "\n"
                        + " " * indent * level
                        + "]"
                    )
                    return result
        # For non-container types (str, int, etc.), just dump as-is
        return json.dumps(data)

    return _format_level(obj, 0)
