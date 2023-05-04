import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from web.models import Recommendation, Restaurant, Category


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        recommendations = (
            Recommendation.objects.filter(visible=True)
            .order_by("sort")
            .select_related("restaurant")
            .all()[:4]
        )

        return {"recommendations": recommendations}


class SearchView(TemplateView):
    template_name = "main/search.html"

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get("page", "1")
        keyword = self.request.GET.get("keyword")  # 검색할 키워드 값
        category_id = self.request.GET.get("category")  # 어떤 카테고리에 속해있는지

        weekday = self.request.GET.get("weekday")
        start_time = self.request.GET.get("start")
        end_time = self.request.GET.get("end")

        category = None

        query_sets = Restaurant.objects.filter(visible=True).order_by("-created_at")
        if keyword:
            query_sets = query_sets.filter(
                Q(name__istartswith=keyword) | Q(address__istartswith=keyword)
            )
        if category_id:
            category = get_object_or_404(Category, id=int(category_id))
            query_sets = query_sets.filter(category=category)

        relation_conditions = None

        if weekday:
            # SELECT * FROM Restautrant r INNER JOIN RestaurantTable rt ON rt.restaurant_id = r.id
            # WHERE rt.weekday = :weekday
            relation_conditions = Q(restauranttable__weekday=weekday)

        if start_time:
            # iso포맷에 맞게 time형으로 변환
            start_time = datetime.time.fromisoformat(start_time)  # ex) 12:00:00
            if relation_conditions:
                relation_conditions = relation_conditions & Q(
                    restauranttable__time__gte=start_time
                )
            # relation_conditions가 None인 경우
            else:
                relation_conditions = Q(restauranttable__time__gte=start_time)

        if end_time:
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
        paginator = Paginator(restaurants, 12)

        paging = paginator.get_page(page_number)

        return {
            "paging": paging,
            "selected_keyword": keyword,
            "selected_category": category,
            "selected_weekday": weekday,
            "selected_start": datetime.time.isoformat(start_time) if start_time else "",
            "selected_end": datetime.time.isoformat(end_time) if end_time else "",
        }
