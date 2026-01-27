from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # Must be before admin.site.urls
    path('admin/', admin.site.urls),
    path('', include('insurance_web.urls')),
]
