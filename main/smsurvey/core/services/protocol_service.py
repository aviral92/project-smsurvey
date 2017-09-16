from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class ProtocolService:

    @staticmethod
    def get_protocol(protocol_id):
        protocols = Model.repository.protocols
        return protocols.select(Where(protocols.id, Where.EQUAL, protocol_id))

    @staticmethod
    def get_all_protocols():
        protocols = Model.repository.protocols
        return protocols.select(force_list=True)

    @staticmethod
    def create_protocol(owner_id, name):
        protocols = Model.repository.protocols
        protocol = protocols.create()

        protocol.owner_id = owner_id
        protocol.name = name

        return protocol.save()

    @staticmethod
    def get_protocols_owned_by(owner_id):
        protocols = Model.repository.protocols
        return protocols.select(Where(protocols.owner_id, Where.E, owner_id), force_list=True)

    @staticmethod
    def is_owned_by(protocol_id, owner_id):
        return ProtocolService.get_protocol(protocol_id).owner_id == owner_id