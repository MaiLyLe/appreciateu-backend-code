from django.core.management.base import BaseCommand
from pathlib import Path
import os
from django.apps import apps
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing course objects into model from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Course.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        course = apps.get_model('core', 'Course').objects.filter(id=counter)
                        if course.exists():
                            course.delete()
                        field_of_studies = apps.get_model('core', 'FieldOfStudies').objects.get(
                            id=int(row['field_of_studies'][0]))
                        professor = apps.get_model('core', 'Professor').objects.get(
                            user__email=row['professor'])
                        apps.get_model('core', 'Course').objects.create(
                            name=row['name'],
                            professor=professor, field_of_studies=field_of_studies)
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(
                    current_file, e.errno, e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
