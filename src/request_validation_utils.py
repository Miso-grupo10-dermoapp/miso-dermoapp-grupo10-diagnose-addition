import json


def validate_body_license(body):
    try:
        license_request = json.loads(body)
        if not validate_property_exist("license_number", license_request):
            raise RuntimeError("license cannot be empty")
    except Exception as err:
        raise RuntimeError("Input request is malformed or missing parameters, details " + str(err))
    return True


def validate_property_exist(property, loaded_body):
    if property in loaded_body:
        if loaded_body[property] is not None:
            return True
        else:
            return False
    else:
        return False
