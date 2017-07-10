class Survey:

    def __init__(self, survey_id, survey_instance_id, owner, participant_id, participant_payload):
        self.survey_id = survey_id
        self.survey_instance_id = survey_instance_id
        self.owner = owner
        self.participant_id = participant_id
        self.participant_payload = participant_payload

    @classmethod
    def from_item(cls, item):
        return cls(item['survey_id']['S'], item['survey_instance_id']['S'], item['owner']['S'], item['participant_id']['S'],
                   item['participant_payload']['S'])


class SurveyOperationException(Exception):

    def __init__(self, message):
        self.message = message
