from smsurvey.core.security import secure
from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.owner_service import OwnerService


class ParticipantService:

    @staticmethod
    def get_participant(participant_id):
        participants = Model.repository.participants
        participant = participants.select(Where(participants.id, Where.EQUAL, participant_id))

        if participant is None:
            return None

        if EnrollmentService.is_enrollment_open(participant.enrollment_id):
            return participant

        else:
            raise secure.SecurityException("Participant no longer accessible")


    @staticmethod
    def register_participant(enrollment_id, plugin_id, plugin_scratch, owner_name, owner_domain):
        # Checking that owner exists, is using a valid password, and the plugin is registered to that owner
        if OwnerService.does_owner_exist(owner_name, owner_domain):
            if PluginService.is_plugin_registered(plugin_id):
                owner = OwnerService.get(owner_name, owner_domain)
                enrollment = EnrollmentService.get(enrollment_id)
                plugin = PluginService.get_plugin(plugin_id)

                if owner.id == enrollment.owner_id == plugin.owner_id:
                    if EnrollmentService.is_enrollment_open(enrollment_id):
                        participants = Model.repository.participants
                        participant = participants.create()

                        participant.enrollment_id = enrollment_id
                        participant.plugin_id = plugin_id
                        participant.plugin_scratch = plugin_scratch

                        return participant.save()
                    else:
                        raise secure.SecurityException("Enrollment not open")
                else:
                    raise secure.SecurityException("Owner is not valid for enrollment or plugin")
            else:
                raise secure.SecurityException("Plugin is not valid")

    @staticmethod
    def delete_participant(participant_id):
        participants = Model.repository.participants
        participants.delete(Where(participants.id, Where.E, participant_id))

    @staticmethod
    def get_participants_in_enrollment(enrollment_id):
        participants = Model.repository.participants
        return participants.select(Where(participants.enrollment_id, Where.EQUAL, enrollment_id), force_list=True)
