from smsurvey.core.model.model import Model

from smsurvey import config
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.protocol_service import ProtocolService

Model.from_database(config.DAO)

owner = OwnerService.get("sam", "mhealth")

enrollment = EnrollmentService.get_by_owner(owner.id)[0]
survey = SurveyService.create_survey(owner.id, ProtocolService.get_all_protocols()[0].id, enrollment.id, 1, 20, 1)


instances = InstanceService.create_instances(survey.id)
