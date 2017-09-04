import json
import requests

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
                    'id': plugin.id,
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

    def delete(self):
        session_id = self.get_argument("session_id")
        plugin_id = self.get_argument("plugin_id")

        logger.debug("Attempting to delete plugin registered to owner of session %s", session_id)
        owner_id = secure.get_session_owner_id(session_id)
        logger.debug("Owner of session is %s", owner_id)

        if owner_id is not None:
            if PluginService.is_owned_by(plugin_id, owner_id):
                PluginService.delete_plugin(plugin_id)

                self.set_status(200)
                response = {
                    "status": "success"
                }
            else:
                self.set_status(401)

                response = {
                    "status": "error",
                    "message": "Plugin is not associated with owner"
                }
        else:
            self.set_status(401)

            response = {
                "status": "error",
                "message": "Invalid session"
            }

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def post(self):
        session_id = self.get_argument("session_id")
        plugin_name = self.get_argument("plugin_name")
        plugin_icon = self.get_argument("plugin_icon", None)
        plugin_url = self.get_argument("plugin_url")
        plugin_permissions = self.get_argument("plugin_permissions")

        logger.debug("Attempting to register plugin to owner of session %s", session_id)
        owner_id = secure.get_session_owner_id(session_id)
        logger.debug("Owner of session is %s", owner_id)

        if owner_id is not None:
            plugin, token = PluginService.register_plugin(plugin_name, owner_id, plugin_url, plugin_icon,
                                                          plugin_permissions)

            self.set_status(200)
            response = {
                "status": "success",
                "owner_id": owner_id,
                "token": token
            }
        else:
            self.set_status(401)

            response = {
                "status": "error",
                "message": "Invalid session"
            }

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def data_received(self, chunk):
        pass


class PluginPermissionsHandler(RequestHandler):

    def get(self, plugin_id):
        logger.debug("Requesting permissions from a registered plugin")
        plugin = PluginService.get_plugin(plugin_id)

        if plugin is None:
            self.set_status(410)

            response = {
                "status": "error",
                "message": "invalid plugin id"
            }
        else:
            self.set_status(200)
            response = {
                "status": "success",
                "permissions": plugin.permissions
            }

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def data_received(self, chunk):
        pass


class UnregisteredPluginPermissionsHandler(RequestHandler):

    def get(self, plugin_url):
        logger.debug("Requesting permissions of an unregistered plugin")

        r = requests.get(plugin_url)

        if r.status_code != 200:
            self.set_status(400)
            response = {
                "status": "error",
                "message": "Something went wrong in the request to the plugin"
            }
        else:
            try:
                r = r.json()

                permissions = r["permissions"]

                self.set_status(200)
                response = {
                    "status": "success",
                    "permissions": permissions
                }
            except ValueError as e:
                self.set_status(400)
                response = {
                    "status": "error",
                    "message": "Plugin did not respond to request as expected"
                }

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def data_received(self, chunk):
        pass
