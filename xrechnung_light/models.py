from django.db import models
from django.urls import reverse
# Create your models here.
from django.utils import timezone
from django.utils.text import slugify
import os
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

import uuid, PIL
from io import BytesIO
import magic, base64

class GenericMetadata(models.Model):
    generic_id = models.UUIDField(default = uuid.uuid4)
    created = models.DateTimeField(null=True)
    changed = models.DateTimeField(null=True)
    deleted = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)
    owned_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    """def save(self, *args, **kwargs):
        self.owned_by_user= self.request.user
        super().save(*args, **kwargs)"""

class LogMessage(GenericMetadata):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"
    
class PostalAddress(GenericMetadata):
    RLP = "RLP"
    HE = "HE"
    FEDERAL_STATE_CHOICES = ((RLP, "Rheinland-Pfalz"), (HE, "Hessen"),)
    street_name = models.CharField(max_length=300, verbose_name="Strasse und Hausnummer", help_text="Beispiel: 'Musterstraße 10'")
    city_name = models.CharField(max_length=300, verbose_name="Stadt/Ort", help_text="Beispiel: 'Musterdorf'")
    postal_zone = models.CharField(max_length=128, verbose_name="Postleitzahl", help_text="Beispiel: '12345'")
    country_subentity = models.CharField(max_length=128,
        choices=FEDERAL_STATE_CHOICES,
        default=RLP, verbose_name="Bundesland")
    country = models.CharField(max_length=128)

    def __str__(self):
        """Returns a string representation of a postal address."""
        #date = timezone.localtime(self.log_date)
        return f"'{self.street_name}'\n'{self.postal_zone}' '{self.city_name}'\n'{self.country}'"
    
    def get_absolute_url(self):
        return reverse("postaladdress-detail", kwargs={"pk": self.pk})
    
class CustomerParty(GenericMetadata):
    party_name = models.CharField(max_length=300, verbose_name="Name", help_text="BT-44")
    party_contact_email = models.CharField(max_length=300, verbose_name="E-Mail-Adresse", help_text="")
    party_legal_entity_name = models.CharField(max_length=300, verbose_name="Rechtliche Bezeichnung", help_text="")
    party_legal_entity_id = models.CharField(max_length=300, verbose_name="Rechtliche Identifikationsnummer", help_text="Handelsregister ID oder Umsatzsteuer ID")
    party_postal_address = models.ForeignKey(PostalAddress, on_delete=models.CASCADE, verbose_name="Postalische Adresse", help_text="BT-50 - BT-55")

    def __str__(self):
        """Returns a string representation of a customer party."""
        return f"'{self.party_name}' \n '{self.party_contact_email}'"
    
    def get_absolute_url(self):
        return reverse("customerparty-detail", kwargs={"pk": self.pk})
    

class MyParty(GenericMetadata):
    
    def get_upload_path(self, filename):
        name, ext = os.path.splitext(filename)
        return os.path.join('uploads', 'logos' , str(self.generic_id), slugify(name)) + ext
    
    party_name = models.CharField(max_length=300, verbose_name="Name", help_text="BT-44")
    party_logo = models.ImageField(blank=True, null = True, upload_to=get_upload_path, verbose_name="Logo", help_text="Graphik mit Logo")
    party_contact_email = models.CharField(max_length=300, verbose_name="E-Mail-Adresse", help_text="BT-43")
    party_legal_entity_name = models.CharField(max_length=300, verbose_name="Rechtlicher Bezeichnung", help_text="BT-27")
    party_legal_entity_id = models.CharField(max_length=300, verbose_name="Rechtliche Identifikationsnummer", help_text="BT-32")
    party_tax_id = models.CharField(max_length=300, verbose_name="Umsatzsteuer ID", help_text="BT-X")
    party_postal_address = models.ForeignKey(PostalAddress, on_delete=models.CASCADE, verbose_name="Postalische Adresse", help_text="")
    party_contact_person_name = models.CharField(max_length=300, verbose_name="Kontaktperson", help_text="")
    party_contact_person_phone = models.CharField(max_length=300, verbose_name="Kontaktperson Telefon", help_text="")
    party_contact_person_email = models.CharField(max_length=300, verbose_name="Kontaktperson E-Mail", help_text="")
    party_payment_financial_account_id = models.CharField(max_length=300, verbose_name="IBAN", help_text="BT-44")
    party_payment_financial_account_name = models.CharField(max_length=300, verbose_name="Name des Kontoinhabers", help_text="")
    party_payment_financial_institution_id = models.CharField(max_length=300, verbose_name="BIC", help_text="")

    def __str__(self):
        """Returns a string representation of my party."""
        return f"'{self.party_name}' \n '{self.party_contact_email}'"
    
    # https://forum.djangoproject.com/t/django-filefield-resize-image-before-save-to-s3botostorage/7595/2
    # https://dev.to/doridoro/in-django-model-save-an-image-with-pillow-pil-library-5hbo
    # https://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil
    def save(self, *args, **kwargs):
        if self.party_logo:
            try:
                img = PIL.Image.open(self.party_logo)
                img.verify()
                # reopen because img.verify() moves pointer to the end of the file
                img = PIL.Image.open(self.party_logo)

                # convert png to RGB
                if img.mode in ("RGBA", "LA", "P"):
                    background = PIL.Image.new('RGBA', img.size, (255, 255, 255))
                    alpha_composite = PIL.Image.alpha_composite(background, img)
                    img = alpha_composite.convert("RGB")

                # Calculate new dimensions to maintain aspect ratio with a width of 800
                new_width = 800
                original_width, original_height = img.size
                new_height = int((new_width / original_width) * original_height)

                # Resize the image
                img = img.resize((new_width, new_height), PIL.Image.LANCZOS)

                # Prepare the image for saving
                temp_img = BytesIO()
                # Save the image as JPEG
                img.save(temp_img, format="JPEG", quality=70, optimize=True)
                temp_img.seek(0)

                # Change file extension to .jpg
                original_name, _ = self.party_logo.name.lower().split(".")
                print(original_name)
                img = f"{original_name}.jpg"

                # Save the BytesIO object to the ImageField with the new filename
                self.party_logo.save(img, ContentFile(temp_img.read()), save=False)

            except (IOError, SyntaxError) as e:
                raise ValueError(f"The uploaded file is not a valid image. -- {e}")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("myparty-detail", kwargs={"pk": self.pk})

    
class Invoice(GenericMetadata):
    identifier = models.CharField(max_length=300, verbose_name="Rechnungsnummer", help_text="Eindeutige Rechnugsnummer des Verkäufers (BT-1). Beispiel: '34-321321'")
    issue_date = models.DateField(verbose_name="Rechnungsdatum", help_text="Ausstellungsdatum der Rechnung (BT-2). Beispiel: '2024-07-30'")
    due_date = models.DateField(verbose_name="Fälligkeitsdatum", help_text="Fälligkeitsdatum der Rechnung (BT-9). Beispiel: '2024-08-30'")
    actual_delivery_date = models.DateField(verbose_name="Lieferdatum", help_text="Tatsächliches Datum der Lieferung (BT-72). Beispiel: '2024-08-02'")
    buyer_reference = models.CharField(max_length=1024, verbose_name="Käuferreferenz", help_text="In Deutschland auch Leitweg-ID, wird vom oft Käufer vorgegeben (BT-10).")   
    order_reference = models.CharField(max_length=1024, verbose_name="Bestellreferenz", help_text="Vom Käufer vorgegeben (BT-13).")  
    project_reference_id = models.CharField(max_length=1024, verbose_name="Projekt-ID", help_text="Identifikationsbezeichnung des Projektes. (BT-11).")  
    payment_terms = models.CharField(max_length=4096, verbose_name="Zahlungsbedingungen", help_text="Freitext für Informationen zu den Zahlungbedingungen. (BT-20).")
    prepaid_amount = models.DecimalField(decimal_places=2, max_digits=16, verbose_name="Vorausleistung", help_text="Betrag, der schon im Voraus geleistet wurde. (BT-X).")
    customer_party = models.ForeignKey(CustomerParty, on_delete=models.CASCADE, verbose_name="Kunde", help_text="Informationen zum Kunden (BG-7).")
    my_party = models.ForeignKey(MyParty, on_delete=models.CASCADE, verbose_name="Firma", help_text="Informationen zum Verkäufer (BG-4).")
    #farbe = models.CharField(max_length=2)

    def __str__(self):
        """Returns a string representation of an invoice."""
        return f"{ self.id }  -  { self.identifier }"
    
    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})

class InvoiceXml(GenericMetadata):

    # https://gist.github.com/chhantyal/5370749
    def get_upload_path(self, filename):
        name, ext = os.path.splitext(filename)
        return os.path.join('invoice', 'xml' , str(self.generic_id), slugify(name)) + ext
    
    name = models.CharField(max_length=1024, verbose_name="Name", help_text="")
    description = models.CharField(max_length=4096, verbose_name="Beschreibung", help_text="")
    attachment = models.FileField(null = True, blank = True, upload_to=get_upload_path, verbose_name="Dokument", help_text="")
    
    def filename_from_attachment(self):
        return self.attachment.file.name.split('/')[-1]
    
    def get_base64_attachment(self):
        return base64.b64encode(self.attachment.file.read()).decode('utf-8')

    def get_mime_type(self):
        """
        Get MIME by reading the header of the file
        """
        initial_pos = self.attachment.file.tell()
        self.attachment.file.seek(0)
        mime_type = magic.from_buffer(self.attachment.file.read(2048), mime=True)
        self.attachment.file.seek(initial_pos)
        return mime_type

    def __str__(self):
        """Returns a string representation of an invoice."""
        return f"{ self.attachment }"

class InvoiceAttachment(GenericMetadata):

    # https://gist.github.com/chhantyal/5370749
    def get_upload_path(self, filename):
        name, ext = os.path.splitext(filename)
        return os.path.join('attachments', 'invoice' , str(self.generic_id), slugify(name)) + ext
    
    identifier = models.CharField(max_length=1024, verbose_name="Name", help_text="")
    description = models.CharField(max_length=4096, verbose_name="Beschreibung", help_text="")
    attachment = models.FileField(null = True, blank = True, upload_to=get_upload_path, verbose_name="Dokument", help_text="https://docs.peppol.eu/poacc/billing/3.0/codelist/MimeCode/")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Rechnung", help_text="")

    def filename_from_attachment(self):
        return self.attachment.file.name.split('/')[-1]
    
    def get_base64_attachment(self):
        return base64.b64encode(self.attachment.file.read()).decode('utf-8')

    def get_mime_type(self):
        """
        Get MIME by reading the header of the file
        """
        initial_pos = self.attachment.file.tell()
        self.attachment.file.seek(0)
        mime_type = magic.from_buffer(self.attachment.file.read(2048), mime=True)
        self.attachment.file.seek(initial_pos)
        return mime_type

    def __str__(self):
        """Returns a string representation of an invoice."""
        return f"{ self.attachment }"
    

class InvoiceLine(GenericMetadata):

    # https://docs.peppol.eu/poacc/billing/3.0/codelist/UNECERec20/
    class UnitChoices(models.TextChoices):
        H87 = "H87", "Stück"
        C62 = "C62", "ein"
        MTK = "MTK", "Quadratmeter"
        LM = "LM", "Laufende Meter"
       
    # id - serial may be enough
    identifier = models.CharField(max_length=300, verbose_name="Identifikator", help_text="Beispiel: '1.1.1'")
    # name
    item_name = models.CharField(max_length=300, verbose_name="Name", help_text="")
    # description
    item_description = models.CharField(max_length=300, verbose_name="Beschreibung", help_text="")
    # price amount
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=16, verbose_name="Einzelpreis", help_text="")
    # unit code
    unit = models.CharField(max_length=5, choices=UnitChoices.choices, verbose_name="Einheit", help_text="")
    

    #unit2 = models.CharField(max_length=5, choices=UnitChoices.choices, verbose_name="Einheit", help_text="")

    # invoiced quantity
    number_of_units = models.DecimalField(decimal_places=2, max_digits=16, verbose_name="Menge", help_text="")
    # tax percent
    tax = models.DecimalField(decimal_places=2, max_digits=16, verbose_name="Steuersatz in %", help_text="Beispiel: '19.00'")
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Rechnung", help_text="")

    @property
    def total_cost(self):
        return self.number_of_units * self.price_per_unit


    def __str__(self):
        """Returns a string representation of an invoice."""
        return f"{ self.id } { self.item_name }"
    
    def get_absolute_url(self):
        return reverse("invoiceline-detail", kwargs={"pk": self.pk})