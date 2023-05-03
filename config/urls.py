from django.contrib import admin
from django.urls import path, include

from web.views.main import IndexView, SearchView
from web.views.users import RegisterView, LoginView, LogoutView, VerificationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/", VerificationView.as_view(), name="verification"),
    path("search/", SearchView.as_view(), name="search"),
    path("oauth/", include("allauth.urls")),
]
