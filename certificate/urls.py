from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('certificate.views',
    # Examples:
    # url(r'^$', 'fossee_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'index', name='index'),
    url(r'^download/$', 'download', name='download'),
    url(r'^verify/$', 'verify', name='verify'),
    url(r'^verify/(?P<serial_key>.*)/$', 'verify', name='verify-directly'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^scipy_feedback/$', 'scipy_feedback', name='scipy_feedback'),
    url(r'^scipy_feedback_2015/$', 'scipy_feedback_2015', name='scipy_feedback_2015'),
    url(r'^scipy_feedback_2016/$', 'scipy_feedback_2016', name='scipy_feedback_2016'),
    url(r'^openmodelica_feedback_2017/$', 'openmodelica_feedback_2017', name='openmodelica_feedback_2017'),
    url(r'^openmodelica_download_2017/$', 'openmodelica_download_2017', name='openmodelica_download_2017'),
    url(r'^python_workshop_download/$', 'python_workshop_download', name='python_workshop_download'),
    url(r'^drupal_feedback/$', 'drupal_feedback', name='drupal_feedback'),
    url(r'^dwsim_feedback/$', 'dwsim_feedback', name='dwsim_feedback'),
    url(r'^arduino_feedback/$', 'arduino_feedback', name='arduino_feedback'),
    url(r'^arduino_google_feedback/$', 'arduino_google_feedback', name='arduino_google_feedback'),
    url(r'^scipy_download/$', 'scipy_download', name='scipy_download'),
    url(r'^drupal_download/$', 'drupal_download', name='drupal_download'),
    url(r'^tbc_freeeda_download/$', 'tbc_freeeda_download', name='tbc_freeeda_download'),
    url(r'^dwsim_download/$', 'dwsim_download', name='dwsim_download'),
    url(r'^arduino_download/$', 'arduino_download', name='arduino_download'),
    url(r'^esim_download/$', 'esim_download', name='esim_download'),
    url(r'^esim_google_feedback/$', 'esim_google_feedback', name='esim_google_feedback'),
    url(r'^osdag_workshop_download/$', 'osdag_workshop_download', name='osdag_workshop_download'),
    url(r'^osdag_workshop_feedback/$', 'osdag_workshop_feedback', name='osdag_workshop_feedback'),
    url(r'^esim_workshop_download/$', 'esim_workshop_download', name='esim_workshop_download'),
    url(r'^esim_workshop_feedback/$', 'esim_workshop_feedback', name='esim_workshop_feedback'),
    url(r'^scipy_download_2015/$', 'scipy_download_2015', name='scipy_download_2015'),
    url(r'^scipy_download_2016/$', 'scipy_download_2016', name='scipy_download_2016'),
    url(r'^openfoam_symposium_download_2016/$', 'openfoam_symposium_download_2016', name='openfoam_symposium_download_2016'),
    url(r'^openfoam_symposium_feedback_2016/$', 'openfoam_symposium_feedback_2016', name='openfoam_symposium_feedback_2016'),
    url(r'^fossee_internship_cerificate_download/$', 'fossee_internship_cerificate_download', name='fossee_internship_cerificate_download'),
    url(r'^fossee_internship16_cerificate_download/$', 'fossee_internship16_cerificate_download', name='fossee_internship16_cerificate_download'),
    url(r'^drupal_workshop_download/$', 'drupal_workshop_download', name='drupal_workshop_download'),
    url(r'^scipy_download_2017/$', 'scipy_download_2017', name='scipy_download_2017'),
    url(r'^scipy_feedback_2017/$', 'scipy_feedback_2017', name='scipy_feedback_2017'),
    url(r'^python_workshop_download/contact$', 'contact', name='contact'),
        
)
