from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Code(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Бинарный код",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    weight = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Данные"
        verbose_name_plural = "Данные"
        db_table = "codes"
        ordering = ("pk",)


class Calculation(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True,  null=True)

    calculation_type = models.CharField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Запрос №" + str(self.pk)

    class Meta:
        verbose_name = "Запрос"
        verbose_name_plural = "Запросы"
        db_table = "calculations"
        ordering = ('-date_formation', )


class CodeCalculation(models.Model):
    code = models.ForeignKey(Code, on_delete=models.DO_NOTHING, blank=True, null=True)
    calculation = models.ForeignKey(Calculation, on_delete=models.DO_NOTHING, blank=True, null=True)
    order = models.IntegerField(verbose_name="Поле м-м", default=1)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "code_calculation"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['code', 'calculation'], name="code_calculation_constraint")
        ]
