from django.views.generic import TemplateView

from web.models import Recommendation


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
