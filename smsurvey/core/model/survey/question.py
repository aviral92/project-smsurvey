import pickle


class Question:

    def __init__(self, survey_id, question_text, variable_name, processor, final=False):
        self.survey_id = survey_id
        self.question_text = question_text
        self.variable_name = variable_name
        if processor is None:
            self.processor = None
        else:
            self.processor = pickle.dumps(processor)
        self.final = final

    def process(self, param):
        if self.processor is not None:
            p = pickle.loads(self.processor)

            if param in p:
                return p[param]
            else:
                return p["~~else~~"]


class QuestionOperationException(Exception):

    def __init__(self, message):
        self.message = message
