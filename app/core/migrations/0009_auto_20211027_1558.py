# Generated by Django 3.1.4 on 2021-10-27 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_student_approx_exit_semester'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googlecontact',
            name='last_updated',
        ),
        migrations.RemoveField(
            model_name='message',
            name='thanked',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_university_administrator',
        ),
        migrations.AlterField(
            model_name='googlecontact',
            name='contact_owner',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='google_identity', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='googlecontact',
            name='owned_contact',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_google_contact', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='UniversityAdministrator',
        ),
    ]
