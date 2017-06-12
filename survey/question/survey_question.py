class SurveyQuestion:

    # Return a String that asks your question
    def ask_question(self):
        raise NotImplementedError("Implement in own class")

    # Process a response, and update survey state
    def process_response(self, response, survey_state):
        raise NotImplementedError("Implement in own class")