from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("web.urls")),
    path("office/", include("office.urls")),
    path("admin/", admin.site.urls),
    path("oauth/", include("allauth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
