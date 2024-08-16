# Generated by Django 4.2.13 on 2024-08-05 09:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import xrechnung_light.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('xrechnung_light', '0022_alter_customerparty_generic_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerparty',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='party_contact_email',
            field=models.CharField(max_length=300, verbose_name='E-Mail-Adresse'),
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='party_legal_entity_id',
            field=models.CharField(help_text='Handelsregister ID oder Umsatzsteuer ID', max_length=300, verbose_name='Rechtliche Identifikationsnummer'),
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='party_legal_entity_name',
            field=models.CharField(max_length=300, verbose_name='Rechtliche Bezeichnung'),
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='party_name',
            field=models.CharField(help_text='BT-44', max_length=300, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='customerparty',
            name='party_postal_address',
            field=models.ForeignKey(help_text='BT-50 - BT-55', on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.postaladdress', verbose_name='Postalische Adresse'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='actual_delivery_date',
            field=models.DateField(help_text="Tatsächliches Datum der Lieferung (BT-72). Beispiel: '2024-08-02'", verbose_name='Lieferdatum'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='buyer_reference',
            field=models.CharField(help_text='In Deutschland auch Leitweg-ID, wird vom oft Käufer vorgegeben (BT-10).', max_length=1024, verbose_name='Käuferreferenz'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_party',
            field=models.ForeignKey(help_text='Informationen zum Kunden (BG-7).', on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.customerparty', verbose_name='Kunde'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(help_text="Fälligkeitsdatum der Rechnung (BT-9). Beispiel: '2024-08-30'", verbose_name='Fälligkeitsdatum'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='identifier',
            field=models.CharField(help_text="Eindeutige Rechnugsnummer des Verkäufers (BT-1). Beispiel: '34-321321'", max_length=300, verbose_name='Rechnungsnummer'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='issue_date',
            field=models.DateField(help_text="Ausstellungsdatum der Rechnung (BT-2). Beispiel: '2024-07-30'", verbose_name='Rechnungsdatum'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='my_party',
            field=models.ForeignKey(help_text='Informationen zum Verkäufer (BG-4).', on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.myparty', verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='order_reference',
            field=models.CharField(help_text='Vom Käufer vorgegeben (BT-13).', max_length=1024, verbose_name='Bestellreferenz'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_terms',
            field=models.CharField(help_text='Freitext für Informationen zu den Zahlungbedingungen. (BT-20).', max_length=4096, verbose_name='Zahlungsbedingungen'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='prepaid_amount',
            field=models.DecimalField(decimal_places=2, help_text='Betrag, der schon im Voraus geleistet wurde. (BT-X).', max_digits=16, verbose_name='Vorausleistung'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='project_reference_id',
            field=models.CharField(help_text='Identifikationsbezeichnung des Projektes. (BT-11).', max_length=1024, verbose_name='Projekt-ID'),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='attachment',
            field=models.FileField(blank=True, help_text='https://docs.peppol.eu/poacc/billing/3.0/codelist/MimeCode/', null=True, upload_to=xrechnung_light.models.InvoiceAttachment.get_upload_path, verbose_name='Dokument'),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='description',
            field=models.CharField(max_length=4096, verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='identifier',
            field=models.CharField(max_length=1024, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='invoiceattachment',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.invoice', verbose_name='Rechnung'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.invoice', verbose_name='Rechnung'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='item_description',
            field=models.CharField(max_length=300, verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='item_name',
            field=models.CharField(max_length=300, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='number_of_units',
            field=models.IntegerField(verbose_name='Menge'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='price_per_unit',
            field=models.DecimalField(decimal_places=2, max_digits=16, verbose_name='Einzelpreis'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='tax',
            field=models.DecimalField(decimal_places=2, help_text="Beispiel: '19.00'", max_digits=16, verbose_name='Steuersatz in %'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='unit',
            field=models.CharField(choices=[('H87', 'Stück'), ('C62', 'ein'), ('MTK', 'Quadratmeter'), ('LM', 'Laufende Meter')], max_length=5, verbose_name='Einheit'),
        ),
        migrations.AlterField(
            model_name='logmessage',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_contact_email',
            field=models.CharField(help_text='BT-43', max_length=300, verbose_name='E-Mail-Adresse'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_contact_person_email',
            field=models.CharField(max_length=300, verbose_name='Kontaktperson E-Mail'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_contact_person_name',
            field=models.CharField(max_length=300, verbose_name='Kontaktperson'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_contact_person_phone',
            field=models.CharField(max_length=300, verbose_name='Kontaktperson Telefon'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_legal_entity_id',
            field=models.CharField(help_text='BT-32', max_length=300, verbose_name='Rechtliche Identifikationsnummer'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_legal_entity_name',
            field=models.CharField(help_text='BT-27', max_length=300, verbose_name='Rechtlicher Bezeichnung'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_name',
            field=models.CharField(help_text='BT-44', max_length=300, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_payment_financial_account_id',
            field=models.CharField(help_text='BT-44', max_length=300, verbose_name='IBAN'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_payment_financial_account_name',
            field=models.CharField(max_length=300, verbose_name='Name des Kontoinhabers'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_payment_financial_institution_id',
            field=models.CharField(max_length=300, verbose_name='BIC'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_postal_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xrechnung_light.postaladdress', verbose_name='Postalische Adresse'),
        ),
        migrations.AlterField(
            model_name='myparty',
            name='party_tax_id',
            field=models.CharField(help_text='BT-X', max_length=300, verbose_name='Umsatzsteuer ID'),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='city_name',
            field=models.CharField(help_text="Beispiel: 'Musterdorf'", max_length=300, verbose_name='Stadt/Ort'),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='country_subentity',
            field=models.CharField(choices=[('RLP', 'Rheinland-Pfalz'), ('HE', 'Hessen')], default='RLP', max_length=128, verbose_name='Bundesland'),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='generic_id',
            field=models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c')),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='postal_zone',
            field=models.CharField(help_text="Beispiel: '12345'", max_length=128, verbose_name='Postleitzahl'),
        ),
        migrations.CreateModel(
            name='InvoiceXml',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generic_id', models.UUIDField(default=uuid.UUID('ef103c3b-0810-4c38-b5e3-89f494ac1d2c'))),
                ('created', models.DateTimeField(null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('deleted', models.DateTimeField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=1024, verbose_name='Name')),
                ('description', models.CharField(max_length=4096, verbose_name='Beschreibung')),
                ('attachment', models.FileField(blank=True, help_text='https://docs.peppol.eu/poacc/billing/3.0/codelist/MimeCode/', null=True, upload_to=xrechnung_light.models.InvoiceXml.get_upload_path, verbose_name='Dokument')),
                ('owned_by_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
