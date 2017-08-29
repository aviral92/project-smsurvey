from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class ParticipantService:

    @staticmethod
    def get_participant(participant_id):
        participants = Model.repository.participants
        return participants.select(Where(participants.id, Where.EQUAL, participant_id))

    @staticmethod
    def register_participant(enrollment_id, plugin_id, plugin_scratch):
        participants = Model.repository.participants
        participant = participants.create()

        participant.enrollment_id = enrollment_id
        participant.plugin_id = plugin_id
        participant.plugin_scratch = plugin_scratch

        return participant.save()

    @staticmethod
    def get_participants_in_enrollment(enrollment_id):
        participants = Model.repository.participants
        return participants.select(Where(participants.enrollment_id, Where.EQUAL, enrollment_id), force_list=True)
