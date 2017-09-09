import json

from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.security.permissions import authenticate, Permissions
from smsurvey.core.services.protocol_service import ProtocolService


class AllProtocolsHandler(RequestHandler):

    def get(self):
        logger.debug("GET /protocol - retrieving owner's protocols")
        auth = authenticate(self, [Permissions.READ_PROTOCOL])

        if auth['valid']:
            protocol_objects = ProtocolService.get_protocols_owned_by(auth['owner_id'])

            protocols = []

            for protocol_object in protocol_objects:
                protocol = {
                    "id": protocol_object.id,
                    "name": protocol_object.name
                }

                protocols.append(protocol)

            response = {
                "status": "success",
                "protocols": protocols
            }

            response_json = json.dumps(response)
            logger.debug(response_json)

            self.set_status(200)
            self.write(response_json)
            self.flush()

        else:
            logger.debug('Request failed - could not authenticate')

    def data_received(self, chunk):
        pass
