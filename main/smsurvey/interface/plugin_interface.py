import json

from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.security.permissions import Permissions, authenticate
from smsurvey.core.services.plugin_service import PluginService


class AllPluginsHandler(RequestHandler):

    def get(self):
        logger.debug("Querying for plugins")
        auth = authenticate(self, [Permissions.READ_PLUGIN])

        permissions = self.get_argument("permissions")

        if auth["valid"]:
            plugins = PluginService.get_plugins_with_at_least_permissions(permissions)

            plugin_list = []

            for plugin in plugins:
                plugin_dict = {
                    "id": plugin.id,
                    "name": plugin.name,
                    "url": plugin.url,
                    "icon": plugin.icon,
                    "permissions": plugin.permissions
                }

                plugin_list.append(plugin_dict)

            response = {
                "status": "success",
                "plugins": plugin_list
            }
            self.set_status(200)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass
