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
    def get_by_owner(owner_id):
        enrollments = Model.repository.enrollments
        return enrollments.select(Where(enrollments.owner_id, Where.EQUAL, owner_id), force_list=True)

    @staticmethod
    def add_enrollment(name, owner_id, open_date, close_date, expiry_date):
        enrollments = Model.repository.enrollments
        enrollment = enrollments.create()

        enrollment.name = name
        enrollment.owner_id = owner_id
        enrollment.open_date = open_date
        enrollment.close_date = close_date
        enrollment.expiry_date = expiry_date

        return enrollment.save()

    @staticmethod
    def delete_enrollment(enrollment_id):
        enrollments = Model.repository.enrollments
        enrollments.delete(Where(enrollments.id, Where.E, enrollment_id))

    @staticmethod
    def is_enrollment_open(enrollment_id):
        enrollment = EnrollmentService.get(enrollment_id)
        now = datetime.now()
        return enrollment.open_date <= now < enrollment.close_date

    @staticmethod
    def enrollment_accessible(enrollment_id):
        enrollment = EnrollmentService.get(enrollment_id)
        return enrollment is not None and enrollment.expiry_date > datetime.now(tz=pytz.utc)

    @staticmethod
    def is_owned_by(enrollment_id, owner_id):
        enrollment = EnrollmentService.get(enrollment_id)
        return enrollment.owner_id == owner_id

    @staticmethod
    def participant_count(enrollment_id):
        participants = Model.repository.participants
        p = participants.select(Where(participants.enrollment_id, Where.E, enrollment_id), force_list=True)
        return len(p)
