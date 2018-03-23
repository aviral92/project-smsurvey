# TO BE USED TEMPORARILY UNTIL UI EXISTS
import inspect
import os
import sys

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config
from smsurvey.core.model.model import Model
from smsurvey.core.model.question import Question
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.protocol_service import ProtocolService

from smsurvey.utility_scripts import create_question_store
from smsurvey.utility_scripts import create_response_store
from smsurvey.utility_scripts import create_time_rule_store


def get_one_p(sid):
    return {
        '0': [[(sid, 4), 1]],
        '1': [[(sid, 2), 1], [(sid, 6), 2]],
        '2': [[(sid, 3), 1], [(sid, 11), 2]],
        '3': [[(sid, 2), 1], [(sid, 3), 2], [(sid, 16), 3]]
    }


def get_four_p(sid):
    return [[(sid, 5), 5]]


def get_six_p(sid):
    return [[(sid, 7), 1]]


def get_seven_p(sid):
    return [[(sid, 8), 1]]


def get_eight_p(sid):
    return [[(sid, 10), 5]]


def get_eleven_p(sid):
    return [[(sid, 12), 1]]


def get_twelve_p(sid):
    return [[(sid, 13), 1]]


def get_thirteen_p(sid):
    return [[(sid, 14), 1]]


def get_fourteen_p(sid):
    return [[(sid, 15), 5]]


def get_sixteen_p(sid):
    return [[(sid, 17), 1]]


def get_seventeen_p(sid):
    return [[(sid, 18), 1]]


def get_eighteen_p(sid):
    return [[(sid, 19), 1]]


def get_nineteen_p(sid):
    return [[(sid, 20), 1]]


def get_twenty_p(sid):
    return[[(sid, 21), 5]]


def get_one(sid):
    pr = get_one_p(sid)
    return Question(sid, "Since your last report: Did you smoke a cigarette and/or E-cigarette? [no=0; cig=1; "
                         "Ecig=2; both=3]", "cigEcig", pr, False, "Invalid response - Must be 0, 1, 2 or 3", False)


def get_two(sid):
    return Question(sid, "How many minutes after waking did you smoke your first cigarette?", "cig_wake", None, True, "", False)


def get_three(sid):
    return Question(sid, "How many minutes after waking did you use your first E-cig?", "ecig_wake", None, True, "", False)


def get_four(sid):
    pr = get_four_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, True, "" ,False)


def get_five(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True, "", True)


def get_six(sid):
    pr = get_six_p(sid)
    return Question(sid, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, True, "", False)


def get_seven(sid):
    pr = get_seven_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last cigarette? [0=Not at all – 9=Extremely "
                         "Satisfying]", "cig_sat", pr, True, "", False)


def get_eight(sid):
    pr = get_eight_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, True, "", False)


def get_ten(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True, "", True)


def get_eleven(sid):
    pr = get_eleven_p(sid)
    return Question(sid, "Since your last report: How many separate times did you use an E-cigarette? ", "Ecig_num",
                    pr, True, "", False)


def get_twelve(sid):
    pr = get_twelve_p(sid)
    return Question(sid, "On average, how many puffs did you take each time?", "Ecig_puffs", pr, True, "", False)


def get_thirteen(sid):
    pr = get_thirteen_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                         "9=Extremely Satisfying]", "Ecig_sat", pr, True, "", False)


def get_fourteen(sid):
    pr = get_fourteen_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all "
                         "– 9=Very, Very much]", "cig_want", pr, True, "", False)


def get_fifteen(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True, "", True)


def get_sixteen(sid):
    pr = get_sixteen_p(sid)
    return Question(sid, "Since your last report: How many cigarettes did you smoke?", "cig_num", pr, True, False)


def get_seventeen(sid):
    pr = get_seventeen_p(sid)
    return Question(sid, "Since your last report: How many separate times did you smoke an E-cigarette? ",
                    "Ecig_num", pr, True, False)


def get_eighteen(sid):
    pr = get_eighteen_p(sid)
    return Question(sid, "If you smoked an E-cigarette was it JUUL or another type?If JUUL- Did you smoke T, "
                         "Mint, Mango, Brule ", "Ecig_type", pr, True, False)


def get_nineteen(sid):
    pr = get_nineteen_p(sid)
    return Question(sid, "On a scale of 0-9, how satisfying was your last E-cigarette? [0=Not at all – "
                         "9=Extremely Satisfying]", "Ecig_sat", pr, True, False)


def get_twenty(sid):
    pr = get_twenty_p(sid)
    return Question(sid, "On a scale of 0-9, how much do you want to smoke a CIGARETTE right now? [0=Not at all – "
                         "9=Very, Very much]", "cig_want", pr, True, False)


def get_twenty_one(sid):
    return Question(sid, "Thank you for completing the survey.", "thanks", None, True, True)


if __name__ == "__main__":

    print("Loading models")
    Model.from_database(config.dao)

    create_question_store.create(True)
    create_response_store.create(True)
    create_time_rule_store.create(True)

    question_service = QuestionService()

    survey_id = "1"

    print("Creating Owner")
    owner = OwnerService.create_owner('ayanagrawal', 'mhealth', 'password')
    print("Owner created")

    print("Generating questions")
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
    print("Questions generated")

    print("Inserting questions")
    question_service.insert(survey_id, 1, one)
    question_service.insert(survey_id, 2, two)
    question_service.insert(survey_id, 3, three)
    question_service.insert(survey_id, 4, four)
    question_service.insert(survey_id, 5, five)
    question_service.insert(survey_id, 6, six)
    question_service.insert(survey_id, 7, seven)
    question_service.insert(survey_id, 8, eight)
    question_service.insert(survey_id, 10, ten)
    question_service.insert(survey_id, 11, eleven)
    question_service.insert(survey_id, 12, twelve)
    question_service.insert(survey_id, 13, thirteen)
    question_service.insert(survey_id, 14, fourteen)
    question_service.insert(survey_id, 15, fifteen)
    question_service.insert(survey_id, 16, sixteen)
    question_service.insert(survey_id, 17, seventeen)
    question_service.insert(survey_id, 18, eighteen)
    question_service.insert(survey_id, 19, nineteen)
    question_service.insert(survey_id, 20, twenty)
    question_service.insert(survey_id, 21, twenty_one)
    print("Questions inserted")

    protocol = ProtocolService.create_protocol(owner.id, "JUUL Protocol")

    print("Script finished")
