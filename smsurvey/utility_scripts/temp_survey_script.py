# TO BE USED TEMPORARILY UNTIL UI EXISTS
import os
import inspect
import sys

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

survey_id = 1


def one_processor(response):
    if response == '0':
        return [SurveyState.new_state_object(survey_id, "1_4")]
    elif response == '1':
        return [SurveyState.new_state_object(survey_id, "1_2"), SurveyState.new_state_object(survey_id, "1_6")]
    elif response == '2':
        return [SurveyState.new_state_object(survey_id, "1_3"), SurveyState.new_state_object(survey_id, "1_11")]
    elif response == '3':
        return [SurveyState.new_state_object(survey_id, "1_2"), SurveyState.new_state_object(survey_id, "1_3"),
                SurveyState.new_state_object(survey_id, "1_16")]
    else:
        return [SurveyState.new_state_object(survey_id, "1_5")]


def two_processor(response):
    return None


def three_processor(response):
    return None


def four_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_5")]


def five_processor(response):
    return None


def six_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_7")]


def seven_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_8")]


def eight_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_10")]


def ten_processor(response):
    return None


def eleven_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_12")]


def twelve_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_13")]


def thirteen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_14")]


def fourteen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_15")]


def fifteen_processor(response):
    return None


def sixteen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_17")]


def seventeen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_18")]


def eighteen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_19")]


def nineteen_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_20")]


def twenty_processor(response):
    return [SurveyState.new_state_object(survey_id, "1_21")]


def twenty_one_processor(response):
    return None

one = Question(survey_id, "Since your last report: Did you smoke a cigarette and/or E-cigarette? [no=0; cig=1; "
                              "Ecig=2; both=3]", "cigEcig", one_processor, False)

two = Question(survey_id, "How many minutes after waking did you smoke your first cigarette?", "cig_wake", two_processor, False)

three = Question(survey_id, "How many minutes after waking did you use your first E-cig?", "ecig_wake", three_processor, False)

four = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                           "9=Very, Very much]", "cig_want", four_processor, False)

five = Question(survey_id, "Thank you for completing the survey.", "thanks", five_processor, True)

six = Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", six_processor, False)

seven = Question(survey_id, "On a scale of 0-9, how satisfying was your last cigarette? [0=Not at all – 9=Extremely "
                            "Satisfying]", "cig_sat", seven_processor, False)

eight = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                            "9=Very, Very much]", "cig_want", eight_processor, False)

ten = Question(survey_id, "Thank you for completing the survey.", "thanks", ten_processor, True)

eleven = Question(survey_id, "Since your last report: How many separate times did you use an E-cigarette? ", "Ecig_num",
                  eleven_processor, False)

twelve = Question(survey_id, "On average, how many puffs did you take each time?", "Ecig_puffs", twelve_processor, False)

thirteen = Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", thirteen_processor, False)

fourteen = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all "
                               "– 9=Very, Very much]", "cig_want", fourteen_processor, False)

fifteen = Question(survey_id, "Thank you for completing the survey.", "thanks", fifteen_processor, True)

sixteen = Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", sixteen_processor, False)

seventeen = Question(survey_id, "Since your last report: How many separate times did you smoke an E-cigarette? ",
                     "Ecig_num", seventeen_processor, False)

eighteen = Question(survey_id, "If you smoked an E-cigarette was it JUUL or another type?If JUUL- Did you smoke T, "
                               "Mint, Mango, Brule ", "Ecig_type", eighteen_processor, False)

nineteen = Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", nineteen_processor, False)

twenty = Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                             "9=Very, Very much]", "cig_want", twenty_processor, False)

twenty_one = Question(survey_id, "Thank you for completing the survey.", "thanks", twenty_one_processor, True)

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

    survey_state = SurveyState.new_state_object("1_1", "owner@test", "1_1")

    survey_state_service.insert(survey_state)
