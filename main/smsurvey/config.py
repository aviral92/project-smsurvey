import os

from smsurvey.core.model.query.dao import DAO

dynamo_url_local = "http://localhost:1234"
local = os.environ.get("ENVIRONMENT", None) is None

response_interface_processes = 10
survey_response_interface_port_begin = 25280

question_backend_name = "Question"
response_backend_name = "ResponseStore"
time_rule_backend_name = "TimeRule"

enrollment_table_name = 'enrollment'

dao = DAO()
