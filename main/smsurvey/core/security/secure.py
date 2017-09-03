import hashlib
import os
import binascii

from datetime import datetime, timedelta

from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


def encrypt_password(not_safe, salt=os.urandom(16)):
    if isinstance(not_safe, str):
        not_safe = not_safe.encode()

    if isinstance(salt, str):
        salt = salt.encode()

    bin_pass = hashlib.pbkdf2_hmac('sha512', not_safe, salt, 100000)
    return binascii.hexlify(bin_pass)


def create_session(owner_id):
    one = os.urandom(16)
    two = os.urandom(16)

    session_id = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', one, two, 100000)).decode()
    sessions = Model.repository.sessions
    sessions.delete(Where(sessions.owner_id, Where.E, owner_id))
    session = sessions.create()
    session.id = session_id
    session.owner_id = owner_id
    session.expires = datetime.now() + timedelta(days=7)

    return session.save(id_override=session_id)


def delete_session(session_id):
    sessions = Model.repository.sessions
    sessions.delete(Where(sessions.id, Where.E, session_id))


def session_valid(owner_id, session_id):
    sessions = Model.repository.sessions
    session = sessions.select(Where(sessions.id, Where.E, session_id))

    if session is None:
        return False

    if datetime.now() > session.expires:
        sessions.delete(Where(sessions.id, Where.E, session_id))
        return False

    return session.owner_id == owner_id


def get_session_owner_id(session_id):
    sessions = Model.repository.sessions
    session = sessions.select(Where(sessions.id, Where.E, session_id))

    if session is None:
        return None

    return session.owner_id


class SecurityException(Exception):

    def __init__(self, message):
        self.message = message
