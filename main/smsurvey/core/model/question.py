import pickle


class Question:

    def __init__(self, protocol_id, question_text, variable_name, processor, free_input=False, invalid_message="",
                 final=False):
        self.protocol_id = protocol_id
        self.question_text = question_text
        self.variable_name = variable_name
        self.free_input = free_input
        self.invalid_message = invalid_message
        if processor is None:
            self.processor = None
        else:
            self.processor = pickle.dumps(processor)
        self.final = final

    def process(self, param):
        if self.processor is not None:
            p = pickle.loads(self.processor)
            if self.free_input:
                return p
            else:
                if param in p:
                    return p[param]
                else:
                    return 'INV_RESP'


class QuestionOperationException(Exception):

    def __init__(self, message):
        self.message = message
