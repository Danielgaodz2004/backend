from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_codes():
    Code.objects.create(
        name="01001001000100",
        description="01001001000100010010010001000100100100010001001001000100010010010001000100100100010001001001000100010010010001000100100100010001001001000100",
        weight=128,
        image="1.png"
    )

    Code.objects.create(
        name="101000101101101",
        description="101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101101000101101101",
        weight=64,
        image="2.png"
    )

    Code.objects.create(
        name="0101011110101010",
        description="01010111101010100101011110101010010101111010101001010111101010100101011110101010010101111010101001010111101010100101011110101010010101111010101001010111101010100101011110101010",
        weight=32,
        image="3.png"
    )

    Code.objects.create(
        name="10110111101101001",
        description="10110111101101001101101111011010011011011110110100110110111101101001101101111011010011011011110110100110110111101101001101101111011010011011011110110100110110111101101001",
        weight=256,
        image="4.png"
    )

    Code.objects.create(
        name="10101101011001010",
        description="10101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100101010101101011001010101011010110010101010110101100",
        weight=128,
        image="5.png"
    )

    Code.objects.create(
        name="010101001001010010",
        description="0101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010010010100100101010",
        weight=16,
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_calculations():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    codes = Code.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_calculation(status, codes, owner, moderators)

    add_calculation(1, codes, users[0], moderators)
    add_calculation(2, codes, users[0], moderators)
    add_calculation(3, codes, users[0], moderators)
    add_calculation(4, codes, users[0], moderators)
    add_calculation(5, codes, users[0], moderators)


def add_calculation(status, codes, owner, moderators):
    calculation = Calculation.objects.create()
    calculation.status = status

    if status in [3, 4]:
        calculation.moderator = random.choice(moderators)
        calculation.date_complete = random_date()
        calculation.date_formation = calculation.date_complete - random_timedelta()
        calculation.date_created = calculation.date_formation - random_timedelta()
    else:
        calculation.date_formation = random_date()
        calculation.date_created = calculation.date_formation - random_timedelta()

    if status == 3:
        calculation.result = random.randint(1, 10)

    calculation.calculation_type = "Шифрование"

    calculation.owner = owner

    i = 1
    for code in random.sample(list(codes), 3):
        item = CodeCalculation(
            calculation=calculation,
            code=code,
            order=i
        )
        item.save()
        i += 1

    calculation.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_codes()
        add_calculations()
