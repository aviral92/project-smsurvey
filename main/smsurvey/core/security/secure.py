import base64
import hashlib
import os
import binascii

from smsurvey.interface.services.plugin_service import PluginService


def encrypt_password(not_safe, salt=os.urandom(16)):
    if isinstance(not_safe, str):
        not_safe = not_safe.encode()
    bin_pass = hashlib.pbkdf2_hmac('sha512', not_safe, salt, 100000)
    return binascii.hexlify(bin_pass)


def authenticate(response):
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
            owner = credentials[:hyphen_index]
            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            plugin_service = PluginService()

            if plugin_service.validate_plugin(owner, plugin_id, token):
                return {
                    "valid": True,
                    "owner": owner
                }
            else:
                response.set_status(403)
                response.write('{"status":"error","message":"Do not have authorization to R/W survey"}')
                response.flush()

    else:
        response.set_status(401)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


class SecurityException(Exception):

    def __init__(self, message):
        self.message = message
