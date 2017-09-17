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


class NoRepeat(TimeRule):

    def __init__(self, run_date, run_times):
        self.run_date = run_date
        self.run_times = run_times

    @staticmethod
    def from_params(params):
        p = params.split("~")
        run_date = parser.parse(p[0])
        run_times = []
        for param in p[1].split('&'):
            run_times.append(parser.parse(param))

        return NoRepeat(run_date, run_times)

    @property
    def to_params(self):

        params = self.run_date.strftime("%Y-%m-%d") + "~"

        for run_time in self.run_times:
            params += run_time.strftime("%H:%M:%S %Z") + "&"

        return params[:-1]

    @staticmethod
    def get_type():
        return "no-repeat"

    def get_date_times(self):
        processed = []

        for run_time in self.run_times:
            processed.append(self.run_date.replace(hour=run_time.hour, minute=run_time.minute, second=run_time.second))

        return processed


class RepeatsDaily(TimeRule):

    def __init__(self, starting_from, every, until, run_times):
        self.starting_from = starting_from
        self.every = every
        self.until = until
        self.run_times = run_times

    @staticmethod
    def from_params(params):
        p = params.split("~")
        starting_from = parser.parse(p[0])
        every = int(p[1])
        until = parser.parse(p[2])
        run_times = []

        for run_time in p[3].split("&"):
            run_times.append(parser.parse(run_time))

        return RepeatsDaily(starting_from, every, until, run_times)

    @property
    def to_params(self):

        run_times = ""

        for run_time in self.run_times:
            run_times += run_time.strftime("%H:%M:%S %Z") + "&"

        return self.starting_from.strftime("%Y-%m-%d") + "~" + str(self.every) + "~" \
               + self.until.strftime("%Y-%m-%d") + "~" + run_times[:-1]

    @staticmethod
    def get_type():
        return "repeat-daily"

    def get_date_times(self):

        date_times = []

        for run_at in self.run_times:
            first_run = self.starting_from.replace(hour=run_at.hour, minute=run_at.minute,
                                               second=run_at.second)
            date_times_day = [first_run]
            number_of_days = (self.until - self.starting_from).days
            for i in range(self.every, number_of_days, self.every):
                date_times_day.append(first_run + timedelta(days=i))

            date_times += date_times_day

        return date_times


class RepeatsMonthlyDate(TimeRule):

    def __init__(self, every, days_of_month, until, run_times):
        self.every = every
        self.days_of_month = days_of_month
        self.until = until
        self.run_times = run_times

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        days_of_month = [int(day) for day in p[1].split(',')]
        until = parser.parse(p[2])
        run_times = [parser.parse(run_at) for run_at in p[3].split('&')]
        return RepeatsMonthlyDate(every, days_of_month, until, run_times)

    @property
    def to_params(self):

        run_times = ""

        for run_at in self.run_times:
            run_times += run_at.strftime("%H:%M:%S %Z") + '&'

        return str(self.every) + "~" + str(self.days_of_month)[1:-1] + "~" + self.until.strftime("%Y-%m-%d") + "~" \
            + run_times[:-1]

    @staticmethod
    def get_type():
        return "repeat-monthly-date"

    def get_date_times(self):
        date_times = []

        for run_at in self.run_times:
            for day in self.days_of_month:
                first_run = datetime.now().replace(day=day, hour=run_at.hour, minute=run_at.minute,
                                                   second=run_at.second)
                date_times += list(rrule.rrule(rrule.MONTHLY, dtstart=first_run, until=self.until))

        return date_times


class RepeatsMonthlyDay(TimeRule):

    def __init__(self, every, param1, days_of_week, until, run_times):
        self.every = every
        self.param1 = param1
        self.days_of_week = days_of_week
        self.until = until
        self.run_times = run_times

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        param1 = p[1]
        days_of_week = []

        for d in p[2].split("&"):
            days_of_week.append(int(d))

        until = parser.parse(p[3])
        run_times = [parser.parse(run_at) for run_at in p[4].split('&')]
        return RepeatsMonthlyDay(every, param1, days_of_week, until, run_times)

    @property
    def to_params(self):

        run_times = ""

        for run_at in self.run_times:
            run_times += run_at.strftime("%H:%M:%S %Z") + '&'

        days_of_week = ""

        for day_of_week in self.days_of_week:
            days_of_week += str(day_of_week) + "&"

        return str(self.every) + "~" + self.param1 + "~" + days_of_week[:-1] + "~" \
               + self.until.strftime("%Y-%m-%d") + "~" + run_times[:-1]

    @staticmethod
    def get_type():
        return "repeat-monthly-day"

    def get_date_times(self):
        date_times = []
        today = datetime.now()
        number_of_months = (self.until.year - today.year) * 12 + today.month - self.until.month

        for day_of_week in self.days_of_week:
            switch = {
                "first": lambda m: self.get_nth_of_month(1, m, day_of_week),
                "second": lambda m: self.get_nth_of_month(2, m, day_of_week),
                "third": lambda m: self.get_nth_of_month(3, m, day_of_week),
                "fourth": lambda m: self.get_nth_of_month(4, m, day_of_week),
                "last": lambda m: self.get_nth_of_month(5, m, day_of_week)
            }

            for i in range(1, number_of_months + 1, self.every):
                day = switch[self.param1](1)

                for run_at in self.run_times:
                    date_times.append(day.replace(hour=run_at.hour, minute=run_at.minute, second=run_at.second))

            return date_times

    @staticmethod
    def get_nth_of_month(week_number, months_to_add, day_of_week):
        years_to_add = 0
        month_of_year = months_to_add

        if months_to_add > 12:
            years_to_add = months_to_add / 12
            month_of_year = month_of_year - (12 * years_to_add) + 1

        d = datetime.today() + relativedelta.relativedelta(years=years_to_add)
        d = d.replace(month=month_of_year)
        d = d.replace(day=1)
        days = d.weekday() - day_of_week
        d -= timedelta(days=days)
        d += relativedelta.relativedelta(weeks=week_number)

        if d.month < month_of_year:
            d += relativedelta.relativedelta(days=7)

        if d.month > month_of_year:
            d -= relativedelta.relativedelta(days=7)

        return d


class RepeatsWeekly(TimeRule):

    def __init__(self, every, days, run_times, starting_from, until):
        self.every = every
        self.days = days
        self.run_times = run_times
        self.starting_from = starting_from
        self.until = until

    @staticmethod
    def from_params(params):
        p = params.split("~")
        every = int(p[0])
        days = [int(day) for day in p[1].split(',')]
        run_times = [parser.parse(run_at) for run_at in p[2].split('&')]
        starting_from = parser.parse(p[3])
        until = parser.parse(p[4])
        return RepeatsWeekly(every, days, run_times, starting_from, until)

    @property
    def to_params(self):

        run_times = ""

        for run_at in self.run_times:
            run_times += run_at.strftime("%H:%M:%S %Z") + '&'

        return str(self.every) + "~" + str(self.days)[1:-1] + "~" + run_times[:-1] \
            + "~" + self.starting_from.strftime("%Y-%m-%d") + "~" + self.until.strftime("%Y-%m-%d")

    @staticmethod
    def get_type():
        return "repeat-weekly"

    def get_date_times(self):
        date_times = []
        monday1 = (self.starting_from - timedelta(days=self.starting_from.weekday()))
        monday2 = (self.until - timedelta(days=self.until.weekday()))

        number_of_weeks = int((monday2 - monday1).days / 7)

        for i in range(0, number_of_weeks, self.every):
            d = datetime.today() + timedelta(weeks=i)

            for day_of_week in self.days:
                d -= timedelta(days=d.weekday() - day_of_week)

                for run_at in self.run_times:
                    d = d.replace(hour=run_at.hour, minute=run_at.minute, second=run_at.second)
                    date_times.append(d)

        return date_times
