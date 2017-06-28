from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey import config
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.core.services.response_service import ResponseService

class DataRequestHandler(RequestHandler):

    def post(self, survey_id):
        data = json_decode(self.request.body)

        if survey_id == "":
            self.set_status(400)
            self.write('{"status":"error","message":"Missing survey_id in url"}')
            self.flush()
            return

        if 'owner' in data:
            owner = data['owner']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing owner parameter"}')
            return

        if 'plugin_id' in data:
            plugin_id = data['plugin_id']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing plugin_id parameter"}')
            return

        if 'token' in data:
            token = data['token']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing token parameter"}')
            return

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(owner, plugin_id, token):
            response_service = ResponseService(config.dynamo_url, config.response_backend_name)

            # TODO: survey id not yet implemented, as in MVP only one survey
            response = response_service.get_response("1", survey_id)

            if response is None:
                self.set_status(404, "No response for this survey")
                self.write('{"status":"error","message":"No response for this survey"}')
                self.flush()
            else:
                self.set_status(200)
                self.write('"status":"success","payload":"' + response.to_json() + '"')
                self.flush()
        else:
            self.set_status(403, "Owner does not have authorization to view this data")
            self.write('{"status":"error","message":"Owner does not have authorization to view this data"}')
            self.flush()

    def data_received(self, chunk):
        pass