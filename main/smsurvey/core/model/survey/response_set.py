import json


class ResponseSet:
    def __init__(self, survey_id, survey_instance_id, response_dict=None):
        self.survey_id = survey_id
        self.survey_instance_id = survey_instance_id
        if response_dict is None:
            self.response_dict = {}
        else:
            self.response_dict = response_dict

    def add_response(self, variable_name, response):
        self.response_dict[variable_name] = response

    def get_response(self, variable_name):
        if variable_name in self.response_dict:
            return self.response_dict[variable_name]
        else:
            return None

    def to_json(self):
        return '{"survey_id":"' + self.survey_id + '","survey_instance_id":"' + self.survey_instance_id + '", "data":' \
              + json.dumps(self.response_dict) + "}"
