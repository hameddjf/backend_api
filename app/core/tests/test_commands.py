"""
test custom django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# this command were going to be mocking database
@patch("core.management.commands.wait_for_db.Command.check")
class ComandTests(SimpleTestCase):
    """test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """test waiting for database ready."""

        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')  # On start delays, ensure the database is present
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """ test waiting for database when getting OperationalError . """
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 6)  # 2 + 3 + True = 6
        patched_check.assert_called_with(databases=['default'])
