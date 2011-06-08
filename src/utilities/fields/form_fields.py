from django import forms

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