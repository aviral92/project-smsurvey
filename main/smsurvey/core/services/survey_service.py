from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class SurveyService:

    @staticmethod
    def get_survey(survey_id):
        surveys = Model.repository.surveys
        return surveys.select(Where(surveys.id, Where.EQUAL, survey_id))

    @staticmethod
    def create_survey(owner_id, protocol_id, enrollment_id, enable_notes, timeout, enable_warnings):
        surveys = Model.repository.surveys
        survey = surveys.create()

        survey.owner_id = owner_id
        survey.protocol_id = protocol_id
        survey.enrollment_id = enrollment_id
        survey.enable_notes = enable_notes
        survey.timeout = timeout
        survey.enable_warnings = enable_warnings

        return survey.save()

    @staticmethod
    def get_surveys_by_owner(owner_id):
        surveys = Model.repository.surveys
        return surveys.select(Where(surveys.owner_id, Where.E, owner_id), force_list=True)