import datetime
import random
from datetime import timedelta, date

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from web.models import (
    Restaurant,
    RestaurantTable,
    RestaurantImage,
    AvailableSeat,
    Booking,
)
from web.utils import convert_weekday


@transaction.atomic
def fetch_remain_and_return_expired_booking(slot_day: date, time: RestaurantTable):
    seat_datetime = timezone.datetime.combine(slot_day, time.time)
    seat, created = AvailableSeat.objects.get_or_create(
        restaurant=time.restaurant,
        table=time,
        datetime=seat_datetime,
        defaults={"remain": time.available},
    )

    if not created:
        created_time = datetime.datetime.now() - datetime.timedelta(minutes=10)
        expired_count = (
            Booking.objects.filter(seat=seat)
            .filter(status=Booking.PayStatus.READY)
            .filter(created_at__lt=created_time)
            .update(status=Booking.PayStatus.FAILED)
        )
        seat.remain = seat.remain + expired_count
        seat.save()

    return {
        "restaurant_id": time.restaurant.id,
        "seat_id": seat.id,
        "time": time.time,
        "price": time.price,
        "total": time.available,
        "remain": seat.remain,
    }


class RestaurantView(TemplateView):
    template_name = "restaurant/detail.html"

    # path parameter를 직접 받도록 restaurant_id로 설정
    def get_context_data(self, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        images = RestaurantImage.objects.filter(restaurant=restaurant).all()
        # 리스트로 바로 변환한 이유는 아래에서 pickling 하기 위함
        tables = list(RestaurantTable.objects.filter(restaurant=restaurant).all())

        # 예약은 내일 부터 ~ 10일치만 가능한 시스템으로 구현
        slots = []
        span_days = 10  # 10일치
        available_start_day = date.today() + timedelta(days=1)  # 내일부터 시작

        # 10일치의 데이터 생성
        for i in range(span_days):
            slot_day = available_start_day + timedelta(days=i)
            week_value = convert_weekday(slot_day.weekday())  # 월요일부터 시작
            times = [table for table in tables if table.weekday == week_value]

            seats = []
            for time in times:
                seat = fetch_remain_and_return_expired_booking(slot_day, time)
                seats.append(seat)

            slots.append(
                {
                    "day": slot_day,
                    "times": seats,
                }
            )

        return {
            "restaurant": restaurant,
            "images": images,
            "slots": slots,
        }


class BookingView(LoginRequiredMixin, TemplateView):
    template_name = "restaurant/book.html"
    login_url = reverse_lazy("login")

    def create_order_number(self, seat_id):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return now + str(seat_id) + str(random.randrange(1000, 10000))

    def get_context_data(self, restaurant_id, seat_id):
        # get: 좌석 사전 확보 + 폼 그리기
        # post: 주문 정보 업데이트

        with transaction.atomic():
            new_order_number = self.create_order_number(seat_id)
            seat = get_object_or_404(AvailableSeat, id=seat_id)
            if seat.remain <= 0:
                messages.warning(self.request, "잔여 좌석이 없습니다.")
                return redirect("restaurant-view", restaurant_id)

            booking, created = Booking.objects.get_or_create(
                user=self.request.user,
                restaurant=seat.restaurant,
                table=seat.table,
                seat=seat,
                status=Booking.PayStatus.READY,
                defaults={"price": seat.table.price, "order_number": new_order_number},
            )

            if created:
                seat.remain = seat.remain - 1
                seat.save()

            booking.save()

            return {"seat": seat, "booking": booking}

    def post(self, request, *args, **kwargs):
        order_number = self.request.POST.get("order_number", "")
        booker_name = self.request.POST.get("booker_name", None)
        booker_phone = self.request.POST.get("booker_phone", None)
        booker_comment = self.request.POST.get("booker_comment", None)

        booking = get_object_or_404(Booking, order_number=order_number)

        if booking.user != self.request.user:
            raise PermissionDenied()

        booking.booker_name = booker_name
        booking.booker_phone = booker_phone
        booking.booker_comment = booker_comment
        booking.save()

        return JsonResponse({}, safe=False)


class PayView(LoginRequiredMixin, TemplateView):
    """연동을 다 끝내고 나서 카드사 인증을 거친 뒤의 내 웹 사이트의 결제 인증 과정"""

    template_name = "restaurant/confirm.html"

    def get_context_data(self, status):
        pg_key = self.request.GET.get("paymentKey")
        order_number = self.request.GET.get("orderId")
        amount = self.request.GET.get("amount")

        booking = get_object_or_404(Booking, order_number=order_number)

        if booking.price != int(amount) or booking.status != Booking.PayStatus.READY:
            raise PermissionDenied()

        if status == "success":
            response = requests.post(
                "https://api.tosspayments.com/v1/payments/" + pg_key,
                json={
                    "amount": amount,
                    "orderId": order_number,
                },
                headers={
                    "Authorization": "Basic dGVzdF9za196WExrS0V5cE5BcldtbzUwblgzbG1lYXhZRzVSOg==",
                    "Content-Type": "application/json",
                },
            )

            with transaction.atomic():
                # 위의 결제 정보를 요청하고 응답받는 시간이 꽤 걸리므로 새로 가져옵니다.
                booking = get_object_or_404(Booking, order_number=order_number)
                booking.pg_transaction_number = pg_key

                if response.ok:  # status_code == 200
                    booking.status = Booking.PayStatus.PAID
                    booking.paid_at = timezone.now()
                else:  # 실패할 경우 기존 데이터를 그대로 저장합니다.
                    booking.status = Booking.PayStatus.FAILED
                booking.save()
        else:
            booking.status = Booking.PayStatus.FAILED
            booking.save()

        return {"booking": booking}
