from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("web.urls")),
    path("office/", include("office.urls")),
    path("admin/", admin.site.urls),
    path("oauth/", include("allauth.urls")),
    path("prometheus/", include("django_prometheus.urls")),
]
