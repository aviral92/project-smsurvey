import json
import tornado

from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey.core.security import secure
from smsurvey.core.services.owner_service import OwnerService


class LoginHandler(RequestHandler):

    def post(self):
        data = json_decode(self.request.body)

        username = data["username"]
        password = data["password"]

        splitter = username.find('@')

        if splitter == -1:
            self.set_status(401)

            response = {
                "status": "error",
                "reason": "Invalid username"
            }
        else:
            owner_name = username[:splitter]
            owner_domain = username[splitter+1:]

            if OwnerService.validate_password(owner_name, owner_domain, password):
                # Generate a session
                session = secure.create_session(OwnerService.get(owner_name, owner_domain).id)

                self.set_status(200)

                response = {
                    "status": "success",
                    "session_id": session.id
                }

            else:
                self.set_status(401)

                response = {
                    "status": "error",
                    "reason": "Username and password do not match"
                }

        self.write(json.dumps(response))
        self.flush()

    def data_received(self, chunk):
        pass


class LogoutHandler(RequestHandler):

    def post(self):
        data = json_decode(self.request.body)

        session_id = data["session_id"]

        secure.delete_session(session_id)

        response = {
            "status": "success"
        }

        self.set_status(200)
        self.write(json.dumps(response))
        self.flush()

    def data_received(self, chunk):
        pass


class CheckLoginHandler(RequestHandler):

    def post(self):

        data = json_decode(self.request.body)

        username = data["username"]
        session_id = data["session_id"]

        splitter = username.find('@')

        if splitter == -1:
            self.set_status(401)

            response = {
                "status": "error",
                "reason": "Invalid username"
            }
        else:
            owner_name = username[:splitter]
            owner_domain = username[splitter + 1:]

            if secure.session_valid(OwnerService.get(owner_name, owner_domain).id, session_id):
                self.set_status(200)

                response = {
                    "status": "success"
                }
            else:
                self.set_status(401)

                response = {
                    "status": "error",
                    "reason": "Invalid or out of date session"
                }

        self.write(json.dumps(response))
        self.flush()

    def data_received(self, chunk):
        pass
