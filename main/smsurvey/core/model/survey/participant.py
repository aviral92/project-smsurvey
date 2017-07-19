class Participant:
    
    def __init__(self, participant_id, participant_scratch):
        self.participant_id = participant_id
        self.participant_scratch = participant_scratch

    @classmethod
    def from_tuple(cls, participant_tuple):
        return cls(participant_tuple[0], participant_tuple[1])


class ParticipantException(Exception):

    def __init__(self, message):
        self.message = message
