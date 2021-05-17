import json, sys
from jsonschema import Draft7Validator, RefResolver, SchemaError
import hashlib

import pkg_resources  # part of setuptools

def get_validator(filename, base_uri=''):
	# Adapated from https://www.programcreek.com/python/example/83374/jsonschema.RefResolver
	# referencing code from HumanCellAtlas Apache License

    """Load schema from JSON file;
    Check whether it's a valid schema;
    Return a Draft4Validator object.
    Optionally specify a base URI for relative path
    resolution of JSON pointers (This is especially useful
    for local resolution via base_uri of form file://{some_path}/)
    """
    def get_json_from_file(filename):
        output = ''
        with open(filename,'rt') as f:
            output = f.read()
        return json.loads(output)
    schema = get_json_from_file(filename)
    try:
        # Check schema via class method call. Works, despite IDE complaining
        Draft7Validator.check_schema(schema)
        #print("Schema %s is valid JSON" % filename)
    except SchemaError:
        raise
        sys.exit(1)
    if base_uri:
        resolver = RefResolver(base_uri=base_uri,
                               referrer=filename)
    else:
        resolver = None
    return Draft7Validator(schema=schema,
                           resolver=resolver) 

def get_version():
    return pkg_resources.require("cio_mass_cytometry")[0].version



def sha256sum(filename):
    # https://stackoverflow.com/a/44873382
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()