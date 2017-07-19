class Instance:

    def __init__(self, instance_id, survey_id, created, timeout):
        self.instance_id = instance_id
        self.survey_id = survey_id
        self.created = created
        self.timeout = timeout

    @classmethod
    def from_tuple(cls, instance_tuple):
        return cls(instance_tuple[0], instance_tuple[1], instance_tuple[2], instance_tuple[3])