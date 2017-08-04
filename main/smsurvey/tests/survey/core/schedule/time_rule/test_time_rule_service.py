import unittest
import pytz

from datetime import datetime, timedelta, time

from smsurvey import config
from smsurvey.utility_scripts.create_time_rule_store import get_dynamo, create
from smsurvey.schedule.time_rule.time_rule import NoRepeatTimeRule, RepeatsDailyTimeRule, RepeatsMonthlyDate, \
    RepeatsMonthlyDay, RepeatsWeekly
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService


class TestTimeRuleService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        t_name = create(force=True, test=True)
        cls.service = TimeRuleService(cache_name=t_name)

    def test_insert_get_no_repeat(self):
        now = datetime.now()
        tr = NoRepeatTimeRule(now)

        time_rule_id = self.service.insert('1', tr)
        actual = self.service.get('1', time_rule_id)

        self.assertEqual(actual.get_type(), 'no-repeat')

    def test_insert_get_repeat_daily(self):
        starting_from = datetime.now()
        every = 2
        until = starting_from + timedelta(days=100)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsDailyTimeRule(starting_from, every, until, run_at)

        time_rule_id = self.service.insert('2', tr)
        actual = self.service.get('2', time_rule_id)

        self.assertEqual(actual.get_type(), 'repeat-daily')

    def test_insert_get_repeat_monthly_date(self):
        every = 1
        days_of_month = [1, 15, 25]
        until = datetime.now() + timedelta(days=365)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsMonthlyDate(every, days_of_month, until, run_at)

        time_rule_id = self.service.insert('3', tr)
        actual = self.service.get('3', time_rule_id)

        self.assertEqual(actual.get_type(), 'repeat-monthly-date')

    def test_insert_get_repeat_monthly_day(self):
        every = 1
        param1 = "second"
        day_of_week = 2
        until = datetime.now() + timedelta(days=365)
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        tr = RepeatsMonthlyDay(every, param1, day_of_week, until, run_at)

        time_rule_id = self.service.insert('4', tr)
        actual = self.service.get('4', time_rule_id)

        self.assertEqual(actual.get_type(), 'repeat-monthly-day')

    def test_insert_get_repeat_weekly(self):
        every = 1
        days = [0, 1, 3]
        run_at = time(tzinfo=pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        starting_from = datetime.now()
        until = datetime.now() + timedelta(days=365)

        tr = RepeatsWeekly(every, days, run_at, starting_from, until)

        time_rule_id = self.service.insert('5', tr)
        actual = self.service.get('5', time_rule_id)

        self.assertEqual(actual.get_type(), 'repeat-weekly')

    def test_get_none(self):
        actual = self.service.get('6', '123')
        self.assertIsNone(actual)

    @classmethod
    def tearDownClass(cls):
        dynamo = get_dynamo(config.local)
        t_name = config.time_rule_backend_name + "Test"
        dynamo.delete_table(TableName=t_name)
