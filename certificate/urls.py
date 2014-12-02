from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fossee_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^download/', 'certificate.views.download', name='download'),
    url(r'^verify/', 'certificate.views.verify', name='verify'),
)
