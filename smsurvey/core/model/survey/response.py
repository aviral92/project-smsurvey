import json


class Response:
    def __init__(self, survey_id, survey_instance_id, response_dict={}):
        self.survey_id = survey_id
        self.survey_instance_id = survey_instance_id
        self.response_dict = response_dict

    def add_response(self, variable_name, response):
        self.response_dict[variable_name] = response

    def to_json(self):
        print(type(self.response_dict))
        print(self.response_dict)
        return '{"survey_id":"' + self.survey_id + '","survey_instance_id":"' + self.survey_instance_id + '", "data":' \
              + json.dumps(self.response_dict) + "}"
