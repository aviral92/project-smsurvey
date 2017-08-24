import unittest

from smsurvey.core.model.query.where import Where


class MockColumn:
    def __init__(self, column_name="column"):
        self.column_name = column_name


class TestWhere(unittest.TestCase):

    def test_equal(self):

        where = Where(MockColumn(), Where.EQUAL, 'value')
        expected = "column = 'value'"
        self.assertEqual(expected, where.build())

    def test_e(self):
        where = Where(MockColumn(), Where.E, 'value')
        expected = "column = 'value'"
        self.assertEqual(expected, where.build())

    def test_not_equal(self):
        where = Where(MockColumn(), Where.NOT_EQUAL, 'value')
        expected = "column <> 'value'"
        self.assertEqual(expected, where.build())

    def test_ne(self):
        where = Where(MockColumn(), Where.NE, 'value')
        expected = "column <> 'value'"
        self.assertEqual(expected, where.build())

    def test_greater_than(self):
        where = Where(MockColumn(), Where.GREATER_THAN, 'value')
        expected = "column > 'value'"
        self.assertEqual(expected, where.build())

    def test_gt(self):
        where = Where(MockColumn(), Where.GT, 'value')
        expected = "column > 'value'"
        self.assertEqual(expected, where.build())

    def test_less_than(self):
        where = Where(MockColumn(), Where.LESS_THAN, 'value')
        expected = "column < 'value'"
        self.assertEqual(expected, where.build())

    def test_lt(self):
        where = Where(MockColumn(), Where.LT, 'value')
        expected = "column < 'value'"
        self.assertEqual(expected, where.build())

    def test_in(self):
        where = Where(MockColumn(), Where.IN, [1, 2, 3])
        expected = "column IN (1, 2, 3)"
        self.assertEqual(expected, where.build())

    def test_value_str(self):
        where = Where(MockColumn(), Where.EQUAL, 'value')
        expected = "column = 'value'"
        self.assertEqual(expected, where.build())

    def test_value_num(self):
        where = Where(MockColumn(), Where.EQUAL, 1)
        expected = "column = 1"
        self.assertEqual(expected, where.build())

    def test_and_clause(self):
        where = Where(MockColumn('col1'), Where.EQUAL, 'value').AND(MockColumn('col2'), Where.LESS_THAN, 1)
        expected = "((col1 = 'value') AND (col2 < 1))"
        self.assertEqual(expected, where.build())

    def test_or_clause(self):
        where = Where(MockColumn('col1'), Where.EQUAL, 'value').OR(MockColumn('col2'), Where.LESS_THAN, 1)
        expected = "((col1 = 'value') OR (col2 < 1))"
        self.assertEqual(expected, where.build())