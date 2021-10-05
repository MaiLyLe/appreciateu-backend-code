from django.core.management.base import BaseCommand
from django.apps import apps
from pathlib import Path
import os
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing course of studies objects into models from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Field of Studies.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        institute = apps.get_model('core', 'Institute').objects.get(
                            id=str(row['foreignkeyrow']))
                        field_of_studies = apps.get_model('core', 'FieldOfStudies').objects.\
                            filter(id=counter)
                        if field_of_studies.exists():
                            field_of_studies.delete()
                        field_of_studies = apps.get_model('core', 'FieldOfStudies').objects.\
                            create(name=row['name'], id=counter, institute=institute)
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(current_file, e.errno,
                                                                         e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
