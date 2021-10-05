from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pathlib import Path
import os
from django.apps import apps
import csv


def parse_boolean(b):
    return b == "True "


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Command for parsing user objects into model from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/User.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = apps.get_model('core', 'User').objects.count() + 1
                    for row in my_reader:
                        user = apps.get_model('core', 'User').objects.filter(email=row['email'])
                        if user.exists():
                            user.delete()
                        get_user_model().objects.create_user(
                                            name=row['name'],
                                            id=counter,
                                            email=row['email'],
                                            password=row['password'],
                                            is_student=parse_boolean(row['is_student']),
                                            is_staff=parse_boolean(row['is_staff']),
                                            is_professor=parse_boolean(row['is_professor']),
                                            is_university_administrator=parse_boolean(
                                                row['is_university_administrator']),
                                            is_active=parse_boolean(row['is_active']),
                                            avatar_num=row['avatar_num'])
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(
                    current_file, e.errno, e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
