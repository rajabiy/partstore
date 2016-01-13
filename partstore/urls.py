
from django.conf.urls import url, include
from django.contrib import admin



urlpatterns = [
    url(r'^crud/',  include('crudbuilder.urls')),
    url(r'^admin/', admin.site.urls),
]
