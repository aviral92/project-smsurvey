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