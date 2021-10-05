from django.core.management.base import BaseCommand
from django.utils import timezone
from pathlib import Path
import os
from datetime import datetime
from django.apps import apps
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing student attributes to existing student models from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Student.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        student_user = apps.get_model('core', 'User').objects.filter(
                            email=row['user_email'])
                        if student_user.exists():
                            entry_sem_date = datetime.strptime(row['entry_semester'], '%d-%m-%Y')\
                                .replace(tzinfo=timezone.utc)
                            field_of_studies = apps.get_model('core', 'FieldOfStudies')\
                                .objects.get(id=int(row['field_of_studies'][0]))
                            institute = apps.get_model('core', 'Institute').objects.get(
                                name=row["institute"])
                            apps.get_model('core', 'Student').objects.filter(user=student_user[0])\
                                .update(field_of_studies=field_of_studies,
                                        entry_semester=entry_sem_date, institute=institute)
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(
                    current_file, e.errno, e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
