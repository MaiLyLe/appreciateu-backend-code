from django.core.management.base import BaseCommand
from pathlib import Path
import os
from django.apps import apps
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing institute objects into model from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Institute.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        institute = apps.get_model('core', 'Institute').objects.filter(id=counter)
                        if institute.exists():
                            institute.delete()
                        apps.get_model('core', 'Institute').objects.create(name=row['name'],
                                                                           id=counter)
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(
                    current_file, e.errno, e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
