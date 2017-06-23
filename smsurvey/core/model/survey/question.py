class Question:

    def __init__(self, survey_id, question_text, variable_name, processor, final=False):
        self.survey_id = survey_id
        self.question_text = question_text
        self.variable_name = variable_name
        self.processor = processor
        self.final = final


class QuestionOperationException(Exception):

    def __init__(self, message):
        self.message = message
