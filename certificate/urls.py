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
    url(r'^drupal_feedback/$', 'drupal_feedback', name='drupal_feedback'),
    url(r'^scipy_download/$', 'scipy_download', name='scipy_download'),
    url(r'^drupal_download/$', 'drupal_download', name='drupal_download'),
)
