import unittest
import pytz

from datetime import datetime, time, timedelta

from smsurvey.schedule.time_rule.time_rule import NoRepeat, RepeatsDaily, RepeatsMonthlyDate, RepeatsMonthlyDay,\
    RepeatsWeekly


class TestNoRepeatTimeRule(unittest.TestCase):
    def test_gets_timestamp(self):
        now = datetime.now()
        tr = NoRepeat(now, [now])
        self.assertTrue(len(tr.get_date_times()) == 1)
        self.assertEqual(now, tr.get_date_times()[0])

    def test_from_params(self):
        tr = NoRepeat.from_params("2020-12-12 ~11:59:12 &14:59:12 ")
        self.assertTrue(len(tr.get_date_times()) == 2)
        self.assertEqual(datetime.strptime("2020-12-12 11:59:12", "%Y-%m-%d %H:%M:%S"), tr.get_date_times()[0])
        self.assertEqual(datetime.strptime("2020-12-12 14:59:12", "%Y-%m-%d %H:%M:%S"), tr.get_date_times()[1])

    def test_to_params(self):
        now = datetime.now()
        tr = NoRepeat(now, [now])
        expected = now.strftime("%Y-%m-%d ~%H:%M:%S %Z")
        actual = tr.to_params
        self.assertEqual(expected, actual)


class TestRepeatsDailyTimeRule(unittest.TestCase):
    def test_gets_timestamp(self):
        starting_from = datetime.now()
        every = 2
        until = starting_from + timedelta(days=100)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsDaily(starting_from, every, until, run_at)
        dts = tr.get_date_times()
        self.assertTrue(len(dts) == 50)

        for dt in dts:
            self.assertEqual(dt.hour, run_at[0].hour)
            self.assertEqual(dt.minute, run_at[0].minute)
            self.assertEqual(dt.second, run_at[0].second)

    def test_from_params(self):
        params = "2017-07-31~2~2017-11-08~12:00:00 UTC"
        tr = RepeatsDaily.from_params(params)
        dts = tr.get_date_times()
        self.assertTrue(len(dts) == 50)

        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        for dt in dts:
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)

    def test_to_params(self):
        starting_from = datetime.now()
        every = 2
        until = starting_from + timedelta(days=100)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsDaily(starting_from, every, until, run_at)
        expected = starting_from.strftime("%Y-%m-%d %Z") + "~" + str(every) + "~" + until.strftime("%Y-%m-%d %Z") + "~" \
                   + run_at[0].strftime("%H:%M:%S %Z")
        actual = tr.to_params
        self.assertEqual(expected, actual)


class TestRepeatsMonthlyDateTimeRule(unittest.TestCase):
    def test_gets_timestamp(self):
        every = 1
        days_of_month = [1, 15, 25]
        until = datetime.now() + timedelta(days=365)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsMonthlyDate(every, days_of_month, until, run_at)
        dts = tr.get_date_times()

        for dt in dts:
            self.assertEqual(dt.hour, run_at[0].hour)
            self.assertEqual(dt.minute, run_at[0].minute)
            self.assertEqual(dt.second, run_at[0].second)
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

    def test_to_params(self):
        every = 1
        days_of_month = [1, 15, 25]
        until = datetime.now() + timedelta(days=365)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsMonthlyDate(every, days_of_month, until, run_at)

        expected = str(every) + "~" + str(days_of_month)[1:-1] + "~" + until.strftime("%Y-%m-%d %Z") + "~" \
                   + run_at[0].strftime("%H:%M:%S %Z")

        actual = tr.to_params
        self.assertEqual(expected, actual)


class TestRepeatsMonthlyDayTimeRule(unittest.TestCase):
    def test_gets_timestamp(self):
        every = 1
        param1 = "second"
        days_of_week = [2]
        until = datetime.now() + timedelta(days=365)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsMonthlyDay(every, param1, days_of_week, until, run_at)
        dts = tr.get_date_times()

        for dt in dts:
            self.assertEqual(dt.hour, run_at[0].hour)
            self.assertEqual(dt.minute, run_at[0].minute)
            self.assertEqual(dt.second, run_at[0].second)
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

    def test_to_params(self):
        every = 1
        param1 = "second"
        day_of_week = [2]
        until = datetime.now() + timedelta(days=365)
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        tr = RepeatsMonthlyDay(every, param1, day_of_week, until, run_at)

        expected = str(every) + "~" + param1 + "~" + str(day_of_week[0]) + "~" + until.strftime("%Y-%m-%d %Z") + "~" \
            + run_at[0].strftime("%H:%M:%S %Z")

        actual = tr.to_params

        self.assertEqual(expected, actual)


class TestRepeatsWeekly(unittest.TestCase):
    def test_get_timestamp(self):
        every = 1
        days = [0, 1, 3]
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        starting_from = datetime.now()
        until = datetime.now() + timedelta(days=365)

        tr = RepeatsWeekly(every, days, run_at, starting_from, until)
        dts = tr.get_date_times()

        for dt in dts:
            self.assertTrue(dt.weekday() in [0, 1, 3])
            self.assertEqual(dt.hour, run_at[0].hour)
            self.assertEqual(dt.minute, run_at[0].minute)
            self.assertEqual(dt.second, run_at[0].second)

    def test_from_params(self):
        tr = RepeatsWeekly.from_params("1~0, 1, 3~12:00:00 UTC~2017-08-04~2018-08-04 ")
        dts = tr.get_date_times()

        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        print(dts)

        for dt in dts:
            self.assertTrue(dt.weekday() in [0, 1, 3])
            self.assertEqual(dt.hour, run_at.hour)
            self.assertEqual(dt.minute, run_at.minute)
            self.assertEqual(dt.second, run_at.second)

    def test_to_params(self):
        every = 1
        days = [0, 1, 3]
        run_at = [time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)]
        starting_from = datetime.now()
        until = datetime.now() + timedelta(days=365)

        tr = RepeatsWeekly(every, days, run_at, starting_from, until)

        actual = tr.to_params
        expected = str(every) + "~" + str(days)[1:-1] + "~" + run_at[0].strftime("%H:%M:%S %Z") \
            + "~" + starting_from.strftime("%Y-%m-%d") + "~" + until.strftime("%Y-%m-%d %Z")

        self.assertEqual(actual, expected)
