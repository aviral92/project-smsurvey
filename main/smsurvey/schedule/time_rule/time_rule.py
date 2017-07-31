from abc import ABCMeta, abstractmethod
from dateutil import rrule, relativedelta, parser
from datetime import datetime, timedelta


class TimeRule(metaclass=ABCMeta):

    @abstractmethod
    def get_date_times(self):
        pass

    @staticmethod
    @abstractmethod
    def from_params(params):
        pass

    @abstractmethod
    def to_params(self):
        pass

    @staticmethod
    @abstractmethod
    def get_type():
        pass


class NoRepeatTimeRule(TimeRule):

    def __init__(self, run_time):
        self.run_time = run_time

    @staticmethod
    def from_params(params):
        return NoRepeatTimeRule(parser.parse(params))

    @property
    def to_params(self):
        print("to_params - " + self.run_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
        return self.run_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    @staticmethod
    def get_type():
        return "no-repeat"

    def get_date_times(self):
        return [self.run_time]


class RepeatsDailyTimeRule(TimeRule):

    def __init__(self, starting_from, every, until, run_at):
        self.starting_from = starting_from
        self.every = every
        self.until = until
        self.run_at = run_at

    @staticmethod
    def from_params(params):
        p = params.split("~")
        starting_from = parser.parse(p[0])
        every = int(p[1])
        until = parser.parse(p[2])
        run_at = parser.parse(p[3])
        return RepeatsDailyTimeRule(starting_from, every, until, run_at)

    @property
    def to_params(self):
        return self.starting_from.strftime("%Y-%m-%d %Z") + "~" + str(self.every) + "~" \
               + self.until.strftime("%Y-%m-%d %Z") + "~" + self.run_at.strftime("%H:%M:%S %Z")

    @staticmethod
    def get_type():
        return "repeat-daily"

    def get_date_times(self):

        first_run = self.starting_from.replace(hour=self.run_at.hour, minute=self.run_at.minute,
                                               second=self.run_at.second)
        date_times = [first_run]

        number_of_days = (self.until - self.starting_from).days

        for i in range(self.every, number_of_days, self.every):
            date_times.append(first_run + timedelta(days=i))

        return date_times


class RepeatsMonthlyDate(TimeRule):

    def __init__(self, every, days_of_month, until, run_at):
        self.every = every
        self.days_of_month = days_of_month
        self.until = until
        self.run_at = run_at

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        days_of_month = [int(day) for day in p[1].split(',')]
        until = parser.parse(p[2])
        run_at = parser.parse(p[3])
        return RepeatsMonthlyDate(every, days_of_month, until, run_at)

    @property
    def to_params(self):
        return str(self.every) + "~" + str(self.days_of_month)[1:-1] + "~" + self.until.strftime("Y-%m-%d %Z") + "~" \
            + self.run_at.strftime("%H:%M:%S %Z")

    @staticmethod
    def get_type():
        return "repeat-monthly-date"

    def get_date_times(self):
        date_times = []

        for day in self.days_of_month:
            first_run = datetime.now().replace(day=day, hour=self.run_at.hour, minute=self.run_at.minute)
            date_times + list(rrule.rrule(rrule.MONTHLY, dtstart=first_run, until=self.until))

        return date_times


class RepeatsMonthlyDay(TimeRule):

    def __init__(self, every, param1, day_of_week, until, run_at):
        self.every = every
        self.param1 = param1
        self.day_of_week = day_of_week
        self.until = until
        self.run_at = run_at

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        param1 = p[1]
        day_of_week = int(p[2])
        until = parser.parse(p[3])
        run_at = parser.parse(p[4])
        return RepeatsMonthlyDay(every, param1, day_of_week, until, run_at)

    @property
    def to_params(self):
        return str(self.every) + "~" + self.param1 + "~" + str(self.day_of_week) + "~" \
               + self.until.strftime("Y-%m-%d %Z") + "~" + self.run_at.strftime("%H:%M:%S %Z")

    @staticmethod
    def get_type():
        return "repeat-monthly-day"

    def get_date_times(self):
        date_times = []
        today = datetime.now()
        number_of_months = (today.year - self.until.year) * 12 + today.month - self.until.month

        switch = {
            "first": lambda m: self.get_nth_of_month(1, m, self.day_of_week),
            "second": lambda m: self.get_nth_of_month(2, m, self.day_of_week),
            "third": lambda m: self.get_nth_of_month(3, m, self.day_of_week),
            "fourth": lambda m: self.get_nth_of_month(4, m, self.day_of_week),
            "last": lambda m: self.get_nth_of_month(5, m, self.day_of_week)
        }

        for i in range(1, number_of_months + 1, self.every):
            date_times.append(switch[self.param1](i).replace(hour=self.run_at.hour, minute=self.run_at.minute))

        return date_times

    @staticmethod
    def get_nth_of_month(week_number, months_to_add, day_of_week):
        years_to_add = 0
        month_of_year = months_to_add

        if months_to_add > 12:
            years_to_add = months_to_add / 12
            month_of_year = month_of_year - (12 * years_to_add) + 1

        d = datetime.today() + relativedelta.relativedelta(years=years_to_add)
        d.replace(month=month_of_year)
        d.replace(day=1)
        days = d.weekday() - day_of_week
        d -= timedelta(days=days)
        d += relativedelta.relativedelta(weeks=week_number)

        if d.month < month_of_year:
            d += relativedelta.relativedelta(days=7)

        if d.month > month_of_year:
            d -= relativedelta.relativedelta(days=7)

        return d


class RepeatsWeekly(TimeRule):

    def __init__(self, every, days, run_at, starting_from, until):
        self.every = every
        self.days = days
        self.run_at = run_at
        self.starting_from = starting_from
        self.until = until

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        days = [int(day) for day in p[1].split(',')]
        run_at = parser.parse(p[2])
        starting_from = parser.parse(p[0])
        until = parser.parse(p[3])
        return RepeatsWeekly(every, days, run_at, starting_from, until)

    @property
    def to_params(self):
        return str(self.every) + "~" + str(self.days)[1:-1] + "~" + self.run_at.strftime("%H:%M:%S %Z") \
            + "~" + self.starting_from.strftime("Y-%m-%d") + "~" + self.until.strftime("Y-%m-%d %Z")

    @staticmethod
    def get_type():
        return "repeat-weekly"

    def get_date_times(self):
        date_times = []
        monday1 = (self.starting_from - timedelta(days=self.starting_from.weekday()))
        monday2 = (self.until - timedelta(days=self.until.weekday()))

        number_of_weeks = (monday2 - monday1).days / 7

        for i in range(0, number_of_weeks, self.every):
            d = datetime.today() + timedelta(weeks=i)

            for day_of_week in self.days:
                d -= timedelta(days=d.weekday() - day_of_week)
                date_times.append(d)

        return date_times
