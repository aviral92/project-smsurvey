from tornado.web import RequestHandler

from smsurvey import config
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.interface.services.owner_service import OwnerService
from smsurvey.core.security.secure import SecurityException


class CreatePluginHandler(RequestHandler):

    def post(self):
        owner = self.get_argument("owner")
        owner_password = self.get_argument("password")
        plugin_id = self.get_argument("plugin_id")

        try:
            plugin_service = PluginService()
            token = plugin_service.register_plugin(owner, owner_password, plugin_id)
        except SecurityException as e:
            self.set_status(403, e.message)
            self.write('{"status":"error","message":"' + e.message + '"}')
            self.flush()
        else:
            self.set_status(200)
            self.write('{"status":"ok","token":"' + token + '"}')
            self.flush()

    def data_received(self, chunk):
        pass


class CreateOwnerHandler(RequestHandler):

    def post(self):
        domain = self.get_argument("domain")
        name = self.get_argument("name")
        password = self.get_argument("password")

        try:
            owner_service = OwnerService()
            owner_service.create_owner(domain, name, password)
        except SecurityException as e:
            self.set_status(400, e.message)
            self.write('{"status":"error","message":"' + e.message + '"}')
            self.flush()
        else:
            self.set_status(200)
            self.write('{"status":"ok"}')
            self.flush()

    def data_received(self, chunk):
        pass