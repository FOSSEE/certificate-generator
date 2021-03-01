from django.urls import path
from certificate.views import *


urlpatterns = [
    path('', index, name='index'),
    path('download/', download, name='download'),
    path('verify/', verify, name='verify'),
    path('verify/<slug:serial_key>/', verify, name='verify-directly'),
    path('feedback/', feedback, name='feedback'),
    path('scipy_feedback/', scipy_feedback, name='scipy_feedback'),
    path('scipy_download/', scipy_download, name='scipy_download'),
    path('cep_certificate_download/', cep_certificate_download,
        name='cep_certificate_download'),
]

app_name = 'certificate'
