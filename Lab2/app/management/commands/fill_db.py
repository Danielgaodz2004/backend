import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta, calc


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


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

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_calculations():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    codes = Code.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_calculation(status, codes, owner, moderators)

    add_calculation(1, codes, users[0], moderators)
    add_calculation(2, codes, users[0], moderators)

    print("Заявки добавлены")


def add_calculation(status, codes, owner, moderators):
    calculation = Calculation.objects.create()
    calculation.status = status

    if calculation.status in [3, 4]:
        calculation.moderator = random.choice(moderators)
        calculation.date_complete = random_date()
        calculation.date_formation = calculation.date_complete - random_timedelta()
        calculation.date_created = calculation.date_formation - random_timedelta()
    else:
        calculation.date_formation = random_date()
        calculation.date_created = calculation.date_formation - random_timedelta()

    calculation.owner = owner

    calculation.type = "Шифрование"

    if calculation.status == 3:
        calculation.result = calc()

    i = 1

    for code in random.sample(list(codes), 3):
        item = CodeCalculation(
            calculation=calculation,
            code=code,
            value=i
        )
        item.save()
        i += 1

    calculation.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_codes()
        add_calculations()
