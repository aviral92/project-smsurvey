import json

from dateutil import parser
from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.security.secure import SecurityException
from smsurvey.core.security.permissions import authenticate, Permissions
from smsurvey.interface.participantsdetails import ParticipantDetails

class AllEnrollmentsHandler(RequestHandler):

    # GET /enrollments - return all authorized enrollments
    def get(self):
        logger.debug("User attempting to retrieve all enrollments")
        auth_response = authenticate(self, [Permissions.READ_ENROLLMENT])

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

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()


    # POST /enrollments - add a new enrollment
    def post(self):
        logger.debug("Adding new enrollment")

        name = self.get_argument("name")
        open_date = self.get_argument("open_date", None)
        close_date = self.get_argument("close_date", None)
        expiry_date = self.get_argument("expiry_date", None)

        auth_response = authenticate(self, [Permissions.WRITE_ENROLLMENT])

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

        response_json = json.dumps(response)
        logger.debug(response_json)
        self.write(response_json)
        self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentHandler(RequestHandler):

    # GET /enrollments/<enrollment-id> - returns meta data about enrollment
    def get(self, enrollment_id):
        logger.debug("Getting metadata about an enrollment")
        auth_response = authenticate(self, [Permissions.READ_ENROLLMENT])

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])
            enrollment = EnrollmentService.get(enrollment_id)

            if enrollment.owner_id == owner.id:

                enrollment_dict = {
                    "id": enrollment.id,
                    "open_date": enrollment.open_date.strftime('%Y-%m-%d'),
                    "close_date": enrollment.close_date.strftime('%Y-%m-%d'),
                    "expiry_date": enrollment.expiry_date.strftime('%Y-%m-%d')
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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    # POST /enrollments/<enrollment-id> - updates meta data about enrollment
    def post(self, enrollment_id):
        logger.debug("Updating metadata about an enrollment")

        name = self.get_argument("name", None)
        open_date = self.get_argument("open_date", None)
        close_date = self.get_argument("close_date", None)
        expiry_date = self.get_argument("expiry_date", None)

        auth_response = authenticate(self, [Permissions.WRITE_ENROLLMENT])

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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    # DELETE /enrollments/<enrollment-id> - deletes an enrollment and all enrolled participants
    def delete(self, enrollment_id):
        logger.debug("Removing an enrollment")
        auth_response = authenticate(self, [Permissions.WRITE_ENROLLMENT])

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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentAllParticipantsHandler(RequestHandler):

    # GET /enrollments/<enrollment-id>/enrolled - returns the list of enrolled participants
    def get(self, enrollment_id):
        logger.debug("Getting list of enrolled participants")
        auth_response = authenticate(self, [Permissions.READ_ENROLLMENT, Permissions.READ_PARTICIPANT])

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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    # POST /enrollments/<enrollment-id>/enrolled - adds participant to enrollment
    def post(self, enrollment_id):
        logger.debug("Adding participant to enrollment")
        plugin_id = self.get_argument("plugin_id")
        plugin_name = self.get_argument("plugin_name")
        plugin_scratch = self.get_argument("plugin_scratch")
        ParticipantDetails.participantEnrollment.append(enrollment_id)
        auth_response = authenticate(self, [Permissions.READ_ENROLLMENT, Permissions.WRITE_PARTICIPANT])

        if auth_response["valid"]:
            owner = OwnerService.get_by_id(auth_response["owner_id"])

            if PluginService.is_owned_by(plugin_id, owner.id):
                enrollment = EnrollmentService.get(int(enrollment_id))

                if owner.id == enrollment.owner_id:
                    try:
                        ParticipantService.register_participant(enrollment.id, plugin_id, plugin_scratch, owner.name,
                                                                owner.domain)

                        participants = ParticipantService.get_participants_in_enrollment(enrollment_id)
                        for participant in participants:
                            lastparticipantid = participant.id
                        ParticipantDetails.participantEnrollment.append(lastparticipantid)
                        ParticipantDetails.participantEnrollment.append(plugin_name)
                        ParticipantDetails.participantEnrollment.append(plugin_scratch)
                        ParticipantDetails.get_enrollment()
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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass


class AnEnrollmentAParticipantHandler(RequestHandler):

    # GET /enrollments/<enrollment-id>/<participant-id> - retrieves participant info
    def get(self, enrollment_id, participant_id):
        logger.debug("Retrieving participant info")
        auth_response = authenticate(self, [[Permissions.READ_ENROLLMENT, Permissions.READ_PARTICIPANT]])

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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    # DELETE /enrollments/<enrollment-id>/<participant-id> - deletes participant from the enrollment
    def delete(self, enrollment_id, participant_id):
        logger.debug("Removing participant from enrollment")
        auth_response = authenticate(self, [Permissions.READ_ENROLLMENT, Permissions.WRITE_PARTICIPANT])

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

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass
