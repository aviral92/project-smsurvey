import unittest

from core.model.model import Enrollments


class TestEnrollments(unittest.TestCase):

    def test_blah(self):
        Enrollments.from_tuple(('a'))
