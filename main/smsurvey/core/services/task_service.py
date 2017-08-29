from smsurvey.core.model.model import Model


class TaskService:

    @staticmethod
    def create_task(survey_id, time_rule_id):
        tasks = Model.repository.tasks
        task = tasks.create()

        task.survey_id = survey_id
        task.time_rule_id = time_rule_id

        return task.save()

    @staticmethod
    def get_all_tasks():
        tasks = Model.repository.tasks
        return tasks.select(force_list=True)
