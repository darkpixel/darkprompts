from os.path import basename
import re


def unclean_name(name):
    """Ensures a checkpoint or a LoRA name ends with .safetensors."""
    # TODO: Need to search to provide full paths probably

    return name.removesuffix(".safetensors") + ".safetensors"


def clean_name(name):
    """Cleans up checkpoint and LoRA names for use in DarkJSON."""
    return basename(name).removesuffix(".safetensors")


def apply_schema_defaults(instance, schema):
    # Handle None or non-dict instances
    if instance is None:
        instance = {}
    if not isinstance(instance, dict):
        return instance

    # Apply default if present at this level (for non-object types like numbers)
    if (
        "default" in schema
        and "properties" not in schema
        and "patternProperties" not in schema
    ):
        return instance if instance is not None else schema["default"]

    # Create a working copy of the instance
    result = instance.copy()

    # Handle unrecognized keys first (like "checkpoint1")
    unrecognized_keys = [k for k in result if k not in schema.get("properties", {})]
    if unrecognized_keys and not schema.get("patternProperties"):
        # Process unrecognized keys, preserving existing values in nested dicts
        for key in unrecognized_keys:
            if isinstance(result[key], dict):
                nested_result = result[
                    key
                ].copy()  # Start with the existing nested dict
                if "properties" in schema:
                    for prop, subschema in schema["properties"].items():
                        # Only apply defaults if the property is missing or None
                        if prop not in nested_result or nested_result[prop] is None:
                            if "default" in subschema:
                                nested_result[prop] = subschema["default"]
                            elif subschema.get("type") == "object":
                                nested_result[prop] = apply_schema_defaults(
                                    {}, subschema
                                )
                        elif (
                            isinstance(nested_result[prop], dict)
                            and "properties" in subschema
                        ):
                            nested_result[prop] = apply_schema_defaults(
                                nested_result[prop], subschema
                            )
                result[key] = nested_result
        return result

    # Process properties (top-level defined properties) only if no unrecognized keys take precedence
    if "properties" in schema:
        for prop, subschema in schema["properties"].items():
            if prop not in result or result[prop] is None:
                if "default" in subschema:
                    result[prop] = subschema["default"]
                elif subschema.get("type") == "object":
                    result[prop] = apply_schema_defaults({}, subschema)
            elif isinstance(result[prop], dict) and "properties" in subschema:
                result[prop] = apply_schema_defaults(result[prop], subschema)

    # Process patternProperties (dynamic keys)
    if "patternProperties" in schema:
        for pattern, subschema in schema["patternProperties"].items():
            for key in list(result.keys()):
                if isinstance(result[key], dict):
                    result[key] = apply_schema_defaults(result[key], subschema)
                elif result[key] is None:
                    result[key] = apply_schema_defaults({}, subschema)

    return result


def merge_dicts(a, b, path=None, update=True):
    "http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge"
    from collections import OrderedDict

    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], OrderedDict) and isinstance(b[key], OrderedDict):
                merge_dicts(dict(a[key]), dict(b[key]), path + [str(key)])
            elif a[key] == b[key]:
                pass
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = a[key] + b[key]
                # BUG: This won't handle merging identical list items, but that
                # shouldn't be a problem unless someone creates a share against
                # a client, and then an identical share against an office
                # This will probably happen and break everything
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
