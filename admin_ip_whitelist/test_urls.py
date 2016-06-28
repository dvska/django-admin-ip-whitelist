from django.conf.urls import url
from django.contrib import admin

from .test_views import TestView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', TestView.as_view(), name='test'),
]
