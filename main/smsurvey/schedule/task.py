class Task:

    def __init__(self, task_id, survey_id, time_rule_id):
        self.task_id = task_id
        self.survey_id = survey_id
        self.time_rule_id = time_rule_id

    @classmethod
    def from_tuple(cls, task_tuple):
        return cls(task_tuple[0], task_tuple[1], task_tuple[2])
