from django import forms
#from xrechnung_light.models import LogMessage, PostalAddress, CustomerParty
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

"""
class LogMessageForm(forms.ModelForm):
    class Meta:
        model = LogMessage
        fields = ("message",)   # NOTE: the trailing comma is required

class PostalAddressForm(forms.ModelForm):
    class Meta:
        model = PostalAddress
        fields = ("street_name", "postal_zone", "city_name", "country", "country_subentity",)   # NOTE: the trailing comma is required   

    def form_valid(self, form):
        form.instance.owned_by_user = self.request.user
        return super().form_valid(form)
        
class CustomerPartyForm(forms.ModelForm):
    class Meta:
        model = CustomerParty
        fields = ("party_name", "party_contact_email", "party_postal_address", )   # NOTE: the trailing comma is required   
"""

class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UploadForm(forms.Form):

    csv_file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder':
        'Upload "invoicelines.csv"', 'help_text': 'Choose a .csv file with invoicelines to enter'}))
    