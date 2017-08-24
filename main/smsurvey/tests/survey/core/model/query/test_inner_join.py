import unittest

from smsurvey.core.model.query.inner_join import InnerJoin


class MockTable:
    def __init__(self, table_name="table"):
        self.table_name = table_name


class MockColumn:
    def __init__(self, column_name="column"):
        self.column_name = column_name


class TestInnerJoin(unittest.TestCase):

    def test_equal(self):
        ij = InnerJoin(MockTable("table1"), MockTable("table2"), MockColumn(), InnerJoin.EQUAL, MockColumn())
        expected = "table2 ON table1.column = table2.column"
        self.assertEqual(expected, ij.build())

    def test_not_equal(self):
        ij = InnerJoin(MockTable("table1"), MockTable("table2"), MockColumn(), InnerJoin.NOT_EQUAL, MockColumn())
        expected = "table2 ON table1.column <> table2.column"
        self.assertEqual(expected, ij.build())

    def test_greater_than(self):
        ij = InnerJoin(MockTable("table1"), MockTable("table2"), MockColumn(), InnerJoin.GT, MockColumn())
        expected = "table2 ON table1.column > table2.column"
        self.assertEqual(expected, ij.build())

    def test_less_than(self):
        ij = InnerJoin(MockTable("table1"), MockTable("table2"), MockColumn(), InnerJoin.LT, MockColumn())
        expected = "table2 ON table1.column < table2.column"
        self.assertEqual(expected, ij.build())

