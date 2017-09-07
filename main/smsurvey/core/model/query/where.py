from datetime import datetime


class Where:

    E, EQUAL = '=', '='
    NE, NOT_EQUAL = '<>', '<>'
    GT, GREATER_THAN = '>', '>'
    LT, LESS_THAN = '<', '<'
    IN = 'IN'

    logic_dict = {
        1: 'AND',
        2: 'OR'
    }

    def __init__(self, column, comparison_operator, value, chained=None):
        self.column_name = column.table_name + '.' + column.column_name
        self.comparison_operator = comparison_operator
        self.value = value
        self.chained = chained

    def AND(self, column, comparison_operator, value):
        return self.chain('AND', column, comparison_operator, value)

    def OR(self, column, comparison_operator, value):
        return self.chain('OR', column, comparison_operator, value)

    def chain(self, chain_op, column, comparison_operator, value):
        new_chained = Where(column, comparison_operator, value)

        temp = self

        while temp.chained is not None:
                temp = temp.chained

        temp.chained = (chain_op, new_chained)
        return self

    @staticmethod
    def format_second_clause(value):
        if isinstance(value, str):
            return "'" + value + "'"

        if isinstance(value, datetime):
            return "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"

        if isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple):
            s = '('

            for i in value:
                s += Where.format_second_clause(i) + ', '

            return s[:-2] + ')'

        return str(value)

    def build(self):
        if self.chained is None:
            return self.column_name + " " + self.comparison_operator + " " + Where.format_second_clause(self.value)
        else:
            temp = self

            out = "("

            while 1:
                second_clause = Where.format_second_clause(temp.value)
                out += "(" + temp.column_name + " " + temp.comparison_operator + " " + second_clause + ")"

                if temp.chained is not None:
                    out += " " + temp.chained[0] + " "
                    temp = temp.chained[1]
                else:
                    break

            out += ")"
            return out
