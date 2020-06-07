"""
Common utils for interacting with AWS services
"""


def build_attributes(**attrs):
    """
    Build attributes structure
    """
    attributes = {}
    for key, value in attrs.items():
        if value is not None:
            attributes[key] = {"DataType": "String", "StringValue": value}
    return attributes


def parse_attributes(attributes):
    """
    Parse attributes structure
    """
    attrs = {}
    for key, value in attributes.items():
        attrs[key] = value["StringValue"]
    return attrs
