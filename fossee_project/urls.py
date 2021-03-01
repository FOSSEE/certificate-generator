from django.urls import  include, path 

from django.contrib import admin
admin.autodiscover()

urlpatterns =[ 

    path('admin/', admin.site.urls),
    path('certificates/', include('certificate.urls', namespace='certificate')),
]
