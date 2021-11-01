from django.core.mail import send_mail, mail_admins
from django.core.management import BaseCommand
from django.apps import apps
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete students whose approx_exit_semester date has passed"

    def handle(self, *args, **options):
        """Command to delete all students if their approx_exit_semester has passed and sends
        information email
        - is called by Redis/Celery every start of semester which is 1th Apr. and 1th Oct."""
        today = timezone.now()
        from_address = None
        subject = 'Course deletion upon semester start - AppreciateU'
        message = (f'We are sending you this email to inform you that we deleted your account '
                   f'as from {today.strftime("%Y-%m-%d")}. '
                   f'This has been done based on your estimated drop out date. '
                   f'If this date is wrong and if you are still studying at this university '
                   f'please register once more.\n'
                   f'Cheers, your AppreciateU Team')

        all_students = apps.get_model('core', 'Student').objects.all()
        for student in all_students.iterator():
            if student.approx_exit_semester is not None:
                if student.approx_exit_semester < today:
                    student.user.delete()
                    greeting = f'Hello, {student.user.name}\n!'
                    emails = [student.user.email, student.user.google_email]
                    send_mail(subject,
                              greeting + message,
                              from_address,
                              emails,
                              fail_silently=True)

        mail_admins(subject="User deletion upon exit",
                    message="Deleted Students that dropped out.",
                    html_message=None)

        self.stdout.write("Deletion of students that dropped out of university done.")
