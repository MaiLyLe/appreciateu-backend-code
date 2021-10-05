from django.core.management.base import BaseCommand
from pathlib import Path
import os
from django.apps import apps
import csv


def parse_boolean(b):
    return b == "True "


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command for parsing institute objects into model from csv"""
        current_file = os.path.basename(__file__)
        path = "/csv_model_files/Message.csv"
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    counter = 1
                    for row in my_reader:
                        receiver = apps.get_model('core', 'User').objects.filter(
                            email=row['receiver'])[0]
                        sender = apps.get_model('core', 'User').objects.filter(
                            email=row['sender'])[0]
                        if receiver is not None and sender is not None:
                            apps.get_model('core', 'Message').objects.create(
                                text=row['text'],
                                sender=sender,
                                receiver=receiver,
                                thanked=parse_boolean(row['thanked']),
                                avatar_num=row['avatar_num']
                            )
                        counter = counter + 1
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(
                    current_file, e.errno, e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
