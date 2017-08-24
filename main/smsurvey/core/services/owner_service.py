import os
from base64 import b64encode

from smsurvey.core.security import secure
from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class OwnerService:

    @staticmethod
    def get(name, domain):
        owners = Model.repository.owners
        return owners.select(Where(owners.name, Where.EQUAL, name).AND(owners.domain, Where.EQUAL, domain))

    @staticmethod
    def get_by_id(owner_id):
        owners = Model.repository.owners
        return owners.select(Where(owners.id, Where.EQUAL, owner_id))

    @staticmethod
    def create_owner(name, domain, unsafe_password):
        salt = b64encode(os.urandom(16)).decode()
        password = secure.encrypt_password(unsafe_password, salt).decode()

        owners = Model.repository.owners
        owner = owners.create()

        owner.name = name
        owner.domain = domain
        owner.password = password
        owner.salt = salt

        return owner.save()

    @staticmethod
    def does_owner_exist(name, domain):
        return OwnerService.get(name, domain) is not None

    @staticmethod
    def validate_password(name, domain, password):
        owner = OwnerService.get(name, domain)

        if owner is not None:
            test = secure.encrypt_password(password, owner.salt).decode()
            return test == owner.password

    @staticmethod
    def get_owner_id(owner_name, owner_domain):
        owner = OwnerService.get(owner_name, owner_domain)
        return owner.id
