# Generated by Django 3.1.4 on 2021-09-28 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_user_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='approx_exit_semester',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
