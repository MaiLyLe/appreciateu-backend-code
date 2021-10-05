from django.core.management.base import BaseCommand
from pathlib import Path
import os
from django.apps import apps
import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Command to add courses objects to specific students from csv"""
        current_file = os.path.basename(__file__)
        path = '/csv_model_files/Course Student.csv'
        if Path(path).is_file():
            try:
                with open(path, 'r') as file:
                    my_reader = csv.DictReader(file, delimiter=',')
                    course_names = my_reader.fieldnames[1:]
                    for row in my_reader:
                        student = apps.get_model('core', 'Student').objects.filter(
                            user__email=row["student"])
                        if student.exists():
                            for course_name in course_names:
                                course = apps.get_model('core', 'Course').objects.filter(
                                    name=course_name)
                                if course.exists():
                                    course_id = course[0].id
                                    if row[course_name] == "True ":
                                        student[0].course_set.add(course_id)
                                        course[0].students.add(student[0].id)
                                    else:
                                        student[0].course_set.remove(course_id)
                                        course[0].students.remove(student[0].id)
            except IOError as e:
                self.stdout.write("In '{0}': I/O error({1}): {2}".format(current_file, e.errno,
                                                                         e.strerror))
        else:
            self.stdout.write(f'File {path} not found.')
