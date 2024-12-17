from django.db.models import TextChoices


class RecordState(TextChoices):
    PENDING = 'PENDING', 'В ожидании'
    APPROVED = 'APPROVED', 'Одобренный'
    REJECTED = 'REJECTED', 'Отклоненный'
