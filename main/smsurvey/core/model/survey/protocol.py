class Protocol:

    def __init__(self, protocol_id, first_question):
        self.protocol_id = protocol_id
        self.first_question = first_question

    @classmethod
    def from_tuple(cls, protocol_tuple):
        return cls(protocol_tuple[0], protocol_tuple[1])