from jsonschema import validate
import json

def validate_output(data, schema_path):
    schema = json.load(open(schema_path))
    validate(instance=data, schema=schema)
