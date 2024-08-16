import xml.etree.ElementTree as ET
import io 

class PostalAddress():
    street_name:str
    city_name:str
    postal_zone:str
    country:str
    

class InvoiceLine():
    identifier:str
    item_name:str
    item_description:str
    price_per_unit:str
    unit_code:str
    number_of_units:str
    tax:str


class InvoiceAttachment():
    identifier:str
    description:str
    attachment:str
    mime_code:str
    filename:str


class CustomerParty():
    party_name:str
    party_contact_email:str
    party_legal_entity_name:str
    party_legal_entity_id:str
    party_postal_address:PostalAddress


class MyParty():
    party_name:str
    party_contact_email:str
    party_legal_entity_name:str
    party_legal_entity_id:str
    party_tax_id:str

    party_postal_address:PostalAddress

    party_contact_person_name:str
    party_contact_person_phone:str
    party_contact_person_email:str
    party_payment_financial_account_id:str
    party_payment_financial_account_name:str
    party_payment_financial_institution_id:str


class Invoice():

    def __init__(self,):
        self.invoice_lines = []
        self.invoice_attachments = []
        
    identifier:str
    issue_date:str
    due_date:str
    actual_delivery_date:str
    buyer_reference:str
    order_reference:str
    project_reference_id:str
    payment_terms:str
    prepaid_amount:str

    customer_party:CustomerParty
    my_party:MyParty
    pass



class Ubl():
    invoice:Invoice
    
    def read_from_xml(self, xml): 
        root = ET.fromstring(xml)
        ns = {'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
             'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
             'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
        
        self.invoice = self.get_invoice(self, root, ns)
        
      

        #get invoice_attachment
        #get invoiceline
        return self
        
    def get_address(self, root:ET, ns:dict, party_type:str):
        party_element = root.find('cac:Accounting' + party_type + 'Party', ns)
        street_name = party_element.find(".//cbc:StreetName", ns).text
        city_name = party_element.find(".//cbc:CityName", ns).text
        postal_zone = party_element.find(".//cbc:PostalZone", ns).text
        country = party_element.find(".//cac:Country/cbc:IdentificationCode", ns).text
        postal_address = PostalAddress()
        postal_address.street_name = street_name
        postal_address.city_name = city_name
        postal_address.postal_zone = postal_zone
        postal_address.country = country
        return postal_address
    
    def get_customer_party(self, root, ns):
        party_element = root.find('cac:AccountingCustomerParty', ns)
        customer_party = CustomerParty()
        customer_party.party_name = party_element.find(".//cac:PartyName/cbc:Name", ns).text
        customer_party.party_contact_email = party_element.find(".//cbc:EndpointID[@schemeID='EM']", ns).text
        customer_party.party_legal_entity_name = party_element.find(".//cac:PartyLegalEntity/cbc:RegistrationName", ns).text
        customer_party.party_legal_entity_id = party_element.find(".//cac:PartyLegalEntity/cbc:CompanyID", ns).text
        customer_party.party_postal_address = self.get_address(self, root, ns, 'Customer')
        return customer_party

    def get_my_party(self, root, ns):
        party_element = root.find('cac:AccountingSupplierParty', ns)
        my_party = MyParty()
        my_party.party_name = party_element.find(".//cac:PartyName/cbc:Name", ns).text
        my_party.party_contact_email = party_element.find(".//cbc:EndpointID[@schemeID='EM']", ns).text
        my_party.party_legal_entity_name = party_element.find(".//cac:PartyLegalEntity/cbc:RegistrationName", ns).text
        my_party.party_legal_entity_id = party_element.find(".//cac:PartyLegalEntity/cbc:CompanyID", ns).text
        my_party.party_postal_address = self.get_address(self, root, ns, 'Supplier')
        my_party.party_tax_id = party_element.find(".//cac:PartyTaxScheme/cbc:CompanyID", ns).text
        my_party.party_contact_person_name = party_element.find(".//cac:Contact/cbc:Name", ns).text
        my_party.party_contact_person_phone = party_element.find(".//cac:Contact/cbc:Telephone", ns).text
        my_party.party_contact_person_email = party_element.find(".//cac:Contact/cbc:ElectronicMail", ns).text
        my_party.party_payment_financial_account_id = root.find('cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:ID', ns).text
        my_party.party_payment_financial_account_name = root.find('cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:Name', ns).text
        my_party.party_payment_financial_institution_id = root.find('cac:PaymentMeans/cac:PayeeFinancialAccount/cac:FinancialInstitutionBranch/cbc:ID', ns).text
        return my_party

    def get_invoice(self, root, ns):
        invoice = Invoice()
        invoice.identifier = root.find("cbc:ID", ns).text
        invoice.issue_date = root.find("cbc:IssueDate", ns).text
        invoice.due_date = root.find("cbc:DueDate", ns).text
        invoice.actual_delivery_date = root.find("cac:Delivery/cbc:ActualDeliveryDate", ns).text
        invoice.buyer_reference = root.find("cbc:BuyerReference", ns).text
        invoice.order_reference = root.find("cac:OrderReference/cbc:ID", ns).text
        invoice.project_reference_id = root.find("cac:ProjectReference/cbc:ID", ns).text
        invoice.payment_terms = root.find("cac:PaymentTerms/cbc:Note", ns).text
        invoice.prepaid_amount = root.find("cac:LegalMonetaryTotal/cbc:PrepaidAmount", ns).text 

        invoice.invoice_lines = self.get_invoice_lines(self, root, ns)
        
        invoice.invoice_attachments = self.get_invoice_attachments(self, root, ns)

        invoice.my_party = self.get_my_party(self, root, ns)
        invoice.customer_party = self.get_customer_party(self, root, ns)
        return invoice

    def get_invoice_lines(self, root, ns):
        invoice_lines = []
        invoice_line_elements = root.findall("cac:InvoiceLine", ns)
        for invoice_line_element in invoice_line_elements:
            invoice_line = InvoiceLine()
            invoice_line.identifier = invoice_line_element.find('cbc:ID', ns).text
            invoice_line.item_name = invoice_line_element.find('cac:Item/cbc:Name', ns).text
            invoice_line.item_description = invoice_line_element.find('cbc:Note', ns).text
            invoice_line.price_per_unit = invoice_line_element.find('cac:Price/cbc:PriceAmount', ns).text
            unit_code_element = invoice_line_element.find('cbc:InvoicedQuantity', ns)
            invoice_line.unit_code = unit_code_element.attrib['unitCode']
            invoice_line.number_of_units = invoice_line_element.find('cbc:InvoicedQuantity', ns).text
            invoice_line.tax = invoice_line_element.find('cac:Item/cac:ClassifiedTaxCategory/cbc:Percent', ns).text
            invoice_lines.append(invoice_line)
        return invoice_lines

    def get_invoice_attachments(self, root, ns):
        invoice_attachments = []
        attachment_elements = root.findall("cac:AdditionalDocumentReference", ns)
        for invoice_attachment_element in attachment_elements:
            invoice_attachment = InvoiceAttachment()
            invoice_attachment.identifier = invoice_attachment_element.find('cbc:ID', ns).text
            invoice_attachment.description = invoice_attachment_element.find('cbc:DocumentDescription', ns).text
            invoice_attachment.attachment = invoice_attachment_element.find('cac:Attachment/cbc:EmbeddedDocumentBinaryObject', ns).text
            mime_code_element = invoice_attachment_element.find('cac:Attachment/cbc:EmbeddedDocumentBinaryObject', ns)
            invoice_attachment.mime_code = mime_code_element.attrib['mimeCode']
            invoice_attachment.filename = mime_code_element.attrib['filename']
            invoice_attachments.append(invoice_attachment)
        return invoice_attachments


