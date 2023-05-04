from datetime import timedelta, date

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from web.models import Restaurant, RestaurantTable, RestaurantImage
from web.utils import convert_weekday


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

            slots.append(
                {
                    "day": slot_day,
                    "times": times,
                }
            )

        return {
            "restaurant": restaurant,
            "images": images,
            "slots": slots,
        }
