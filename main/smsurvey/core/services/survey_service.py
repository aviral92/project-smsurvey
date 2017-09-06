from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class SurveyService:

    @staticmethod
    def get_survey(survey_id):
        surveys = Model.repository.surveys
        return surveys.select(Where(surveys.id, Where.EQUAL, survey_id))

    @staticmethod
    def create_survey(owner_id, protocol_id, enrollment_id, enable_notes):
        surveys = Model.repository.surveys
        survey = surveys.create()

        survey.owner_id = owner_id
        survey.protocol_id = protocol_id
        survey.enrollment_id = enrollment_id
        survey.enable_notes = enable_notes

        return survey.save()
