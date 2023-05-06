import requests
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, UpdateView

from office.views.permission import BookingPermissionRequiredMixin
from web.models import Booking, PayHistory


class BookingListView(BookingPermissionRequiredMixin, ListView):
    model = Booking
    paginate_by = 10
    template_name = "office/booking/list.html"
    ordering = ["-created_at"]
    permission_required = "web.manage_booking"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return self.get_bookings_has_perms()


class BookingUpdateView(BookingPermissionRequiredMixin, UpdateView):
    """결제 이후 이름, 연락처, comment 등을 수정할 수 있는 View"""

    model = Booking
    fields = ("booker_name", "booker_phone", "booker_comment")
    pk_url_kwarg = "booking_id"
    template_name = "office/booking/update.html"
    success_url = reverse_lazy("office-booking-list")
    permission_required = "web.manage_booking"
    # URL에서 정의한 path paramter를 쓰면 Minin에서 권한을 가진 것으로 필터링 됨
    check_permission_path_variable = "booking_id"
    login_url = reverse_lazy("login")


class BookingCancelView(BookingPermissionRequiredMixin, View):
    permission_required = "web.manage_booking"
    check_permission_path_variable = "booking_id"
    login_url = reverse_lazy("login")

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        if booking.status != Booking.PayStatus.PAID:
            messages.warning(request, "취소할 수 없는 예약입니다.")
            return redirect("office-booking-list")

        response = requests.post(
            "https://api.tosspayments.com/v1/payments/"
            + booking.pg_transaction_number
            + "/cancel",
            json={"cancelReason": "관리자 예약취소"},
            headers={
                "Authorization": "Basic dGVzdF9za196WExrS0V5cE5BcldtbzUwblgzbG1lYXhZRzVSOg==",
                "Content-Type": "application/json",
            },
        )

        if response.ok:
            with transaction.atomic():
                booking.status = Booking.PayStatus.CANCELED
                booking.canceled_at = timezone.now()
                booking.seat.remain += 1
                booking.save()
                booking.seat.save()
                PayHistory.objects.create(booking=booking, amount=-booking.price)

        return redirect("office-booking-list")
