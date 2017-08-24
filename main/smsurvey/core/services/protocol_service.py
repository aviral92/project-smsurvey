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
        return protocols.select()

    @staticmethod
    def create_protocol(first_question):
        protocols = Model.repository.protocols
        protocol = protocols.create()

        protocol.first_question = first_question

        return protocol.save()
