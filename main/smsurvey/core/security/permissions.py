from enum import Enum
from smsurvey.core.services.plugin_service import PluginService
import base64


class Permissions(Enum):
    READ_PARTICIPANT = 10
    WRITE_PARTICIPANT = 11
    READ_ENROLLMENT = 20
    WRITE_ENROLLMENT = 21
    READ_PROTOCOL = 30
    WRITE_PROTOCOL = 31
    READ_QUESTION = 40
    WRITE_QUESTION = 41
    READ_RESPONSE = 50
    WRITE_RESPONSE = 51
    READ_NOTE = 60
    WRITE_NOTE = 61
    READ_SURVEY = 70
    WRITE_SURVEY = 71
    READ_TASK = 80
    WRITE_TASK = 81
    READ_PLUGIN = 90
    WRITE_PLUGIN = 91
    READ_OWNER = 100
    WRITE_OWNER = 101


def authenticate(response, permissions):
    auth = response.request.headers.get("Authorization")

    if auth is None:
        response.set_status(401)
        response.write('{"status":"error","message":"Missing Authorization header"}')
        response.flush()

    if auth.startswith("Basic"):
        base64enc = auth[6:]
        credentials = base64.b64decode(base64enc).decode()
        hyphen_index = credentials.find("-")
        colon_index = credentials.find(":")

        if colon_index is -1 or hyphen_index is -1:
            response.set_status(401)
            response.write('{"status":"error","message":"Invalid Authorization header"}')
            response.flush()
        else:
            owner_id = credentials[:hyphen_index]

            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            if PluginService.validate_plugin(plugin_id, owner_id, token):
                if has_permission(plugin_id, permissions):
                    return {
                        "valid": True,
                        "owner_id": owner_id
                    }
                else:
                    response.set_status(403)
                    response.write('{"status":"error","message":"Permission Denied"}')
                    response.flush()
            else:
                response.set_status(403)
                response.write('{"status":"error","message":"Not authorized"}')
                response.flush()

    else:
        response.set_status(401)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


def has_permission(plugin_id, permissions):
    plugin = PluginService.get_plugin(plugin_id)
    permission_string = plugin.permissions

    for permission in permissions:
        permission_char = permission_string[int(permission.value / 10) - 1]

        if permission_char == '1':
            return False

        if permission.value % 10 == 0 and permission_char == '3':
            return False

        if permission.value % 10 == 1 and permission_char == '2':
            return False

    return True
