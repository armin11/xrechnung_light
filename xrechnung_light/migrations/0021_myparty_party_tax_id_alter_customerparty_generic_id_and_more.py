# Generated by Django 4.2.13 on 2024-08-02 11:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('xrechnung_light', '0020_alter_customerparty_generic_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='myparty',
            name='party_tax_id',
            field=models.CharField(default='dfd/hdahd/jsjaD', max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='logmessage',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('cf5923d5-51b9-4ef7-a675-8822c10fb295')),
        ),
    ]
