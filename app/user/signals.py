from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from core.models import Student, Professor, UniversityAdministrator


@receiver(post_save, sender=get_user_model())
def create_role(sender, instance, created, **kwargs):
    """Signal that listens to user creation and looks whether role is checked"""
    if created:
        if instance.is_professor is True:
            Professor.objects.create(user=instance)
        if instance.is_student is True:
            Student.objects.create(user=instance)
        if instance.is_university_administrator is True:
            UniversityAdministrator.objects.create(user=instance)
