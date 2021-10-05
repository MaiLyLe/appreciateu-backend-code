from django.core.management.base import BaseCommand
from pathlib import Path
import os
from django.apps import apps
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing professor attributes into existing professor models from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Professor.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        professor_user = apps.get_model('core', 'User').objects.filter(
                            email=row['user_email'])
                        if professor_user.exists():
                            institute = apps.get_model('core', 'Institute').objects\
                                .get(name=row['institute'])
                            field_of_studies = apps.get_model('core', 'FieldOfStudies').objects\
                                .get(id=int(row['field_of_studies'][0]))
                            apps.get_model('core', 'Professor').objects.filter(
                                user=professor_user[0]).update(
                                    field_of_studies=field_of_studies,
                                    institute=institute)

                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(current_file, e.errno,
                                                                         e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
