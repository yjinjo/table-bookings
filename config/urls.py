from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from web.views.history import BookingHistoryView, BookingCancelView
from web.views.main import IndexView, SearchView, SearchJsonView
from web.views.restaurant import RestaurantView, BookingView, PayView
from web.views.users import (
    RegisterView,
    LoginView,
    LogoutView,
    VerificationView,
    ProfileView,
    PasswordView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/", VerificationView.as_view(), name="verification"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password/", PasswordView.as_view(), name="password"),
    path("search/", SearchView.as_view(), name="search"),
    path("search/json/", SearchJsonView.as_view(), name="search-json"),
    path(
        "restaurant/<int:restaurant_id>/",
        RestaurantView.as_view(),
        name="restaurant-view",
    ),
    path(
        "restaurant/<int:restaurant_id>/booking/<int:seat_id>",
        BookingView.as_view(),
        name="booking",
    ),
    path("restaurant/confirm/<str:status>", PayView.as_view(), name="payment"),
    path("history", BookingHistoryView.as_view(), name="history"),
    path("cancel/<int:booking_id>", BookingCancelView.as_view(), name="cancel"),
    path("oauth/", include("allauth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
