# Generated by Django 4.2.13 on 2024-07-25 17:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('xrechnung_light', '0004_logmessage_active_logmessage_changed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logmessage',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('aa5d5943-e0be-46d2-879a-36b7c8a644bb')),
        ),
    ]
