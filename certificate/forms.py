from django import forms
from certificate.models import FeedBack

class FeedBackForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    #phone = forms.CharField(max_length=15, required=False)
    #organisation = forms.CharField(max_length=30)
    #department = forms.CharField\
    #            (max_length=64)
    #role = forms.CharField\
    #    (max_length=64)
    #address = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows':1}))
    #city = forms.CharField(max_length=30)
    #pincode_number = forms.CharField\
    #            (max_length=30, required=False)
    #state = forms.CharField\
    #            (max_length=128)
