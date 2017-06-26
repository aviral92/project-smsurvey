import hashlib
import os
import binascii


def encrypt_password(not_safe, salt=os.urandom(16)):
    if isinstance(not_safe, str):
        not_safe = not_safe.encode()
    bin_pass = hashlib.pbkdf2_hmac('sha512', not_safe, salt, 100000)
    return binascii.hexlify(bin_pass)


class SecurityException(Exception):

    def __init__(self, message):
        self.message = message
