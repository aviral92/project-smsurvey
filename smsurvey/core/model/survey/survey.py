class Survey:

    def __init__(self, survey_id, survey_instance_id, participant):
        self.survey_id = survey_id
        self.survey_instance_id = survey_instance_id
        self.participant = participant

    @classmethod
    def from_item(cls, item):
        return cls(item['survey_id']['S'], item['instance_id']['S'], item['participant']['S'])
