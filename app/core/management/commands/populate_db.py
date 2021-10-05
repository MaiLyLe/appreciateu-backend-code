from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command to populate whole db for testing purposes"""
        call_command('populate_institute')
        call_command('populate_field_of_studies')
        call_command('populate_user')
        call_command('populate_student')
        call_command('populate_professor')
        call_command('populate_course')
        call_command('add_courses_to_student')
        call_command('populate_message')
