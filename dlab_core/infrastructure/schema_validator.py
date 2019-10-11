from jsonschema import validate


def validate_schema(request_data, schema):
    if not request_data:
        return 0
    try:
        validate(request_data, schema)
        return 1
    except Exception:
        return 0
