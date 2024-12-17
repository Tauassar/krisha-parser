import datetime
import re

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime

from .enum import RecordState


class TimestampModel(models.Model):
    created_at: 'datetime.datetime' = models.DateTimeField(
        "Время создания",
        auto_now_add=True,
        db_index=True,
    )
    changed_at: 'datetime.datetime' = models.DateTimeField(
        "Время последнего изменения",
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True

    @property
    def created_at_pretty(self) -> str:
        return localtime(self.created_at).strftime("%d.%m.%Y %H:%M:%S")

    created_at_pretty.fget.short_description = "Время создания"

    @property
    def updated_at_pretty(self) -> str:
        return localtime(self.changed_at).strftime("%d.%m.%Y %H:%M:%S")

    updated_at_pretty.fget.short_description = "Время последнего изменения"


class Record(TimestampModel):
    state: RecordState = models.CharField(choices=RecordState, default=RecordState.PENDING, max_length=16)
    kid: str = models.CharField(unique=True, max_length=64)
    data: dict = models.JSONField(default=dict)
    comment: str = models.TextField(blank=True, default="")
    expired: bool = models.BooleanField(default=False)
    price: int | None = models.IntegerField(null=True, default=None)

    def __str__(self):
        return self.kid

    @property
    def plain_link(self):
        return f"https://krisha.kz/a/show/{self.kid}"

    @property
    def krisha_link(self):
        return mark_safe(f'<a href="{self.plain_link}" target="_blank">Перейти</a>')

    @property
    def residential_complex(self):
        return self.data.get("residential_complex")

    @property
    def floor(self):
        return self.data.get("floor")

    @property
    def max_floor(self):
        return self.data.get("max_floor")

    @property
    def post_date(self):
        return datetime.datetime.strptime(self.data.get("post_date"), "%Y-%m-%d").date()

    @property
    def krisha_created_at(self):
        return datetime.datetime.strptime(self.data.get("created_at"), "%Y-%m-%d").date()

    @property
    def full_address(self):
        return self.data.get("full_address")

    @property
    def area(self):
        return self.data.get("Площадь, м²")

    @property
    def total_price(self):
        if self.price and self.area:
            numbers = [float(num) for num in re.findall(r'\d+\.\d+|\d+', self.area)]
            max_number = max(numbers)
            max_integer = int(max_number)
            return round(max_integer * self.price / 500000) * 500000
        return None

    @property
    def description(self):
        return self.data.get("description")


class ParsingProcess(TimestampModel):
    pid: str = models.CharField(unique=True, max_length=64)
