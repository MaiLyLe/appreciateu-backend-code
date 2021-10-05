# Generated by Django 3.1.4 on 2021-09-01 14:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_student', models.BooleanField(default=False)),
                ('google_email', models.CharField(blank=True, max_length=255)),
                ('is_professor', models.BooleanField(default=False)),
                ('is_university_administrator', models.BooleanField(default=False)),
                ('avatar_num', models.CharField(default='1', max_length=3)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FieldOfStudies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UniversityAdministrator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_of_institute', models.BooleanField(default=False)),
                ('profession_description', models.CharField(max_length=1000, null=True)),
                ('institute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_semester', models.DateTimeField(blank=True, null=True)),
                ('field_of_studies', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.fieldofstudies')),
                ('institute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_of_expertise', models.CharField(max_length=1000)),
                ('field_of_studies', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.fieldofstudies')),
                ('institute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=2000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('thanked', models.BooleanField(default=False)),
                ('is_seen', models.BooleanField(default=False)),
                ('is_positive', models.BooleanField(default=False)),
                ('avatar_num', models.CharField(default='1', max_length=3)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_received', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_sent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GoogleContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('contact_owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='google_identity', to=settings.AUTH_USER_MODEL)),
                ('owned_contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_google_contact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='fieldofstudies',
            name='institute',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.institute'),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('field_of_studies', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.fieldofstudies')),
                ('professor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.professor')),
                ('students', models.ManyToManyField(to='core.Student')),
            ],
        ),
    ]
