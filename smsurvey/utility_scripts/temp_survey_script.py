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


def get_one_p(survey_id):
    return {
        '0': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_4", 1)],
        '1': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_2", 1), SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_6"), 2],
        '2': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_3", 1), SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_11", 2)],
        '3': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_2", 1), SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_3", 2),
                SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_16", 3)],
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_5", 5)]
    }


def get_four_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_5", 5)]
    }


def get_six_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_7", 1)]
    }


def get_seven_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_8", 1)]
    }


def get_eight_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_10", 5)]
    }


def get_eleven_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_12", 1)]
    }


def get_twelve_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_13", 1)]
    }


def get_thirteen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_14", 1)]
    }


def get_fourteen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_15", 5)]
    }


def get_sixteen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_17", 1)]
    }


def get_seventeen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_18", 1)]
    }


def get_eighteen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_19", 1)]
    }


def get_nineteen_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_20", 1)]
    }


def get_twenty_p(survey_id):
    return {
        '~~else~~': [SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_21", 5)]
    }


def get_one(survey_id):
    pr = get_one_p(survey_id)
    return Question(survey_id, "Since your last report: Did you smoke a cigarette and/or E-cigarette? [no=0; cig=1; "
                              "Ecig=2; both=3]", "cigEcig", pr, False)


def get_two(survey_id):
    return Question(survey_id, "How many minutes after waking did you smoke your first cigarette?", "cig_wake", None, False)


def get_three(survey_id):
    return Question(survey_id, "How many minutes after waking did you use your first E-cig?", "ecig_wake", None, False)


def get_four(survey_id):
    pr = get_four_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                           "9=Very, Very much]", "cig_want", pr, False)


def get_five(survey_id):
    return Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)


def get_six(survey_id):
    pr = get_six_p(survey_id)
    return Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, False)


def get_seven(survey_id):
    pr = get_seven_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how satisfying was your last cigarette? [0=Not at all – 9=Extremely "
                            "Satisfying]", "cig_sat", pr, False)


def get_eight(survey_id):
    pr = get_eight_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                            "9=Very, Very much]", "cig_want", pr, False)


def get_ten(survey_id):
    return Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)


def get_eleven(survey_id):
    pr = get_eleven_p(survey_id)
    return Question(survey_id, "Since your last report: How many separate times did you use an E-cigarette? ", "Ecig_num",
                  pr, False)


def get_twelve(survey_id):
    pr = get_twelve_p(survey_id)
    return Question(survey_id, "On average, how many puffs did you take each time?", "Ecig_puffs", pr, False)


def get_thirteen(survey_id):
    pr = get_thirteen_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", pr, False)


def get_fourteen(survey_id):
    pr = get_fourteen_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all "
                               "– 9=Very, Very much]", "cig_want", pr, False)


def get_fifteen(survey_id):
    return Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)


def get_sixteen(survey_id):
    pr = get_sixteen_p(survey_id)
    return Question(survey_id, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, False)


def get_seventeen(survey_id):
    pr = get_seventeen_p(survey_id)
    return Question(survey_id, "Since your last report: How many separate times did you smoke an E-cigarette? ",
                     "Ecig_num", pr, False)


def get_eighteen(survey_id):
    pr = get_eighteen_p(survey_id)
    return Question(survey_id, "If you smoked an E-cigarette was it JUUL or another type?If JUUL- Did you smoke T, "
                               "Mint, Mango, Brule ", "Ecig_type", pr, False)


def get_nineteen(survey_id):
    pr = get_nineteen_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                               "9=Extremely Satisfying]", "Ecig_sat", pr, False)


def get_twenty(survey_id):
    pr = get_twenty_p(survey_id)
    return Question(survey_id, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                             "9=Very, Very much]", "cig_want", pr, False)


def get_twenty_one(survey_id):
    return Question(survey_id, "Thank you for completing the survey.", "thanks", None, True)


if __name__ == "__main__":
    question_service = QuestionService(config.dynamo_url, config.question_backend_name)

    survey_ids = ["1_1", "1_2","1_3", "1_4","1_5", "1_6","1_7", "1_8","1_9", "1_10"]

    owner_service = OwnerService(config.dynamo_url, config.owner_backend_name)
    owner_service.create_owner('test', 'owner', 'password')

    plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
    token = plugin_service.register_plugin("owner@test", "password", "12345")
    print("token = " + token)
    survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)

    for survey_id in survey_ids:
        one = get_one(survey_id)
        two = get_two(survey_id)
        three = get_three(survey_id)
        four = get_four(survey_id)
        five = get_five(survey_id)
        six = get_six(survey_id)
        seven = get_seven(survey_id)
        eight = get_eight(survey_id)
        ten = get_ten(survey_id)
        eleven = get_eleven(survey_id)
        twelve = get_twelve(survey_id)
        thirteen = get_thirteen(survey_id)
        fourteen = get_fourteen(survey_id)
        fifteen = get_fifteen(survey_id)
        sixteen = get_sixteen(survey_id)
        seventeen = get_seventeen(survey_id)
        eighteen = get_eighteen(survey_id)
        nineteen = get_nineteen(survey_id)
        twenty = get_twenty(survey_id)
        twenty_one = get_twenty_one(survey_id)

        question_service.insert(survey_id + "_" + "1_1", one)
        question_service.insert(survey_id + "_" + "1_2", two)
        question_service.insert(survey_id + "_" + "1_3", three)
        question_service.insert(survey_id + "_" + "1_4", four)
        question_service.insert(survey_id + "_" + "1_5", five)
        question_service.insert(survey_id + "_" + "1_6", six)
        question_service.insert(survey_id + "_" + "1_7", seven)
        question_service.insert(survey_id + "_" + "1_8", eight)
        question_service.insert(survey_id + "_" + "1_10", ten)
        question_service.insert(survey_id + "_" + "1_11", eleven)
        question_service.insert(survey_id + "_" + "1_12", twelve)
        question_service.insert(survey_id + "_" + "1_13", thirteen)
        question_service.insert(survey_id + "_" + "1_14", fourteen)
        question_service.insert(survey_id + "_" + "1_15", fifteen)
        question_service.insert(survey_id + "_" + "1_16", sixteen)
        question_service.insert(survey_id + "_" + "1_17", seventeen)
        question_service.insert(survey_id + "_" + "1_18", eighteen)
        question_service.insert(survey_id + "_" + "1_19", nineteen)
        question_service.insert(survey_id + "_" + "1_20", twenty)
        question_service.insert(survey_id + "_" + "1_21", twenty_one)

        survey_state = SurveyState.new_state_object(survey_id, "owner@test", survey_id + "_" + "1_1")

        survey_state_service.insert(survey_state)
