from tornado.web import RequestHandler

from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.security.secure import SecurityException


class CreatePluginHandler(RequestHandler):
    def post(self):
        owner = self.get_argument("owner")
        owner_password = self.get_argument("password")
        poke_url = self.get_argument("plugin_id")
        permissions = self.get_argument("permissions")

        at_index = owner.find("@")

        if at_index is -1:
            self.set_status(401)
            self.write('{"status":"error","message":"Invalid owner string <name@domain>"}')
            self.flush()
        else:
            try:

                owner_name = owner[:at_index]
                owner_domain = owner[at_index + 1:]

                plugin, token = PluginService.register_plugin(owner_name, owner_domain, owner_password, poke_url,
                                                                permissions)

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
            OwnerService.create_owner(name, domain, password)
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
