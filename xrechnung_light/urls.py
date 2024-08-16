from django.urls import include, path
from xrechnung_light import views
from django.contrib.auth import views as auth_views

from xrechnung_light.models import LogMessage, CustomerParty
from xrechnung_light.views import PostalAddressCreateView, PostalAddressDetailView, PostalAddressUpdateView, PostalAddressListView, PostalAddressDeleteView
from xrechnung_light.views import CustomerPartyCreateView, CustomerPartyUpdateView, CustomerPartyListView, CustomerPartyDeleteView
from xrechnung_light.views import MyPartyCreateView, MyPartyUpdateView, MyPartyListView, MyPartyDeleteView
from xrechnung_light.views import InvoiceCreateView, InvoiceListView,InvoiceUpdateView, InvoiceDeleteView
from xrechnung_light.views import InvoiceLineCreateView, InvoiceLineListView, InvoiceLineUpdateView
from xrechnung_light.views import InvoiceLineDeleteView, InvoiceLineListXmlView, InvoiceLineListCsvView
from xrechnung_light.views import InvoiceAttachmentListView, InvoiceAttachmentCreateView, InvoiceAttachmentUpdateView, InvoiceAttachmentDeleteView
from xrechnung_light.views import InvoiceXmlListView, InvoiceXmlCreateView, InvoiceXmlUpdateView, InvoiceXmlDeleteView


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    #path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(next_page="home"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name='logout'),
    # https://dev.to/donesrom/how-to-set-up-django-built-in-registration-in-2023-41hg
    path("register/", views.register, name = "register"),

    path("invoiceattachment/<int:pk>/", views.get_invoice_attachment, name="invoiceattachment-download"),

    path("postaladdress/", PostalAddressListView.as_view(), name="postaladdress-list"),
    path("postaladdress/create/", PostalAddressCreateView.as_view(), name="postaladdress-create"),
    path("postaladdress/<int:pk>/", PostalAddressDetailView.as_view(), name="postaladdress-detail"),
    path("postaladdress/<int:pk>/update/", PostalAddressUpdateView.as_view(), name="postaladdress-update"),
    path("postaladdress/<int:pk>/delete/", PostalAddressDeleteView.as_view(), name="postaladdress-delete"),

    path("customerparty/", CustomerPartyListView.as_view(), name="customerparty-list"),
    path("customerparty/create/", CustomerPartyCreateView.as_view(), name="customerparty-create"),
    path("customerparty/<int:pk>/update/", CustomerPartyUpdateView.as_view(), name="customerparty-update"),
    path("customerparty/<int:pk>/delete/", CustomerPartyDeleteView.as_view(), name="customerparty-delete"),

    path("myparty/", MyPartyListView.as_view(), name="myparty-list"),
    path("myparty/create/", MyPartyCreateView.as_view(), name="myparty-create"),
    path("myparty/<int:pk>/update/", MyPartyUpdateView.as_view(), name="myparty-update"),
    path("myparty/<int:pk>/delete/", MyPartyDeleteView.as_view(), name="myparty-delete"),
    path("myparty/<int:pk>/logo/", views.get_myparty_logo, name="myparty-logo"),

    path("invoicexml/", InvoiceXmlListView.as_view(), name="invoicexml-list"),
    path("invoicexml/create/", InvoiceXmlCreateView.as_view(), name="invoicexml-create"),
    path("invoicexml/<int:pk>/update/", InvoiceXmlUpdateView.as_view(), name="invoicexml-update"),
    path("invoicexml/<int:pk>/delete/", InvoiceXmlDeleteView.as_view(), name="invoicexml-delete"),

    path("invoice/create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("invoice/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoice/<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("invoice/<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    

    path("invoice/<int:invoiceid>/invoiceline/create/", InvoiceLineCreateView.as_view(), name="invoiceline-create"),
    path("invoice/<int:invoiceid>/invoiceline/", InvoiceLineListView.as_view(), name="invoiceline-list"),

    path("invoice/<int:invoiceid>/invoiceline/<int:pk>/update/", InvoiceLineUpdateView.as_view(), name="invoiceline-update"),
    path("invoice/<int:invoiceid>/invoiceline/<int:pk>/delete/", InvoiceLineDeleteView.as_view(), name="invoiceline-delete"),
    
    path("invoice/<int:invoiceid>/invoiceline/xml/", InvoiceLineListXmlView.as_view(template_name="xrechnung_light/invoice_template_ubl.xml"), name="invoiceline-list-xml"),
    #path("invoice/<int:invoiceid>/invoiceline/csv/", InvoiceLineListCsvView.as_view(template_name="xrechnung_light/invoiceline_csv_template.csv"), name="invoiceline-list-csv"),
    path("invoice/<int:invoiceid>/invoiceline/csv/", views.get_invoicelines_csv, name="invoiceline-list-csv"),
    path("invoice/<int:invoiceid>/invoiceline/csv/upload/", views.invoicelines_csv_upload, name="invoicelines-csv-upload"),

    path("invoice/<int:pk>/pdf/", views.get_invoice_pdf, name="invoiceline-list-pdf"),

    path("invoice/<int:invoiceid>/invoiceattachment/create/", InvoiceAttachmentCreateView.as_view(), name="invoiceattachment-create"),
    path("invoice/<int:invoiceid>/invoiceattachment/", InvoiceAttachmentListView.as_view(), name="invoiceattachment-list"),

    path("invoice/<int:invoiceid>/invoiceattachment/<int:pk>/update/", InvoiceAttachmentUpdateView.as_view(), name="invoiceattachment-update"),
    path("invoice/<int:invoiceid>/invoiceattachment/<int:pk>/delete/", InvoiceAttachmentDeleteView.as_view(), name="invoiceattachment-delete"),

]



