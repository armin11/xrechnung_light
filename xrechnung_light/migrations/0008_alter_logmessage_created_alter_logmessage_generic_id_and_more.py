# Generated by Django 4.2.13 on 2024-07-30 19:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('xrechnung_light', '0007_alter_logmessage_generic_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logmessage',
            name='created',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='logmessage',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('a01ee7eb-317f-4337-99b1-d588e1f8d13a')),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='created',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('a01ee7eb-317f-4337-99b1-d588e1f8d13a')),
        ),
    ]
