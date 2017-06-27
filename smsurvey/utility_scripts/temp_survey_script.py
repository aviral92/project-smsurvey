# TO BE USED TEMPORARILY UNTIL UI EXISTS
import os
import inspect
import sys
import pickle

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config
from smsurvey.core.model.survey.question import Question
from smsurvey.core.model.survey.survey_state_machine import SurveyState
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.interface.services.owner_service import OwnerService
from smsurvey.interface.services.plugin_service import PluginService

survey_id = "1_1"

oneP = {
    '0': [SurveyState.new_state_object(survey_id, "owner@test", "1_4")],
    '1': [SurveyState.new_state_object(survey_id, "owner@test", "1_2"), SurveyState.new_state_object(survey_id, "owner@test", "1_6")],
    '2': [SurveyState.new_state_object(survey_id, "owner@test", "1_3"), SurveyState.new_state_object(survey_id, "owner@test", "1_11")],
    '3': [SurveyState.new_state_object(survey_id, "owner@test", "1_2"), SurveyState.new_state_object(survey_id, "owner@test", "1_3"),
                SurveyState.new_state_object(survey_id, "owner@test", "1_16")],
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_5")]
}

fourP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_5")]
}


sixP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_7")]
}


sevenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_8")]
}


eightP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_10")]
}


elevenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_12")]
}


twelveP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_13")]
}

thirteenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_14")]
}


fourteenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_15")]
}


sixteenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_17")]
}


seventeenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_18")]
}


eighteenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_19")]
}


nineteenP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_20")]
}

twentyP = {
    '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", "1_21")]
}

one = Question(survey_id, "Since your last report: Did you smoke a cigarette and/or E-cigarette? [no=0; cig=1; "
                              "Ecig=2; both=3]", "cigEcig", oneP, False)

two = Question(survey_id, "How many minutes after waking did you smoke your first cigarette?", "cig_wake", None, False)

three = Question(survey_id, "How many minutes after waking did you use your first E-cig?", "ecig_wake", None, False)

four = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                           "9=Very, Very much]", "cig_want", fourP, False)

five = Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)

six = Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", sixP, False)

seven = Question(survey_id, "On a scale of 0-9, how satisfying was your last cigarette? [0=Not at all – 9=Extremely "
                            "Satisfying]", "cig_sat", sevenP, False)

eight = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                            "9=Very, Very much]", "cig_want", eightP, False)

ten = Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)

eleven = Question(survey_id, "Since your last report: How many separate times did you use an E-cigarette? ", "Ecig_num",
                  elevenP, False)

twelve = Question(survey_id, "On average, how many puffs did you take each time?", "Ecig_puffs", twelveP, False)

thirteen = Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", thirteenP, False)

fourteen = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all "
                               "– 9=Very, Very much]", "cig_want", fourteenP, False)

fifteen = Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)

sixteen = Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", sixteenP, False)

seventeen = Question(survey_id, "Since your last report: How many separate times did you smoke an E-cigarette? ",
                     "Ecig_num", seventeenP, False)

eighteen = Question(survey_id, "If you smoked an E-cigarette was it JUUL or another type?If JUUL- Did you smoke T, "
                               "Mint, Mango, Brule ", "Ecig_type", eighteenP, False)

nineteen = Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", nineteenP, False)

twenty = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                             "9=Very, Very much]", "cig_want", twentyP, False)

twenty_one = Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)

if __name__ == "__main__":
    question_service = QuestionService(config.dynamo_url, config.question_backend_name)

    question_service.insert("1_1", one)
    question_service.insert("1_2", two)
    question_service.insert("1_3", three)
    question_service.insert("1_4", four)
    question_service.insert("1_5", five)
    question_service.insert("1_6", six)
    question_service.insert("1_7", seven)
    question_service.insert("1_8", eight)
    question_service.insert("1_10", ten)
    question_service.insert("1_11", eleven)
    question_service.insert("1_12", twelve)
    question_service.insert("1_13", thirteen)
    question_service.insert("1_14", fourteen)
    question_service.insert("1_15", fifteen)
    question_service.insert("1_16", sixteen)
    question_service.insert("1_17", seventeen)
    question_service.insert("1_18", eighteen)
    question_service.insert("1_19", nineteen)
    question_service.insert("1_20", twenty)
    question_service.insert("1_21", twenty_one)

    owner_service = OwnerService(config.dynamo_url, config.owner_backend_name)
    owner_service.create_owner('test', 'owner', 'password')

    plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
    token = plugin_service.register_plugin("owner@test", "password", "12345")
    print("token = " + token)
    survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)

    survey_state = SurveyState.new_state_object(survey_id, "owner@test", "1_1")

    survey_state_service.insert(survey_state)
