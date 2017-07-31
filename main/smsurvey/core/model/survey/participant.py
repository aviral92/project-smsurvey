class Participant:
    
    def __init__(self, participant_id, plugin_id, plugin_scratch):
        self.participant_id = participant_id
        self.plugin_id = plugin_id
        self.plugin_scratch = plugin_scratch

    @classmethod
    def from_tuple(cls, participant_tuple):
        return cls(participant_tuple[0], participant_tuple[1], participant_tuple[2])


class ParticipantException(Exception):

    def __init__(self, message):
        self.message = message
