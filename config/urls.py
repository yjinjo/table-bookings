from django.contrib import admin
from django.urls import path, include

from web.views.main import IndexView, SearchView, SearchJsonView
from web.views.restaurant import RestaurantView, BookingView, PayView
from web.views.users import RegisterView, LoginView, LogoutView, VerificationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/", VerificationView.as_view(), name="verification"),
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
    path("oauth/", include("allauth.urls")),
]
