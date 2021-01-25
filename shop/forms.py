from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class PaymentForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    street_address = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}))
    street_address_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '80'}))
    country = CountryField(blank_label='Select country..').formfield(
        widget=CountrySelectWidget(attrs={
            "class": "wide w-100"
        })
    )
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    zip = forms.CharField()
