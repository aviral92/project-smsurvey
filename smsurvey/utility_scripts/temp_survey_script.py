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

from smsurvey.utility_scripts import create_owner_db
from smsurvey.utility_scripts import create_plugin_db
from smsurvey.utility_scripts import create_question_cache
from smsurvey.utility_scripts import create_response_store
from smsurvey.utility_scripts import create_survey_cache
from smsurvey.utility_scripts import create_survey_state_cache


def get_one_p(sid):
    return {
        '0': [SurveyState.new_state_object(sid, "owner@test", sid + "_4", 1)],
        '1': [SurveyState.new_state_object(sid, "owner@test", sid + "_2", 1),
              SurveyState.new_state_object(sid, "owner@test", sid + "_6"), 2],
        '2': [SurveyState.new_state_object(sid, "owner@test", sid + "_3", 1),
              SurveyState.new_state_object(sid, "owner@test", sid + "_11", 2)],
        '3': [SurveyState.new_state_object(sid, "owner@test", sid + "_2", 1),
              SurveyState.new_state_object(sid, "owner@test", sid + "_3", 2),
              SurveyState.new_state_object(sid, "owner@test", survey_id + "_16", 3)],
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_5", 5)]
    }


def get_four_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_5", 5)]
    }


def get_six_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_7", 1)]
    }


def get_seven_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_8", 1)]
    }


def get_eight_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_10", 5)]
    }


def get_eleven_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_12", 1)]
    }


def get_twelve_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_13", 1)]
    }


def get_thirteen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_14", 1)]
    }


def get_fourteen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_15", 5)]
    }


def get_sixteen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_17", 1)]
    }


def get_seventeen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_18", 1)]
    }


def get_eighteen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_19", 1)]
    }


def get_nineteen_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_20", 1)]
    }


def get_twenty_p(sid):
    return {
        '~~else~~': [SurveyState.new_state_object(sid, "owner@test", sid + "_21", 5)]
    }


def get_one(sid):
    pr = get_one_p(sid)
    return Question(sid, "Since your last report: Did you smoke a cigarette and/or E-cigarette? [no=0; cig=1; "
                         "Ecig=2; both=3]", "cigEcig", pr, False)


def get_two(sid):
    return Question(sid, "How many minutes after waking did you smoke your first cigarette?", "cig_wake", None, False)


def get_three(sid):
    return Question(sid, "How many minutes after waking did you use your first E-cig?", "ecig_wake", None, False)


def get_four(sid):
    pr = get_four_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, False)


def get_five(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True)


def get_six(sid):
    pr = get_six_p(sid)
    return Question(sid, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, False)


def get_seven(sid):
    pr = get_seven_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last cigarette? [0=Not at all – 9=Extremely "
                         "Satisfying]", "cig_sat", pr, False)


def get_eight(sid):
    pr = get_eight_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, False)


def get_ten(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True)


def get_eleven(sid):
    pr = get_eleven_p(sid)
    return Question(sid, "Since your last report: How many separate times did you use an E-cigarette? ", "Ecig_num",
                    pr, False)


def get_twelve(sid):
    pr = get_twelve_p(sid)
    return Question(sid, "On average, how many puffs did you take each time?", "Ecig_puffs", pr, False)


def get_thirteen(sid):
    pr = get_thirteen_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                         "9=Extremely Satisfying]", "Ecig_sat", pr, False)


def get_fourteen(sid):
    pr = get_fourteen_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all "
                         "– 9=Very, Very much]", "cig_want", pr, False)


def get_fifteen(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True)


def get_sixteen(sid):
    pr = get_sixteen_p(sid)
    return Question(sid, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, False)


def get_seventeen(sid):
    pr = get_seventeen_p(sid)
    return Question(sid, "Since your last report: How many separate times did you smoke an E-cigarette? ",
                    "Ecig_num", pr, False)


def get_eighteen(sid):
    pr = get_eighteen_p(sid)
    return Question(sid, "If you smoked an E-cigarette was it JUUL or another type?If JUUL- Did you smoke T, "
                         "Mint, Mango, Brule ", "Ecig_type", pr, False)


def get_nineteen(sid):
    pr = get_nineteen_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                         "9=Extremely Satisfying]", "Ecig_sat", pr, False)


def get_twenty(sid):
    pr = get_twenty_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, False)


def get_twenty_one(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True)


if __name__ == "__main__":

    create_owner_db.main(True)
    create_plugin_db.main(True)
    create_question_cache.main(True)
    create_response_store.main(True)
    create_survey_cache.main(True)
    create_survey_state_cache.main(True)

    question_service = QuestionService(config.dynamo_url, config.question_backend_name)

    survey_id = "1"
    survey_instance_ids = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    owner_service = OwnerService(config.dynamo_url, config.owner_backend_name)
    owner_service.create_owner('test', 'owner', 'password')

    plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
    token = plugin_service.register_plugin("owner@test", "password", "12345")
    print("token = " + token)
    survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)

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

    question_service.insert(survey_id + "_" + "1", one)
    question_service.insert(survey_id + "_" + "2", two)
    question_service.insert(survey_id + "_" + "3", three)
    question_service.insert(survey_id + "_" + "4", four)
    question_service.insert(survey_id + "_" + "5", five)
    question_service.insert(survey_id + "_" + "6", six)
    question_service.insert(survey_id + "_" + "7", seven)
    question_service.insert(survey_id + "_" + "8", eight)
    question_service.insert(survey_id + "_" + "10", ten)
    question_service.insert(survey_id + "_" + "11", eleven)
    question_service.insert(survey_id + "_" + "12", twelve)
    question_service.insert(survey_id + "_" + "13", thirteen)
    question_service.insert(survey_id + "_" + "14", fourteen)
    question_service.insert(survey_id + "_" + "15", fifteen)
    question_service.insert(survey_id + "_" + "16", sixteen)
    question_service.insert(survey_id + "_" + "17", seventeen)
    question_service.insert(survey_id + "_" + "18", eighteen)
    question_service.insert(survey_id + "_" + "19", nineteen)
    question_service.insert(survey_id + "_" + "20", twenty)
    question_service.insert(survey_id + "_" + "21", twenty_one)

    first_question = survey_id + "_" + "1"

    for instance_id in survey_instance_ids:
        instance = survey_id + "_" + instance_id
        survey_state = SurveyState.new_state_object(instance, "owner@test", first_question)
        survey_state_service.insert(survey_state)
