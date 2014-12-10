from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fossee_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'certificate.views.index', name='index'),
    url(r'^download/$', 'certificate.views.download', name='download'),
    url(r'^verify/$', 'certificate.views.verify', name='verify'),
    url(r'^feedback/$', 'certificate.views.feedback', name='feedback'),
    url(r'^scipy_feedback/$', 'certificate.views.scipy_feedback', name='scipy_feedback'),
    url(r'^scipy_download/$', 'certificate.views.scipy_download', name='scipy_download'),
)
