from django import forms
from certificate.models import FeedBack
import datetime

class FeedBackForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()

email_subject_choice = [
('Certificate not Awarded','Certificate not Awarded'),
('Change in Name','Change in Name'),
('Issue with Workshop Date','Issue with Workshop Date'),
('Invalid Email Address','Invalid Email Address'),
('Others','Others')]
ws_type_choice = [
('iscp','Introduction to Scientific Computing using Python(ISCP)'),
('2day','Advanced Python'),
('3day','Basic Programming using Python'),
('sel','Self Learning(Basics of Python)')]

class ContactForm(forms.Form):
    name = forms.CharField(label= 'Full Name',max_length=30)
    email = forms.EmailField()
    date = forms.DateField(label="Workshop Date",initial=datetime.date.today)
    category = forms.CharField(widget=forms.Select(choices=ws_type_choice))
    subject = forms.CharField(widget=forms.Select(choices=email_subject_choice))
    message = forms.CharField(label='Message',widget=forms.Textarea)
    
