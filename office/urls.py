from django.urls import path

from office.views.booking import BookingListView, BookingUpdateView, BookingCancelView
from office.views.main import OfficeIndexView
from office.views.restaurant import RestaurantListView, RestaurantCreateView, RestaurantUpdateView, RestaurantDeleteView

urlpatterns = [
    # main
    path("", OfficeIndexView.as_view(), name="office-index"),
    # restaurant
    path("restaurant/", RestaurantListView.as_view(), name="office-restaurant-list"),
    path(
        "restaurant/create/",
        RestaurantCreateView.as_view(),
        name="office-restaurant-create",
    ),
    path(
        "restaurant/<int:restaurant_id>/update/",
        RestaurantUpdateView.as_view(),
        name="office-restaurant-update",
    ),
    path(
        "restaurant/<int:restaurant_id>/delete/",
        RestaurantDeleteView.as_view(),
        name="office-restaurant-delete",
    ),
    # booking
    path("booking/", BookingListView.as_view(), name="office-booking-list"),
    path(
        "booking/<int:booking_id>/update/",
        BookingUpdateView.as_view(),
        name="office-booking-update",
    ),
    path(
        "booking/<int:booking_id>/cancel/",
        BookingCancelView.as_view(),
        name="office-booking-cancel",
    ),
]
