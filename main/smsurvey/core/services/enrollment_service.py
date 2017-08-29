import time
import pytz

from datetime import datetime

from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class EnrollmentService:

    @staticmethod
    def get(enrollment_id):
        enrollments = Model.repository.enrollments
        return enrollments.select(Where(enrollments.id, Where.EQUAL, enrollment_id))

    @staticmethod
    def add_enrollment(name, owner_id, opens, closes, remove_on):
        enrollments = Model.repository.enrollments
        enrollment = enrollments.create()

        enrollment.name = name
        enrollment.owner_id = owner_id
        enrollment.opens = opens
        enrollment.closes = closes
        enrollment.remove_on = remove_on

        return enrollment.save()

    @staticmethod
    def is_enrollment_open(enrollment_id):
        enrollment = EnrollmentService.get(enrollment_id)
        now = datetime.now(tz=pytz.utc)

        return enrollment.opens <= now < enrollment.closes

    @staticmethod
    def enrollment_accessible(enrollment_id):
        enrollment = EnrollmentService.get(enrollment_id)
        return enrollment is not None and enrollment.remove_on > datetime.now(tz=pytz.utc)

    @staticmethod
    def is_owned_by(enrollment_id, owner_id):
        enrollment = EnrollmentService.get(enrollment_id)
        return enrollment.owner_id == owner_id

    @staticmethod
    def run_loop():
        print("Starting enrollment cleanup loop")
        while True:
            time.sleep(24000)

