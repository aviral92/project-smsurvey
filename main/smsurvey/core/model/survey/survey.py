class Survey:

    def __init__(self, survey_id, protocol_id, time_rule_id, participant_id, owner_name, owner_domain):
        self.survey_id = survey_id
        self.protocol_id = protocol_id
        self.time_rule_id = time_rule_id
        self.participant_id = participant_id
        self.owner_name = owner_name
        self.owner_domain = owner_domain

    @classmethod
    def from_tuple(cls, survey_tuple):
        return cls(survey_tuple[0], survey_tuple[1], survey_tuple[2], survey_tuple[3], survey_tuple[4], survey_tuple[5])


class SurveyException(Exception):

    def __init__(self, message):
        self.message = message