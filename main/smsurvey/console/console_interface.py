import json

from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.security import secure
from smsurvey.core.services.plugin_service import PluginService


class PluginsRequestHandler(RequestHandler):

    def get(self):
        session_id = self.get_argument("session_id")
        logger.debug("Attempting to get plugins registered to owner of session %s", session_id)
        owner_id = secure.get_session_owner_id(session_id)
        logger.debug("Owner of session is %s", owner_id)

        if owner_id is not None:
            p = PluginService.get_by_owner_id(owner_id)

            plugins = []

            for plugin in p:
                plugins.append({
                    'name': plugin.name,
                    'url': plugin.url,
                    'icon': plugin.icon
                })

            self.set_status(200)
            response = {
                "status": "success",
                "plugins": plugins
            }
        else:
            self.set_status(401)
            response = {
                "status": "error",
                "message": "No valid session"
            }

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def data_received(self, chunk):
        pass
