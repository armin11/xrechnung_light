from django.contrib import admin
from xrechnung_light.models import Invoice, InvoiceLine, MyParty

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceLine)
admin.site.register(MyParty)