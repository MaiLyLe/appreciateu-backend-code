from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available
        Code is taken from https://www.udemy.com/course/django-python-advanced/"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db
        Code is taken from https://www.udemy.com/course/django-python-advanced/"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 10 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 11)
