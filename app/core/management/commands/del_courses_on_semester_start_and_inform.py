from django.core.mail import send_mail, mail_admins
from django.core.management import BaseCommand
from django.apps import apps

from django.utils import timezone


class Command(BaseCommand):
    help = "Delete students and profs connected to courses on semester start"

    def handle(self, *args, **options):
        today = timezone.now()
        subject = 'We deleted your account upon your estimated university exit - AppreciateU'
        from_address = None
        message = (f'Since this is the start of the new semester, we deleted your courses '
                   f'as from {today.strftime("%Y-%m-%d")}.'
                   f'Please select new courses you are involved with '
                   f'if you need better recommmendation lists of users that '
                   f'you can send your thanks to.\nCheers, your AppreciateU Team')

        all_students = apps.get_model('core', 'Student').objects.all()
        for student in all_students.iterator():
            student.course_set.clear()
            greeting = f'Hello, {student.user.name}\n!'
            emails = [student.user.email, student.user.google_email]
            send_mail(subject,
                      greeting + message,
                      from_address,
                      emails,
                      fail_silently=True)

        all_courses = apps.get_model('core', 'Course').objects.all()
        for course in all_courses.iterator():
            prof = course.professor
            course.professor = None
            course.save()
            greeting = f'Hello, Professor {prof.user.name}\n!'
            emails = [prof.user.email, prof.user.google_email]
            send_mail(subject,
                      greeting + message,
                      from_address,
                      emails,
                      fail_silently=True)

        mail_admins(subject="Course deletion", message="Deleted Courses", html_message=None)

        self.stdout.write("Course deletion complete.")
