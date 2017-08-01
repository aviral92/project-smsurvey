import unittest
import pytz

from datetime import datetime, time, timedelta

from smsurvey.schedule.time_rule.time_rule import NoRepeatTimeRule, RepeatsDailyTimeRule, RepeatsMonthlyDate,\
    RepeatsMonthlyDay


class TestNoRepeatTimeRule(unittest.TestCase):

    def test_gets_timestamp(self):
        now = datetime.now()
        tr = NoRepeatTimeRule(now)
        self.assertTrue(len(tr.get_date_times()) == 1)
        self.assertEqual(now, tr.get_date_times()[0])

    def test_from_params(self):
        tr = NoRepeatTimeRule.from_params("2020-12-12 11:59:12")
        self.assertTrue(len(tr.get_date_times()) == 1)
        self.assertEqual(datetime.strptime("2020-12-12 11:59:12", "%Y-%m-%d %H:%M:%S"), tr.get_date_times()[0])


class TestRepeatsDailyTimeRule(unittest.TestCase):

    def test_gets_timestamp(self):
        starting_from = datetime.now()
        every = 2
        until = starting_from + timedelta(days=100)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsDailyTimeRule(starting_from, every, until, run_at)
        dts = tr.get_date_times()
        self.assertTrue(len(dts) == 50)

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)

    def test_from_params(self):
        params = "2017-07-31~2~2017-11-08~12:00:00 UTC"
        tr = RepeatsDailyTimeRule.from_params(params)
        dts = tr.get_date_times()
        self.assertTrue(len(dts) == 50)

        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)


class TestRepeatsMonthlyDateTimeRule(unittest.TestCase):

    def test_gets_timestamp(self):
        every = 1
        days_of_month = [1, 15, 25]
        until = datetime.now() + timedelta(days=365)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsMonthlyDate(every, days_of_month, until, run_at)
        dts = tr.get_date_times()

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)
            self.assertTrue(dt.day in [1, 15, 25])

    def test_from_params(self):
        tr = RepeatsMonthlyDate.from_params("1~1, 15, 25~2018-08-01 ~12:00:00 UTC")
        dts = tr.get_date_times()
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)
            self.assertTrue(dt.day in [1, 15, 25])


class TestRepeatsMonthlyDayTimeRule(unittest.TestCase):

    def test_gets_timestamp(self):
        every = 1
        param1 = "second"
        day_of_week = 2
        until = datetime.now() + timedelta(days=365)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsMonthlyDay(every, param1, day_of_week, until, run_at)
        dts = tr.get_date_times()

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)
            self.assertEqual(dt.weekday(), 2)

    def test_from_params(self):
        tr = RepeatsMonthlyDay.from_params("1~second~2~2018-08-01 ~12:00:00 UTC")
        dts = tr.get_date_times()
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)
            self.assertEqual(dt.weekday(), 2)
