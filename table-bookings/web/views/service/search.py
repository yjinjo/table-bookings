import datetime

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from web.models import Restaurant


class RestaurantSearch:
    def create_cache_key(
        self, keyword, category_id, weekday, start_time, end_time, page_number
    ):
        """params의 조합으로 캐시키 생성"""
        return (
            f"{keyword}:{category_id}:{weekday}:{start_time}:{end_time}:{page_number}"
        )

    def search(self, keyword, category_id, weekday, start_time, end_time, page_number):
        cache_key = self.create_cache_key(
            keyword, category_id, weekday, start_time, end_time, page_number
        )
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        category = None

        query_sets = Restaurant.objects.filter(visible=True).order_by("-created_at")
        if keyword and len(keyword) > 0:
            query_sets = query_sets.filter(
                Q(name__istartswith=keyword) | Q(address__istartswith=keyword)
            )
        if category_id and len(category_id) > 0:
            category = get_object_or_404(Category, id=int(category_id))
            query_sets = query_sets.filter(category=category)

        relation_conditions = None

        if weekday and len(weekday) > 0:
            # SELECT * FROM Restautrant r INNER JOIN RestaurantTable rt ON rt.restaurant_id = r.id
            # WHERE rt.weekday = :weekday
            relation_conditions = Q(restauranttable__weekday=weekday)

        if start_time and len(start_time) > 0:
            # iso포맷에 맞게 time형으로 변환
            start_time = datetime.time.fromisoformat(start_time)  # ex) 12:00:00
            if relation_conditions:
                relation_conditions = relation_conditions & Q(
                    restauranttable__time__gte=start_time
                )
            # relation_conditions가 None인 경우
            else:
                relation_conditions = Q(restauranttable__time__gte=start_time)

        if end_time and len(end_time) > 0:
            # iso포맷에 맞게 time형으로 변환
            end_time = datetime.time.fromisoformat(end_time)  # ex) 12:00:00
            if relation_conditions:
                relation_conditions = relation_conditions & Q(
                    restauranttable__time__lte=end_time
                )
            # relation_conditions가 None인 경우
            else:
                relation_conditions = Q(restauranttable__time__lte=end_time)

        if relation_conditions:
            query_sets = query_sets.filter(relation_conditions)

        restaurants = query_sets.distinct().all()
        paginator = Paginator(restaurants, 8)

        paging = paginator.get_page(page_number)

        result = {
            "paging": paging,
            "selected_keyword": keyword,
            "selected_category": category,
            "selected_weekday": weekday,
            "selected_start": datetime.time.isoformat(start_time) if start_time else "",
            "selected_end": datetime.time.isoformat(end_time) if end_time else "",
        }

        cache.set(cache_key, result, 60)  # cache_key 라는 이름으로 result를 60초 저장

        return result
