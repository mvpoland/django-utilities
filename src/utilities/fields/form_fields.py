from django import forms
from django.utils.translation import ugettext_lazy as _

from utilities.valuta import validate_iban

import re

class IBANField(forms.CharField):
    def clean(self, value):
        m = re.findall('[A-Z-a-z0-9]+', value)

        data = ''.join(m)

        valid, data = validate_iban(data)

        if not valid:
            raise forms.ValidationError(_('This is not a valid IBAN number'))

        return value.strip()

class VATField(forms.CharField):
    def clean(self, value):
        valid = len(value) == 12

        if valid:
            m = re.match('BE0[0-9]+', value)

            valid = m is not None

        if not valid:
            raise forms.ValidationError(_('This is not a valid Belgian VAT number'))

        return value
    
class EnterpriseNumberField(forms.CharField):
    def clean(self, value):
        value = super(EnterpriseNumberField, self).clean(value)
        if value != '':
            valid = len(value) == 10

            if valid:
                m = re.match('0[0-9]+', value)

                valid = m is not None

            if not valid:
                raise forms.ValidationError(_('This is not a valid Belgian enterprise number'))

        return value
