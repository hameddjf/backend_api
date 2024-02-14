"""
test custom django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperaationalError
from django.test import SimpleTestCase

@patch("core.management.commands.wait_for_db.Command.check")# this command were going to be mocking
class ComandTests(SimpleTestCase):
    """test commands."""

    def test_wait_for_db_ready(self , patched_check):
        """test waiting for database ready."""

        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(database=['default'])