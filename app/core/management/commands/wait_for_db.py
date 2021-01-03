from django.core.management.base import BaseCommand
import time
from django.db.utils import OperationalError
from django.db import connections


class Command(BaseCommand):
    """Command to wait for db to start before running server"""
    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for DB Connection...')
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections['default']
                self.stdout.write(self.style.SUCCESS('DB available'))
            except OperationalError:
                self.stdout.write('DB not available - waiting another sec...')
                time.sleep(1)
