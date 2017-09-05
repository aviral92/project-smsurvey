import base64
import json

from dateutil import parser
from tornado.web import RequestHandler

from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.security.secure import SecurityException


def authenticate(response):
    auth = response.request.headers.get("Authorization")

    if auth is None:
        response.set_status(401)
        response.write('{"status":"error","message":"Missing Authorization header"}')
        response.flush()

    if auth.startswith("Basic"):
        base64enc = auth[6:]
        credentials = base64.b64decode(base64enc).decode()
        hyphen_index = credentials.find("-")
        colon_index = credentials.find(":")

        if colon_index is -1 or hyphen_index is -1:
            response.set_status(401)
            response.write('{"status":"error","message":"Invalid Authorization header"}')
            response.flush()
        else:
            owner_id = credentials[:hyphen_index]

            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            if PluginService.validate_plugin(plugin_id, owner_id, token):
                return {
                    "valid": True,
                    "owner_id": owner_id
                }
            else:
                response.set_status(403)
                response.write('{"status":"error","message":"Do not have authorization to administer enrollments"}')
                response.flush()

    else:
        response.set_status(401)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


class AllEnrollmentsHandler(RequestHandler):

    # GET /enrollments - return all authorized enrollments
    def get(self):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            enrollments = EnrollmentService.get_by_owner(auth_response["owner_id"])

            enrollments_list = []

            for enrollment in enrollments:
                enrollment_dict = {
                    "id": enrollment.id,
                    "name": enrollment.name,
                    "participants": EnrollmentService.participant_count(enrollment.id)
                }

                if enrollment.open_date is not None:
                    enrollment_dict["open_date"] = enrollment.open_date.strftime('%Y-%m-%d')
                else:
                    enrollment_dict["open_date"] = None

                if enrollment.close_date is not None:
                    enrollment_dict["close_date"] = enrollment.close_date.strftime('%Y-%m-%d')
                else:
                    enrollment_dict["close_date"] = None

                if enrollment.expiry_date is not None:
                    enrollment_dict["expiry_date"] = enrollment.expiry_date.strftime('%Y-%m-%d')
                else:
                    enrollment_dict["expiry_date"] = None

                enrollments_list.append(enrollment_dict)

            response = {
                "status": "success",
                "enrollments": enrollments_list
            }
            self.set_status(200)
        else:
            response = {
                "status": "error",
                "message": "Do not have authorization to make this request"
            }
            self.set_status(401)

        self.write(json.dumps(response))
        self.flush()


    # POST /enrollments - add a new enrollment
    def post(self):

        name = self.get_argument("name")
        open_date = self.get_argument("open_date", None)
        close_date = self.get_argument("close_date", None)
        expiry_date = self.get_argument("expiry_date", None)

        auth_response = authenticate(self)

        if auth_response["valid"]:

            if open_date is not None:
                open_date = parser.parse(open_date)

            if close_date is not None:
                close_date = parser.parse(close_date)

            if expiry_date is not None:
                expiry_date = parser.parse(expiry_date)

            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.add_enrollment(name, owner.id, open_date, close_date, expiry_date)

            response = {
                "status": "success",
                "enrollment_id": enrollment.id
            }
            self.set_status(200)
        else:
            response = {
                "status": "error",
                "message": "Do not have authorization to make this request"

            }
            self.set_status(401)

        self.write(json.dumps(response))
        self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentHandler(RequestHandler):

    # GET /enrollments/<enrollment-id> - returns meta data about enrollment
    def get(self, enrollment_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if enrollment.owner_id == owner.id:

                enrollment_dict = {
                    "id": enrollment.id,
                    "open_date": enrollment.open_date.strftime('%Y-%m-%d %Z'),
                    "close_date": enrollment.close_date.strftime('%Y-%m-%d %Z'),
                    "expiry_date": enrollment.expiry_date.strftime('%Y-%m-%d %Z')
                }

                response = {
                    "status": "success",
                    "enrollment": enrollment_dict
                }
                self.set_status(200)
            else:
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer this enrollment"
                }
                self.set_status(401)

            self.write(json.dumps(response))
            self.flush()

    # POST /enrollments/<enrollment-id> - updates meta data about enrollment
    def post(self, enrollment_id):

        name = self.get_argument("name", None)
        open_date = self.get_argument("open_date", None)
        close_date = self.get_argument("close_date", None)
        expiry_date = self.get_argument("expiry_date", None)

        auth_response = authenticate(self)

        if auth_response['valid']:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if enrollment.owner_id == owner.id:

                if name is not None:
                    enrollment.name = name

                if open_date is not None:
                    enrollment.open_date = parser.parse(open_date)

                if close_date is not None:
                    enrollment.close_date = parser.parse(close_date)

                if expiry_date is not None:
                    enrollment.expiry_date = parser.parse(expiry_date)

                enrollment.save()

                response = {
                    "status": "success"
                }
                self.set_status(200)
            else:
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer this enrollment"
                }
                self.set_status(401)

            self.write(json.dumps(response))
            self.flush()



    # DELETE /enrollments/<enrollment-id> - deletes an enrollment and all enrolled participants
    def delete(self, enrollment_id):
        auth_response = authenticate(self)

        if auth_response['valid']:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if enrollment is None or owner.id == enrollment.owner_id:
                if enrollment is not None: # DELETE is idempotent
                    EnrollmentService.delete_enrollment(enrollment_id)

                self.set_status(200)
                response = {
                    "status": "success"
                }
            else:
                self.set_status(401)
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer this enrollment"
                }

            self.write(json.dumps(response))
            self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentAllParticipantsHandler(RequestHandler):

    # GET /enrollments/<enrollment-id>/enrolled - returns the list of enrolled participants
    def get(self, enrollment_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if owner.id == enrollment.owner_id:
                participants = ParticipantService.get_participants_in_enrollment(enrollment.id)

                response = {
                    "status": "success",
                    "participant_ids": [participant.id for participant in participants]
                }
                self.set_status(200)
            else:
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer this enrollment"
                }
                self.set_status(401)

            self.write(json.dumps(response))
            self.flush()

    # POST /enrollments/<enrollment-id>/enrolled - adds participant to enrollment
    def post(self, enrollment_id):

        plugin_id = self.get_argument("plugin_id")
        plugin_scratch = self.get_argument("plugin_scratch")

        auth_response = authenticate(self)

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])

            if PluginService.is_owned_by(plugin_id, owner.id):
                enrollment = EnrollmentService.get(enrollment_id)

                if owner.id == enrollment.owner_id:
                    try:
                        ParticipantService.register_participant(enrollment.id, plugin_id, plugin_scratch, owner.name,
                                                                owner.domain)
                    except SecurityException as e:
                        response = {
                            "status": "error",
                            "message": e.message
                        }
                    else:
                        response = {
                            "status": "success"
                        }
                else:
                    response = {
                        "status": "error",
                        "message": "Owner does not have authorization to administer this enrollment"
                    }
            else:
                response = {
                    "status": "error",
                    "message": "Participant's plugin is not registered with owner"
                }

                self.set_status(401)

            self.write(json.dumps(response))
            self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentAParticipantHandler(RequestHandler):

    # GET /enrollments/<enrollment-id>/<participant-id> - retrieves participant info
    def get(self, enrollment_id, participant_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if owner.id == enrollment.owner_id:
                try:
                    participant = ParticipantService.get_participant(participant_id)
                except SecurityException as e:
                    response = {
                        "status": "error",
                        "message": e.message
                    }
                    self.set_status(410)
                else:
                    if participant is None:
                        response = {
                            "status": "error",
                            "message": "Participant does not exist"
                        }

                        self.set_status(410)
                    elif participant.enrollment_id == enrollment_id:
                        participant_dict = {
                            "participant_id": participant.id,
                            "plugin_id": participant.plugin_id,
                            "plugin_scratch": participant.plugin_scratch,
                            "enrollment_id": participant.enrollment_id
                        }

                        response = {
                            "status": "success",
                            "participant": participant_dict
                        }

                        self.set_status(200)
                    else:
                        response = {
                            "status": "error",
                            "message": "Participant does not belong to enrollment"
                        }
                        self.set_status(400)
            else:
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer enrollment"
                }

            self.write(json.dumps(response))
            self.flush()

    # DELETE /enrollments/<enrollment-id>/<participant-id> - deletes participant from the enrollment
    def delete(self, enrollment_id, participant_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if owner.id == enrollment.owner_id:
                participant = ParticipantService.get_participant(participant_id)

                if participant is None or participant.enrollment_id == enrollment.id:
                    if participant is not None:
                        ParticipantService.delete_participant(participant_id)

                    response = {
                        "status": "success",
                    }
                    self.set_status(200)
                else:
                    response = {
                        "status": "error",
                        "message": "Participant does not belong to enrollment"
                    }
            else:
                response = {
                    "status": "error",
                    "message": "Owner does not have authorization to administer enrollment"
                }
                self.set_status(401)

            self.write(json.dumps(response))
            self.flush()

    def data_received(self, chunk):
        pass
