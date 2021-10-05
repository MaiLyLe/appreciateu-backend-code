from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
import random
from django.apps import apps


def parse_boolean(b):
    return b == "True "


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Add random messages for user John Wayne in last 6 months"""
        # number_of_messages = 300

        # for x in range(number_of_messages):
        #     random_num = random.randrange(0, 179) + 1
        #     avatar = random.randrange(0, 9) + 1
        #     receiver_id = random.randrange(1, 47) + 1
        #     date = timezone.now() - timedelta(days=random_num)

        #     sender = apps.get_model('core', 'User').objects.filter(id=2)[0]
        #     receiver = apps.get_model('core', 'User').objects.filter(id=receiver_id)[0]
        #     apps.get_model('core', 'Message').objects.create(
        #         text='you cool',
        #         sender=sender,
        #         receiver=receiver,
        #         thanked=True,
        #         avatar_num=avatar,
        #         timestamp=date,
        #     )

        # for x in range(number_of_messages):
        #     random_num = random.randrange(0, 179) + 1
        #     avatar = random.randrange(0, 9) + 1
        #     sender_id = random.randrange(1, 47) + 1
        #     date = timezone.now() - timedelta(days=random_num)

        #     receiver = apps.get_model('core', 'User').objects.filter(id=2)[0]
        #     sender = apps.get_model('core', 'User').objects.filter(id=sender_id)[0]
        #     apps.get_model('core', 'Message').objects.create(
        #         text='you cool',
        #         sender=sender,
        #         receiver=receiver,
        #         thanked=True,
        #         avatar_num=avatar,
        #         timestamp=date
        #     )
        apps.get_model('core', 'Message').objects.all().update(is_seen=True)
