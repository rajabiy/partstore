
from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^', admin.site.urls),
]
