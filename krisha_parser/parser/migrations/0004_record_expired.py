# Generated by Django 5.0.9 on 2024-11-30 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0003_record_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='expired',
            field=models.TextField(default=False),
        ),
    ]
