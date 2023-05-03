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

        category = None

        query_sets = Restaurant.objects.filter(visible=True).order_by("-created_at")
        if keyword:
            query_sets = query_sets.filter(
                Q(name__istartswith=keyword) | Q(address__istartswith=keyword)
            )
        if category_id:
            category = get_object_or_404(Category, id=int(category_id))
            query_sets = query_sets.filter(category=category)

        restaurants = query_sets.all()
        paginator = Paginator(restaurants, 12)

        paging = paginator.get_page(page_number)

        return {
            "paging": paging,
            "selected_keyword": keyword,
            "selected_category": category,
        }
