class InnerJoin:

    E, EQUAL = '=', '='
    NE, NOT_EQUAL = '<>', '<>'
    GT, GREATER_THAN = '>', '>'
    LT, LESS_THAN = '<', '<'

    def __init__(self, this_model, other_model, this_column, comparison_operator, other_column):
        self.this_table = this_model.table_name
        self.other_table = other_model.table_name
        self.this_column = this_column.column_name
        self.comparison_operator = comparison_operator
        self.other_column = other_column.column_name

    def build(self):
        return self.other_table + " ON " + self.this_table + "." + self.this_column + " " + self.comparison_operator \
               + " " + self.other_table + "." + self.other_column
