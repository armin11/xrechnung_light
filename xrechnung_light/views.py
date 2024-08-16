import re, decimal,json, os, base64, copy, PIL, csv
from xrechnung_light.xml_parser.ubl import Ubl
from reportlab.pdfgen import canvas
from django.urls import reverse_lazy
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.http import FileResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import *
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
#from xrechnung_light.forms import PostalAddressForm, CustomerPartyForm
from xrechnung_light.models import PostalAddress, CustomerParty, Invoice, InvoiceLine, InvoiceAttachment, MyParty, InvoiceXml
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
#from django.shortcuts import HttpResponse
from bootstrap_datepicker_plus.widgets import DatePickerInput
from xrechnung_light.forms import RegistrationForm, UploadForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from reportlab.platypus import BaseDocTemplate
from io import BytesIO

# Create your views here.
def home(request):
    return render(request, "xrechnung_light/home.html")
    
def about(request):
    return render(request, "xrechnung_light/about.html")

def contact(request):
    return render(request, "xrechnung_light/contact.html")

def decode_utf8(line_iterator):
    for line in line_iterator:
        yield line.decode('utf-8')

# https://stackoverflow.com/questions/70897970/django-how-to-upload-csv-file-using-form-to-populate-postgres-database-and-displ
@login_required
def invoicelines_csv_upload(request, invoiceid):
    print("form invoked")
    if request.method == 'GET':
        print("GET")
        form = UploadForm()
        return render(request, 'xrechnung_light/invoiceline_upload_csv.html', {'form': form})

    form = UploadForm(request.POST, request.FILES)

    # Validate the form
    if form.is_valid():
        try:
            invoice_object = Invoice.objects.get(owned_by_user=request.user, pk=invoiceid)
        except Invoice.DoesNotExist:
            invoice_object = None
            return HttpResponse("Invoice not found", status=404)
        # Get the correct type string instead of byte without reading full file into memory with a generator to decode line by line
        invoicelines_file = csv.reader(decode_utf8(request.FILES['sent_file']), delimiter='|')
        next(invoicelines_file)  # Skip header row

        for counter, line in enumerate(invoicelines_file):
            identifier = line[0]
            item_name = line[1]
            item_description = line[2]
            unit = line[3]
            price_per_unit = line[4]
            number_of_units = line[5]
            tax = line[6]

            invoiceline = InvoiceLine()
            invoiceline.identifier = identifier
            invoiceline.item_name = item_name
            invoiceline.item_description = item_description
            invoiceline.unit = unit
            invoiceline.price_per_unit = price_per_unit
            invoiceline.number_of_units = number_of_units
            invoiceline.tax = tax 
            invoiceline.invoice = invoice_object
            invoiceline.owned_by_user = request.user
            invoiceline.created = datetime.now()
            invoiceline.changed = datetime.now()

            invoiceline.save()

        messages.success(request, 'Saved successfully!')

        return redirect('invoiceline-list', invoiceid=invoice_object.pk)



@login_required
def get_invoice_attachment(request, pk):
    try:
        attachment = InvoiceAttachment.objects.get(owned_by_user=request.user, pk=pk)
    except InvoiceAttachment.DoesNotExist:
        attachment = None
    print(str(attachment))
    if attachment:
        if os.path.exists(attachment.attachment.file.name):
            response = FileResponse(attachment.attachment)
            return response
        else:
           return HttpResponse("File not found", status=404) 
    else:
        return HttpResponse("Object not found", status=404)

@login_required
def get_myparty_logo(request, pk):
    try:
        my_party = MyParty.objects.get(owned_by_user=request.user, pk=pk)
    except MyParty.DoesNotExist:
        my_party = None
    # print(str(logo))
    if my_party.party_logo:
        if os.path.exists(my_party.party_logo.file.name):
            response = FileResponse(my_party.party_logo)
            return response
        else:
           return HttpResponse("File not found", status=404) 
    else:
        return HttpResponse("Object not found", status=404)
    
@login_required
def get_invoicelines_csv(request, invoiceid):
    try:
        invoicelines = InvoiceLine.objects.filter(owned_by_user=request.user, invoice=invoiceid)
    except InvoiceLine.DoesNotExist:
        invoicelines = None
        return HttpResponse("No InvoiceLines found", status=404) 
    if invoicelines:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="somefilename.csv"'},
        )

        writer = csv.writer(response, delimiter='|')
        writer.writerow(["identifier", "item_name", "item_description", "unit", "price_per_unit", "number_of_units", "tax"])
        for invoiceline in invoicelines:
            writer.writerow([invoiceline.identifier.replace('\n',' '), invoiceline.item_name.replace('\n',' '), invoiceline.item_description.replace('\n',' '), invoiceline.unit.replace('\n',' '), invoiceline.price_per_unit, invoiceline.number_of_units, invoiceline.tax])

        return response
    else:
        return HttpResponse("No InvoiceLines found", status=404) 

@login_required
def get_invoice_pdf(request, pk):
    try:
        invoice = Invoice.objects.get(owned_by_user=request.user, pk=pk)
    except Invoice.DoesNotExist:
        invoice = None
    if invoice:
        pdf_buffer = BytesIO()
        # tests
        PdfInvoice(pdf_buffer, "Their address", ["Product", "Product"] * 50, invoice=invoice)
        pdf_buffer.seek(0)
        response = FileResponse(pdf_buffer, 
                        as_attachment=True, 
                        filename='invoice.pdf')
        #generate_pdf = GeneratePdf(invoice)
        #response = FileResponse(generate_pdf.generate_pdf_file(), 
        #                as_attachment=True, 
        #                filename='invoice.pdf')
        return response
    else:
        return HttpResponse("Object not found", status=404)


class PdfInvoice(BaseDocTemplate):
    # https://stackoverflow.com/questions/39266415/dynamic-framesize-in-python-reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import styles 
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, Paragraph, PageBreak, Table, \
        TableStyle


    def __init__(self, filename, their_adress, objects, invoice,  **kwargs):
        super().__init__(filename, page_size=self.A4, _pageBreakQuick=0, **kwargs)
        self.their_adress = their_adress
        self.objects = objects
        self.invoice = invoice
        # overwrite margins
        self.topMargin=45.0*self.mm
        self.leftMargin=25*self.mm
        self.rightMargin=20*self.mm
        self.bottomMargin=25*self.mm
        # https://stackoverflow.com/questions/637800/showing-page-count-with-reportlab
        self.final_pages = 1
        self.total_pages = 0
        self.pageinfo = "pageinfo"

        self.style = self.styles.getSampleStyleSheet()

        # Setting up the frames, frames are use for dynamic content not fixed page elements
        first_page_table_frame = self.Frame(self.leftMargin, self.bottomMargin + 10 * self.mm, 165 * self.mm, self.height - 10 * self.cm, id='small_table')
        later_pages_table_frame = self.Frame(self.leftMargin, self.bottomMargin + 10 * self.mm, 165 * self.mm, 217 * self.mm, id='large_table')

        # Creating the page templates
        first_page = self.PageTemplate(id='FirstPage', frames=[first_page_table_frame], onPage=self.on_first_page)
        later_pages = self.PageTemplate(id='LaterPages', frames=[later_pages_table_frame], onPage=self.add_default_info)
        self.addPageTemplates([first_page, later_pages])

        # Tell Reportlab to use the other template on the later pages,
        # by the default the first template that was added is used for the first page.
        story = [self.NextPageTemplate(['*', 'LaterPages'])]
        
        table_grid = [["Pos.", "Beschreibung", "Menge", "Einheit", "EP(€)", "GP(€)"]]
        # Add the objects
        invoicelines = InvoiceLine.objects.filter(invoice=invoice)
        sum_invoice = 0.0
        sum_tax = 0.0
        description_paragraph_style = copy.deepcopy(self.style['Normal'])
        description_paragraph_style.alignment = 0
        description_paragraph_style.fontSize = 8
        sum_b = 0.0
        for invoiceline in invoicelines:
            table_grid.append([invoiceline.identifier, self.Paragraph(invoiceline.item_description + " - " + invoiceline.item_name, description_paragraph_style), invoiceline.number_of_units,  invoiceline.get_unit_display(), invoiceline.price_per_unit, "{:.2f}".format(invoiceline.total_cost)])
            sum_invoice = sum_invoice + float(invoiceline.total_cost)
            sum_tax = sum_tax + (float(invoiceline.total_cost) * float(invoiceline.tax) / 100.0)
            sum_b = sum_invoice + sum_tax
            to_pay = sum_b - float(invoice.prepaid_amount)
        total_paragraph_style = copy.deepcopy(self.style['Normal'])
        total_paragraph_style.alignment = 2
        total_paragraph_style.fontSize = 8

        story.append(self.Table(table_grid, repeatRows=1, colWidths=[0.10 * 165 * self.mm,  0.40 * 165 * self.mm, 0.10 * 165 * self.mm, 0.15 * 165 * self.mm, 0.10 * 165 * self.mm, 0.15 * 165 * self.mm],
                           style=self.TableStyle([('GRID',(0,1),(-1,-1), 0.25, self.colors.gray),
                                             ('BOX', (0,0), (-1,-1), 1.0, self.colors.black),
                                             #('BOX', (0,0), (1,0), 1.0, self.colors.black),
                                             #('BOX', (0,0), (1,0), 1.0, self.colors.black),


                                             ('ALIGN', (0,0), (-1,0), 'CENTER'), # first row

                                             
                                             ('ALIGN', (0,1), (0,-1), 'CENTER'), # first column from second row
                                             ('ALIGN', (1,1), (1,-1), 'LEFT'), # second column from second row
                                             ('ALIGN', (2,1), (2,-1), 'RIGHT'), 
                                             ('ALIGN', (3,1), (3,-1), 'CENTER'), 
                                             ('ALIGN', (4,1), (4,-1), 'RIGHT'), 
                                             ('ALIGN', (5,1), (5,-1), 'RIGHT'),
                                             #('LINEBELOW', (-1,-1), (-1,-1), 1, self.colors.black),
                                             #('ALIGN', (0,1), (-1,-1), 'RIGHT'), # first column, second row: all rows from second row
                                             ('FONTSIZE', (0,1), (-1,-1), 8),
                                             ])))
        
        table_sum = []
        table_sum.append(["", "", "",  "Summe:", "", "{:.2f}".format(sum_invoice) + " €"])
        table_sum.append(["", "", "",  "Steuer:", "", "+ " + "{:.2f}".format(sum_tax) + " €"])
        table_sum.append(["", "", "",  "Brutto:", "", "{:.2f}".format(sum_b) + " €"])
        table_sum.append(["", "", "",  "abgerechnet:", "", "- " + "{:.2f}".format(invoice.prepaid_amount) + " €"])
        table_sum.append(["", "", "",  "Rechnungsbetrag:" , "", self.Paragraph("<b>" + "{:.2f}".format(to_pay) + " €</b>", total_paragraph_style)])
        story.append(self.Table(table_sum, repeatRows=0, colWidths=[0.10 * 165 * self.mm,  0.40 * 165 * self.mm, 0.10 * 165 * self.mm, 0.15 * 165 * self.mm, 0.10 * 165 * self.mm, 0.15 * 165 * self.mm],
                           style=self.TableStyle([
                                             ('ALIGN', (0,0), (0,-1), 'CENTER'), # first column from second row
                                             ('ALIGN', (1,0), (1,-1), 'LEFT'), # second column from second row
                                             ('ALIGN', (2,0), (2,-1), 'RIGHT'), 
                                             ('ALIGN', (3,0), (3,-1), 'LEFT'), 
                                             ('ALIGN', (4,0), (4,-1), 'RIGHT'), 
                                             ('ALIGN', (5,0), (5,-1), 'RIGHT'),
                                             ('FONTSIZE', (0,0), (-1,-1), 8),
                                             ])))
        # append sums
        sum_paragraph_style = copy.deepcopy(self.style['Normal'])
        sum_paragraph_style.fontSize = 10
        sum_paragraph = self.Paragraph("<b>Zahlungsfrist:</b> " + str(invoice.due_date) + "<br/><b>Zahlungsbedingungen:</b> " + invoice.payment_terms, sum_paragraph_style)
        sum_paragraph.hAlign = 'RIGHT'
        story.append(sum_paragraph)
        
        
        self.build(copy.deepcopy(story))
        self.final_pages = self.total_pages
        self.build(copy.deepcopy(story))

    def on_first_page(self, canvas, doc):
        canvas.saveState()
        # Add the logo and other default stuff
        self.add_default_info(canvas, doc)
        #logo_frame = self.Frame(127*self.mm, 252*self.mm, 63*self.mm, 35*self.mm, showBoundary=1)
        if self.invoice.my_party.party_logo: 
            canvas.drawImage(self.invoice.my_party.party_logo.path, 127*self.mm, 252*self.mm, width=63*self.mm, height=35*self.mm)
            #print("Path of logo image: " + str(self.invoice.my_party.party_logo.path))

        #logo_frame.drawBoundary(canvas)
        # 5 lines small 8pt
        # 6 lines big / normal
        address_frame = self.Frame(25*self.mm, 207*self.mm, 85*self.mm, 45*self.mm, showBoundary=0)
        address_content = "<font size=8>" + self.invoice.my_party.party_name + " | "
        address_content = address_content + self.invoice.my_party.party_postal_address.street_name + " | "
        address_content = address_content + "" + self.invoice.my_party.party_postal_address.postal_zone + " "
        address_content = address_content + self.invoice.my_party.party_postal_address.city_name + "<br/>"
        address_content = address_content + "Wenn unzustellbar, bitte mit neuer Anschrift zurück<br/>"
        address_content = address_content + "<br/></font>"
        address_content = address_content + self.invoice.customer_party.party_name + "<br/>" 
        address_content = address_content + self.invoice.customer_party.party_postal_address.street_name + "<br/>"
        address_content = address_content + "<b>" + self.invoice.customer_party.party_postal_address.postal_zone + "</b> " + self.invoice.customer_party.party_postal_address.city_name
        address_paragraph_style = self.style['Normal']
        address_flowable = self.Paragraph(address_content, address_paragraph_style)
        address_story = []
        address_story.append(address_flowable)
        address_frame.addFromList(address_story, canvas)

        content_info_frame = self.Frame(125*self.mm, 192*self.mm, 75*self.mm, 55*self.mm, showBoundary=0)   
        content_info_content = "<font size=10><b>" + self.invoice.my_party.party_name + "</b><br/>"
        content_info_content = content_info_content + "<b>Rechnungsnummer:</b> " + self.invoice.identifier + "<br/>" 
        content_info_content = content_info_content + "<b>Rechnungsdatum:</b> " + str(self.invoice.issue_date) + "<br/><br/>"
        content_info_content = content_info_content + "<b>Ansprechpartner:</b> " + self.invoice.my_party.party_contact_person_name + "<br/>" 
        content_info_content = content_info_content + "<b>E-Mail:</b> " + self.invoice.my_party.party_contact_person_email + "<br/>" 
        content_info_content = content_info_content + "<b>Telefon:</b> " + self.invoice.my_party.party_contact_person_phone + "<br/><br/>"
        content_info_content = content_info_content + "<b>Projekt-ID:</b> " + self.invoice.project_reference_id + "<br/>" 
        content_info_content = content_info_content + "<b>Leitweg-ID:</b> " + self.invoice.buyer_reference + "<br/>" 
        content_info_content = content_info_content + "<b>Bestellreferenz:</b> " + self.invoice.order_reference + "<br/></font>" 

        content_info_paragraph_style = self.style['Normal']
        content_info_flowable = self.Paragraph(content_info_content, content_info_paragraph_style)
        content_info_story = []
        content_info_story.append(content_info_flowable)
        content_info_frame.addFromList(content_info_story, canvas)

        table_header_frame = self.Frame(self.leftMargin, self.height - 47 * self.mm, self.width - (self.leftMargin + self.rightMargin), 10*self.mm, showBoundary=0)  
        table_header_paragraph_style = self.style['Normal']
        table_header_flowable = self.Paragraph("<font size=14><b>Rechnung</b></font>", table_header_paragraph_style)
        table_header_story = []
        table_header_story.append(table_header_flowable)
        table_header_frame.addFromList(table_header_story, canvas)

        canvas.restoreState()

    def afterPage(self):
        self.total_pages += 1  # Increment page count after each page is built
        super().afterPage()  # Call the superclass method

    def add_default_info(self, canvas, doc):
        canvas.saveState()

        page_number_content = f'Seite {doc.page} von {self.final_pages}'
        # draw pagenumbers as textobject
        # https://www.blog.pythonlibrary.org/2018/02/06/reportlab-101-the-textobject/
        # Create textobject
        textobject = canvas.beginText()
        # Set text location (x, y)
        textobject.setTextOrigin(170*self.mm, 33*self.mm)
        # Set font face and size
        textobject.setFont('Helvetica', 9)
        textobject.textLine(text=page_number_content)
        # Write text to the canvas
        canvas.drawText(textobject)
        canvas.line(25*self.mm, 30*self.mm, 195*self.mm, 30*self.mm)

        footer_frame = self.Frame(25*self.mm, 12*self.mm, 165*self.mm, 17*self.mm, showBoundary=0)
        footer_content = "<font size=8><b>" + self.invoice.my_party.party_name + "</b> | "
        footer_content = footer_content + self.invoice.my_party.party_postal_address.city_name + " | "
        footer_content = footer_content + "<b>E-Mail:</b> " + self.invoice.my_party.party_contact_email + " | "
        footer_content = footer_content + "<b>BIC:</b> " + self.invoice.my_party.party_payment_financial_institution_id + " | "
        footer_content = footer_content + "<b>IBAN:</b> " + self.invoice.my_party.party_payment_financial_account_id + " | "
        footer_content = footer_content + "<b>Kontoinhaber:</b> " + self.invoice.my_party.party_payment_financial_account_name + "</font>"
        footer_paragraph_style = self.style['Normal']
        footer_flowable = self.Paragraph(footer_content, footer_paragraph_style)
        footer_story = []
        footer_story.append(footer_flowable)
        footer_frame.addFromList(footer_story, canvas)

        canvas.restoreState()


# My default view classes
class MyCreateView(LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.created = datetime.now()
        form.instance.changed = datetime.now()
        form.instance.owned_by_user = self.request.user
        return super().form_valid(form)


class MyListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created')


class MyUpdateView(LoginRequiredMixin, UpdateView):
     
     def form_valid(self, form):
        if form.instance.owned_by_user == self.request.user:
            form.instance.changed = datetime.now()
            return super().form_valid(form)
        else:
            return HttpResponse("Object not owned by logged in user!", status=401)


class MyDeleteView(LoginRequiredMixin, DeleteView):

    def form_valid(self, form):
        object = self.get_object()
        if object.owned_by_user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Object not owned by logged in user!", status=401)


class MyDetailView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created')
    

class PostalAddressCreateView(MyCreateView):
    #template_name = "xrechnung_light/postaladdress_form.html"
    model = PostalAddress
    fields = ["street_name", "postal_zone", "city_name", "country_subentity",]
    success_url = reverse_lazy("postaladdress-list")   
    def form_valid(self, form):
        form.instance.country = 'DE'
        return super().form_valid(form)


class PostalAddressDetailView(DetailView):
    model = PostalAddress
    context_object_name = "postaladdress"
    def get_object(self):
        obj = super().get_object()
        # Record the last accessed date
        #obj.last_accessed = timezone.now()
        #obj.save()
        return obj
    #fields = ["party_name"]


class PostalAddressUpdateView(MyUpdateView):
    model = PostalAddress
    fields = ["street_name", "postal_zone", "city_name", "country_subentity",]
    success_url = reverse_lazy("postaladdress-list") 


class PostalAddressDeleteView(MyDeleteView):
    model = PostalAddress
    success_url = reverse_lazy("postaladdress-list")


class PostalAddressListView(MyListView):
    """Renders the postal addresses, with a list of all postal addresses"""
    model = PostalAddress


class CustomerPartyCreateView(MyCreateView):
    #template_name = "xrechnung_light/customerparty_form.html"
    model = CustomerParty
    fields = ["party_name", "party_contact_email", "party_postal_address", "party_legal_entity_name", "party_legal_entity_id"]
    success_url = reverse_lazy("customerparty-list")   

    # reduce choices for postal addresses to own postal addresses    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['party_postal_address'].queryset = form.fields['party_postal_address'].queryset.filter(owned_by_user=self.request.user.id)
        return form


class CustomerPartyUpdateView(MyUpdateView):
    model = CustomerParty
    fields = ["party_name", "party_contact_email", "party_postal_address", "party_legal_entity_name", "party_legal_entity_id" ]
    success_url = reverse_lazy("customerparty-list") 

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['party_postal_address'].queryset = form.fields['party_postal_address'].queryset.filter(owned_by_user=self.request.user.id)
        return form 


class CustomerPartyDeleteView(MyDeleteView):
    model = CustomerParty
    success_url = reverse_lazy("customerparty-list")


class CustomerPartyListView(MyListView):
    """Renders the customer parties, with a list of all customer parties"""
    model = CustomerParty

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created').prefetch_related('party_postal_address')


class CustomerPartyDetailView(DetailView):
    model = CustomerParty
    context_object_name = "customerparty"

    def get_object(self):
        obj = super().get_object()
        # Record the last accessed date
        #obj.last_accessed = timezone.now()
        #obj.save()
        return obj


class InvoiceCreateView(MyCreateView):
    model = Invoice
    fields = ["identifier", "issue_date", "due_date", "actual_delivery_date", "buyer_reference", "order_reference", "project_reference_id", "payment_terms",  "customer_party", "my_party", "prepaid_amount"]
    success_url = reverse_lazy("invoice-list")   

    # reduce choices for postal addresses to own postal addresses    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['customer_party'].queryset = form.fields['customer_party'].queryset.filter(owned_by_user=self.request.user.id)
        form.fields['my_party'].queryset = form.fields['my_party'].queryset.filter(owned_by_user=self.request.user.id)
        #https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/Walkthrough.html
        form.fields['issue_date'].widget = DatePickerInput()
        form.fields['due_date'].widget = DatePickerInput()
        form.fields['actual_delivery_date'].widget = DatePickerInput()
        return form


class InvoiceListView(MyListView):
    """Renders the customer parties, with a list of all customer parties"""
    model = Invoice

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created').prefetch_related('customer_party', 'my_party')#.prefetch_related('invoiceline')
        
    
    # add the invoicelines to the view context!
    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data()
    #    # calculate sums
    #    tax_exclusive_amount = 0.0
    #   for  in context['invoice_list']:
    #    print(str(context['invoice_list']))
    #    for test in context['invoice_list']:
    #        print(str(test.invoiceline))
    #    #context['invoicelines'] = self.invoiceline
    #    return context

 
class InvoiceUpdateView(MyUpdateView):
    model = Invoice
    fields = ["identifier", "issue_date", "due_date", "actual_delivery_date", "buyer_reference", "order_reference", "project_reference_id", "payment_terms",  "customer_party", "my_party", "prepaid_amount"]
    success_url = reverse_lazy("invoice-list") 

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['customer_party'].queryset = form.fields['customer_party'].queryset.filter(owned_by_user=self.request.user.id)
        form.fields['my_party'].queryset = form.fields['my_party'].queryset.filter(owned_by_user=self.request.user.id)
        form.fields['issue_date'].widget = DatePickerInput()
        form.fields['due_date'].widget = DatePickerInput()
        form.fields['actual_delivery_date'].widget = DatePickerInput()
        return form 


class InvoiceDeleteView(MyDeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")


class InvoiceDetailXmlView(MyDetailView):
    model = Invoice
    success_url = reverse_lazy("invoice-detail-xml")


class InvoiceLineCreateView(MyCreateView):
    model = InvoiceLine
    fields = ["identifier", "item_name", "item_description", "price_per_unit", "unit", "number_of_units", "tax", "invoice"]
    
    def form_valid(self, form):
        # validate user is owner of invoice
        if form.instance.invoice.owned_by_user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Parent object not owned by logged in user!", status=401)
    # reduce choices for postal addresses to own postal addresses    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['invoice'].queryset = form.fields['invoice'].queryset.filter(owned_by_user=self.request.user.id)
        #https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/Walkthrough.html
        #form.fields['issue_date'].widget = DatePickerInput()
        #form.fields['due_date'].widget = DatePickerInput()
        #form.fields['actual_delivery_date'].widget = DatePickerInput()
        return form
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        invoiceid = self.kwargs['invoiceid']
        
        form['initial'].update({'invoice': Invoice.objects.get(pk=invoiceid)})
        form['initial'].update({'owned_by_user': self.request.user})
        return form
        #return super().get_form_kwargs()

    def get_success_url(self):
        return reverse_lazy("invoiceline-list", kwargs={'invoiceid': self.kwargs['invoiceid']})    



class InvoiceLineListView(MyListView):
    """Renders the InvoiceLines"""
    model = InvoiceLine
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['invoiceid'] = self.kwargs['invoiceid']
        context['invoice'] = Invoice.objects.get(pk=self.kwargs['invoiceid'])
        # calculate sums - one foreach given tax value
        tax_exclusive_amount = float('0.0')
        tax_amount = float('0.0')
        tax_list = []
        """
        [{ "tax_percentage": 0.0,
            "amount_for_tax" : 0.0,
            "tax_amount": 0.0
        },
        { "tax_percentage": 0.0,
            "amount_for_tax" : 0.0,
            "tax_amount": 0.0
        },
        ]
        """
        for invoiceline in context['invoiceline_list']:
            # test if tax_value already exists in tax_list
            tax_value_index = False
            index = 0
            
            for tax_list_entry in tax_list:
                print(str(float(tax_list_entry.get('tax_percentage'))) + ' - ' + str(float(invoiceline.tax)))
                if float(tax_list_entry.get('tax_percentage')) == float(invoiceline.tax):
                    tax_value_index = index
                    break
                index = index + 1
            # get key for this tax value
            # 
            tax_amount_for_invoiceline = ( float(invoiceline.price_per_unit) * float(invoiceline.number_of_units) ) * float(invoiceline.tax) / float('100.0')
            amount_for_invoiceline = ( float(invoiceline.price_per_unit) * float(invoiceline.number_of_units) )
            if tax_value_index != False or str(tax_value_index) == '0':
                #tax_list[tax_value_index]['amount_for_tax'] = f"{round(float(tax_list[tax_value_index]['amount_for_tax']) + amount_for_invoiceline, 2):.2f}"
                #tax_list[tax_value_index]['tax_amount'] = f"{round(float(tax_list[tax_value_index]['tax_amount']) + tax_amount_for_invoiceline, 2):.2f}"
                tax_list[tax_value_index]['amount_for_tax'] = float(tax_list[tax_value_index]['amount_for_tax']) + amount_for_invoiceline
                tax_list[tax_value_index]['tax_amount'] = float(tax_list[tax_value_index]['tax_amount']) + tax_amount_for_invoiceline
            
            else:
                new_dict = {
                    "tax_percentage": round(invoiceline.tax, 2),
                    "amount_for_tax": round(amount_for_invoiceline, 2),
                    "tax_amount": round(tax_amount_for_invoiceline, 2),
                }
                # print("tax list append" + ' for ' + str(invoiceline.tax))
                tax_list.append(new_dict)
            # print(str(tax_list))

            tax_exclusive_amount = tax_exclusive_amount + amount_for_invoiceline
            tax_amount = tax_amount + tax_amount_for_invoiceline
        context['tax_list'] = tax_list
        context['tax_exclusive_amount'] = f"{round(tax_exclusive_amount, 2):.2f}"
        context['tax_amount'] = f"{round(tax_amount, 2):.2f}"
        context['tax_inclusive_amount'] = f"{round(tax_amount + tax_exclusive_amount, 2):.2f}"
        context['payable_amount'] = f"{round(tax_amount + tax_exclusive_amount - float(context['invoice'].prepaid_amount), 2):.2f}"
        return context
    
    def get_queryset(self):
        # reduce queryset to those invoicelines which came from the invoice
        invoiceid = self.kwargs['invoiceid']
        if invoiceid:
            return self.model.objects.filter(
            invoice=Invoice.objects.get(pk=invoiceid)
        ).order_by('identifier','created')
        else:
            return self.model.objects.order_by('-created')
        
class InvoiceLineListXmlView(InvoiceLineListView):  

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        response['Content-type'] = "application/xml"  # set header
        return response

class InvoiceLineListCsvView(InvoiceLineListView):  

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        response['Content-type'] = "text/csv"  # set header
        return response


class InvoiceLineUpdateView(MyUpdateView):
    model = InvoiceLine
    fields = ["identifier", "item_name", "item_description", "price_per_unit", "unit", "number_of_units", "tax", "invoice"] 

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['invoice'].queryset = form.fields['invoice'].queryset.filter(owned_by_user=self.request.user.id)
        return form 
    
    def get_success_url(self):
        return reverse_lazy("invoiceline-list", kwargs={'invoiceid': self.kwargs['invoiceid']})


class InvoiceLineDeleteView(MyDeleteView):
    model = InvoiceLine

    def get_success_url(self):
        return reverse_lazy("invoiceline-list", kwargs={'invoiceid': self.kwargs['invoiceid']})

class InvoiceAttachmentCreateView(MyCreateView):
    model = InvoiceAttachment
    fields = ["identifier", "description", "attachment", "invoice"]
    
    def form_valid(self, form):
        # validate user is owner of invoice
        if form.instance.invoice.owned_by_user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Parent object not owned by logged in user!", status=401)
    # reduce choices for invoice to own invoices    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['invoice'].queryset = form.fields['invoice'].queryset.filter(owned_by_user=self.request.user.id)
        #https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/Walkthrough.html
        #form.fields['issue_date'].widget = DatePickerInput()
        #form.fields['due_date'].widget = DatePickerInput()
        #form.fields['actual_delivery_date'].widget = DatePickerInput()
        return form
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        invoiceid = self.kwargs['invoiceid']
        
        form['initial'].update({'invoice': Invoice.objects.get(pk=invoiceid)})
        form['initial'].update({'owned_by_user': self.request.user})
        return form
        #return super().get_form_kwargs()

    def get_success_url(self):
        return reverse_lazy("invoiceattachment-list", kwargs={'invoiceid': self.kwargs['invoiceid']})   
    

class InvoiceAttachmentListView(MyListView):
    """Renders the InvoiceLines"""
    model = InvoiceAttachment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['invoiceid'] = self.kwargs['invoiceid']
        context['invoice'] = Invoice.objects.get(pk=self.kwargs['invoiceid'])
        return context
    
    def get_queryset(self):
        # reduce queryset to those invoicelines which came from the invoice
        invoiceid = self.kwargs['invoiceid']
        if invoiceid:
            return self.model.objects.filter(
            invoice=Invoice.objects.get(pk=invoiceid)
        ).order_by('-created')
        else:
            return self.model.objects.order_by('-created')
        

class InvoiceAttachmentUpdateView(MyUpdateView):
    model = InvoiceAttachment
    fields = ["identifier", "description", "attachment", "invoice"] 

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['invoice'].queryset = form.fields['invoice'].queryset.filter(owned_by_user=self.request.user.id)
        return form 
    
    def get_success_url(self):
        return reverse_lazy("invoiceattachment-list", kwargs={'invoiceid': self.kwargs['invoiceid']})


class InvoiceAttachmentDeleteView(MyDeleteView):
    model = InvoiceAttachment

    def get_success_url(self):
        return reverse_lazy("invoiceattachment-list", kwargs={'invoiceid': self.kwargs['invoiceid']})
    
"""
class InvoiceAttachmentDownloadView(MyDetailView):
    model = InvoiceAttachment
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(pk=self.pk)
        return queryset
    
    def get_form(self): 
        return HttpResponse("Test", status=200)
    
    #def get_success_url(self):
    #    return reverse_lazy("invoiceattachment-list", kwargs={'invoiceid': self.kwargs['invoiceid']})
"""
    
    
class InvoiceXmlCreateView(MyCreateView):
    model = InvoiceXml
    fields = ["name", "description", "attachment"]
    
    # reduce choices for invoice to own invoices    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        form['initial'].update({'owned_by_user': self.request.user})
        return form
    
    def form_valid(self, form):
        files = form.cleaned_data["attachment"]
        ubl_invoice = Ubl.read_from_xml(Ubl, files.read().decode('UTF-8'))
        if ubl_invoice != False:
            #create customer party
            #try to load existing entry
            customer_party_postal_address = PostalAddress.objects.filter(street_name=ubl_invoice.invoice.customer_party.party_postal_address.street_name, 
                                                          city_name=ubl_invoice.invoice.customer_party.party_postal_address.city_name, 
                                                          postal_zone=ubl_invoice.invoice.customer_party.party_postal_address.postal_zone, 
                                                          country='DE',  
                                                          owned_by_user=self.request.user,
                                                          )
            if customer_party_postal_address:
                print('record for c_p_address already exists - will not be added twice')
                p_a_primary_key = customer_party_postal_address[0].pk
            else:
                customer_party_postal_address = PostalAddress(street_name=ubl_invoice.invoice.customer_party.party_postal_address.street_name, 
                                                          city_name=ubl_invoice.invoice.customer_party.party_postal_address.city_name, 
                                                          postal_zone=ubl_invoice.invoice.customer_party.party_postal_address.postal_zone, 
                                                          country='DE', 
                                                          created=datetime.now(), 
                                                          owned_by_user=self.request.user,
                                                          )
                customer_party_postal_address.save()
                p_a_primary_key = customer_party_postal_address.pk

            customer_party = CustomerParty.objects.filter(party_name=ubl_invoice.invoice.customer_party.party_name,
                                           party_contact_email=ubl_invoice.invoice.customer_party.party_contact_email, 
                                           party_legal_entity_name=ubl_invoice.invoice.customer_party.party_legal_entity_name, 
                                           party_legal_entity_id=ubl_invoice.invoice.customer_party.party_legal_entity_id, 
                                           party_postal_address=PostalAddress.objects.get(pk=p_a_primary_key),
                                           owned_by_user=self.request.user,
                                           )
            if customer_party:
                print('record for customer party  already exists - will not be added twice')
                c_p_primary_key = customer_party[0].pk
            else:
                customer_party = CustomerParty(party_name=ubl_invoice.invoice.customer_party.party_name,
                                           party_contact_email=ubl_invoice.invoice.customer_party.party_contact_email, 
                                           party_legal_entity_name=ubl_invoice.invoice.customer_party.party_legal_entity_name, 
                                           party_legal_entity_id=ubl_invoice.invoice.customer_party.party_legal_entity_id, 
                                           party_postal_address=PostalAddress.objects.get(pk=p_a_primary_key),
                                           created=datetime.now(),
                                           owned_by_user=self.request.user,
                                           )
                customer_party.save()
                c_p_primary_key = customer_party.pk

            #create supplier party
            my_party_postal_address = PostalAddress.objects.filter(street_name=ubl_invoice.invoice.my_party.party_postal_address.street_name, 
                                                          city_name=ubl_invoice.invoice.my_party.party_postal_address.city_name, 
                                                          postal_zone=ubl_invoice.invoice.my_party.party_postal_address.postal_zone, 
                                                          country='DE',  
                                                          owned_by_user=self.request.user,
                                                          )
            if my_party_postal_address:
                print('record for m_p_address already exists - will not be added twice')
                primary_key = my_party_postal_address[0].pk
            else:
                my_party_postal_address = PostalAddress(street_name=ubl_invoice.invoice.my_party.party_postal_address.street_name, 
                                                          city_name=ubl_invoice.invoice.my_party.party_postal_address.city_name, 
                                                          postal_zone=ubl_invoice.invoice.my_party.party_postal_address.postal_zone, 
                                                          country='DE', 
                                                          created=datetime.now(), 
                                                          owned_by_user=self.request.user,
                                                        )
                my_party_postal_address.save()
                p_a_primary_key = my_party_postal_address.pk

            my_party = MyParty.objects.filter(party_name=ubl_invoice.invoice.my_party.party_name,
                                           party_contact_email=ubl_invoice.invoice.my_party.party_contact_email, 
                                           party_legal_entity_name=ubl_invoice.invoice.my_party.party_legal_entity_name, 
                                           party_legal_entity_id=ubl_invoice.invoice.my_party.party_legal_entity_id, 
                                           party_postal_address=PostalAddress.objects.get(pk=p_a_primary_key),
                                           owned_by_user=self.request.user,
                                           party_tax_id=ubl_invoice.invoice.my_party.party_tax_id,
                                           party_contact_person_name=ubl_invoice.invoice.my_party.party_contact_person_name,
                                           party_contact_person_phone=ubl_invoice.invoice.my_party.party_contact_person_phone,
                                           party_contact_person_email=ubl_invoice.invoice.my_party.party_contact_person_email,
                                           party_payment_financial_account_id=ubl_invoice.invoice.my_party.party_payment_financial_account_id,
                                           party_payment_financial_account_name=ubl_invoice.invoice.my_party.party_payment_financial_account_name,
                                           party_payment_financial_institution_id=ubl_invoice.invoice.my_party.party_payment_financial_institution_id,
                                    )
            if my_party:
                print('record for my party  already exists - will not be added twice')
                m_p_primary_key = my_party[0].pk
            else:
                my_party = MyParty(party_name=ubl_invoice.invoice.my_party.party_name,
                                    party_contact_email=ubl_invoice.invoice.my_party.party_contact_email, 
                                    party_legal_entity_name=ubl_invoice.invoice.my_party.party_legal_entity_name, 
                                    party_legal_entity_id=ubl_invoice.invoice.my_party.party_legal_entity_id, 
                                    party_postal_address=PostalAddress.objects.get(pk=p_a_primary_key),
                                    created=datetime.now(),
                                    owned_by_user=self.request.user,
                                    party_tax_id=ubl_invoice.invoice.my_party.party_tax_id,
                                    party_contact_person_name=ubl_invoice.invoice.my_party.party_contact_person_name,
                                    party_contact_person_phone=ubl_invoice.invoice.my_party.party_contact_person_phone,
                                    party_contact_person_email=ubl_invoice.invoice.my_party.party_contact_person_email,
                                    party_payment_financial_account_id=ubl_invoice.invoice.my_party.party_payment_financial_account_id,
                                    party_payment_financial_account_name=ubl_invoice.invoice.my_party.party_payment_financial_account_name,
                                    party_payment_financial_institution_id=ubl_invoice.invoice.my_party.party_payment_financial_institution_id,
                                    )
                my_party.save()
                m_p_primary_key = my_party.pk
            #create invoice
            invoice = Invoice(identifier=ubl_invoice.invoice.identifier,
                                issue_date=ubl_invoice.invoice.issue_date,
                                due_date=ubl_invoice.invoice.due_date,
                                created=datetime.now(),
                                owned_by_user=self.request.user,
                                actual_delivery_date=ubl_invoice.invoice.actual_delivery_date,
                                order_reference=ubl_invoice.invoice.order_reference,
                                buyer_reference=ubl_invoice.invoice.buyer_reference,
                                project_reference_id=ubl_invoice.invoice.project_reference_id,
                                payment_terms=ubl_invoice.invoice.payment_terms,
                                prepaid_amount=ubl_invoice.invoice.prepaid_amount,
                                customer_party=CustomerParty.objects.get(pk=c_p_primary_key),
                                my_party=MyParty.objects.get(pk=m_p_primary_key),
            )
            invoice.save()
            i_primary_key = invoice.pk
            #create invoice_lines
            for ubl_invoice_line in ubl_invoice.invoice.invoice_lines:
                invoice_line = InvoiceLine(
                    identifier=ubl_invoice_line.identifier,
                    item_name=ubl_invoice_line.item_name,
                    item_description=ubl_invoice_line.item_description,
                    price_per_unit=ubl_invoice_line.price_per_unit,
                    unit=ubl_invoice_line.unit_code,
                    number_of_units=float(ubl_invoice_line.number_of_units),
                    tax=ubl_invoice_line.tax,
                    invoice=Invoice.objects.get(pk=i_primary_key),
                    created=datetime.now(),
                    owned_by_user=self.request.user,
                )
                invoice_line.save()
            #create invoice_attachments
            for ubl_invoice_attachment in ubl_invoice.invoice.invoice_attachments:
                invoice_attachment = InvoiceAttachment(
                    identifier=ubl_invoice_attachment.identifier,
                    description=ubl_invoice_attachment.description,
                    #attachment=ubl_invoice_attachment.attachment,
                    invoice=Invoice.objects.get(pk=i_primary_key),
                    #mime_code=ubl_invoice_attachment.mime_code,
                    #filename=ubl_invoice_attachment.filename,
                    created=datetime.now(),
                    owned_by_user=self.request.user,
                )
                invoice_attachment.save()
                file_path = 'attachments/invoice/' + str(invoice_attachment.generic_id) + '/' + ubl_invoice_attachment.filename
                #store file to folder
                path = 'attachments/invoice/' + str(invoice_attachment.generic_id)
                os.makedirs(path, exist_ok=True)
                with open(file_path, "wb") as file:
                    binary_data =  base64.b64decode(ubl_invoice_attachment.attachment.encode('utf-8'))
                    file.write(binary_data)
                    file.close()
                #update record with filename in attachment row
                invoice_attachment.attachment.name=file_path
                invoice_attachment.save()

            return super().form_valid(form)
        else:
            return HttpResponse("XRechnung XML could not be parsed!", status=507)
    
    def get_success_url(self):
        return reverse_lazy("invoicexml-list")   
    

class InvoiceXmlListView(MyListView):
    """Renders the InvoiceLines"""
    model = InvoiceXml


class InvoiceXmlUpdateView(MyUpdateView):
    model = InvoiceXml
    fields = ["name", "description", "attachment"] 
      
    def get_success_url(self):
        return reverse_lazy("invoicexml-list")


class InvoiceXmlDeleteView(MyDeleteView):
    model = InvoiceXml

    def get_success_url(self):
        return reverse_lazy("invoicexml-list")







# https://dev.to/balt1794/registration-page-using-usercreationform-django-part-1-21j7
def register(request):
    if request.method != 'POST':
        form = RegistrationForm()
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            #
            user = form.save()
            login(request, user)
            #
            return redirect('home')
        else:
            print('form is invalid')
    context = {'form': form}

    return render(request, 'registration/register.html', context)


class MyPartyCreateView(MyCreateView):
    #template_name = "xrechnung_light/myparty_form.html"
    model = MyParty
    fields = ["party_name", "party_logo", "party_contact_email", "party_postal_address", "party_legal_entity_id","party_legal_entity_name", "party_tax_id", "party_contact_person_name", "party_contact_person_phone",
               "party_contact_person_email", "party_payment_financial_account_id", "party_payment_financial_account_name", "party_payment_financial_institution_id"]
    success_url = reverse_lazy("myparty-list")   

    # reduce choices for postal addresses to own postal addresses    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['party_postal_address'].queryset = form.fields['party_postal_address'].queryset.filter(owned_by_user=self.request.user.id)
        return form


class MyPartyUpdateView(MyUpdateView):
    model = MyParty
    fields = ["party_name", "party_logo", "party_contact_email", "party_postal_address", "party_legal_entity_id","party_legal_entity_name", "party_tax_id", "party_contact_person_name", "party_contact_person_phone",
               "party_contact_person_email", "party_payment_financial_account_id", "party_payment_financial_account_name", "party_payment_financial_institution_id"]
    success_url = reverse_lazy("myparty-list") 

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['party_postal_address'].queryset = form.fields['party_postal_address'].queryset.filter(owned_by_user=self.request.user.id)
        return form 


class MyPartyDeleteView(MyDeleteView):
    model = MyParty
    success_url = reverse_lazy("myparty-list")


class MyPartyListView(MyListView):
    model = MyParty

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created').prefetch_related('party_postal_address')


class MyPartyDetailView(DetailView):
    model = MyParty
    context_object_name = "myparty"


