from abc import ABCMeta, abstractmethod

from datetime import datetime


class DataType(metaclass=ABCMeta):

    @classmethod
    def from_db(cls, data_type, required):
        if data_type.startswith('int'):
            return Int(required)

        if data_type.startswith('tinyint'):
            return TinyInt(required)

        if data_type.startswith('varchar'):
            limit = int(data_type[8:-1])
            return Varchar(limit, required)

        if data_type.startswith('timestamp'):
            return Timestamp(required)

        if data_type.startswith('bool'):
            return Bool(required)

    @abstractmethod
    def validate(self, value):
        pass

    @staticmethod
    def validate_required(required, value):
        if required and value is None:
            raise ValueError("Column must not be null")
        elif value is None:
            return False
        return True


class Bool(DataType):

    def __init__(self, required):
        self.required = required

    def validate(self, value):
        if not self.validate_required(self.required, value):
            return True


class Int(DataType):

    def __init__(self, required):
        self.required = required

    def validate(self, value):
        if not self.validate_required(self.required, value):
            return True

        try:
            value_str = str(value)
            value_int = int(value)

            if value_str != str(value_int):
                raise ValueError("Not an integer value")
        except ValueError as e:
            raise e

        return True


class TinyInt(DataType):

    def __init__(self, required):
        self.required = required

    def validate(self, value):
        if not self.validate_required(self.required, value):
            return True

        try:
            value_str = str(value)
            value_int = int(value)

            if value_str != str(value_int):
                raise ValueError("Not an integer value")

            if value_int < -128 or value_int > 127:
                raise ValueError("Out of range for TinyInt")
        except ValueError as e:
            raise e

        return True


class Varchar(DataType):

    def __init__(self, limit, required):
        self.limit = limit
        self.required = required

    def validate(self, value):
        if not self.validate_required(self.required, value):
            return True

        value = str(value)

        if len(value) > self.limit:
            raise ValueError("Value can not be longer than " + str(self.limit))

        return True


class Timestamp(DataType):

    def __init__(self, required):
        self.required = required

    def validate(self, value):
        if not self.validate_required(self.required, value):
            return True

        if isinstance(value, datetime):
            return True

        raise ValueError("Only Python's datetime object accepted")