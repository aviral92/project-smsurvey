class Instance:

    def __init__(self, instance_id, survey_id, created, triggered, timeout):
        self.instance_id = instance_id
        self.survey_id = survey_id
        self.created = created
        self.triggered = triggered
        self.timeout = timeout

    @classmethod
    def from_tuple(cls, instance_tuple):
        return cls(instance_tuple[0], instance_tuple[1], instance_tuple[2], instance_tuple[3], instance_tuple[4])
