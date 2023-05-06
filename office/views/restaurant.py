from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from web.models import Restaurant, RestaurantImage


class RestaurantListView(PermissionRequiredMixin, ListView):
    model = Restaurant
    paginate_by = 10
    template_name = "office/restaurant/list.html"
    ordering = ["-created_at"]
    permission_required = "web.manage_restaurant"
    login_url = reverse_lazy("login")  # 권한이 없다면 login 페이지로 이동


class RestaurantCreateView(PermissionRequiredMixin, CreateView):
    model = Restaurant
    fields = ("name", "category", "address", "phone", "menu_info", "description")
    template_name = "office/restaurant/create.html"
    success_url = reverse_lazy("office-restaurant-list")
    permission_required = "web.manage_restaurant"
    login_url = reverse_lazy("login")  # 권한이 없다면 login 페이지로 이동

    def form_valid(self, form):
        data = form.save(commit=False)
        data.save()

        image_data = self.request.FILES.get("main_image")
        if image_data:
            image = RestaurantImage(restaurant=data, image=image_data)
            image.save()
            data.main_image = image
            data.save()

        return super().form_valid(form)


class RestaurantUpdateView(PermissionRequiredMixin, UpdateView):
    model = Restaurant
    pk_url_kwarg = "restaurant_id"
    fields = (
        "name",
        "category",
        "address",
        "phone",
        "menu_info",
        "description",
    )
    template_name = "office/restaurant/update.html"
    success_url = reverse_lazy("office-restaurant-list")
    permission_required = "web.manage_restaurant"
    login_url = reverse_lazy("login")  # 권한이 없다면 login 페이지로 이동

    def get_context_data(self, **kwargs):
        """기존 이미지를 포함한 원본 데이터"""
        context = super().get_context_data(**kwargs)
        context["object"] = self.object  # Restaurant의 pk로 들어온 값이 들어감

        return context

    def form_valid(self, form):
        data = form.save(commit=False)  # db에 저장없이 객체만 생성
        data.save()

        image_data = self.request.FILES.get("main_image")
        if image_data:
            image = RestaurantImage(restaurant=data, image=image_data)
            image.save()
            data.main_image = image
            data.save()

        return super().form_valid(form)


class RestaurantDeleteView(PermissionRequiredMixin, DeleteView):
    model = Restaurant
    pk_url_kwarg = "restaurant_id"
    template_name = "office/restaurant/delete.html"
    success_url = reverse_lazy("office-restaurant-list")
    permission_required = "web.manage_restaurant"
    login_url = reverse_lazy("login")  # 권한이 없다면 login 페이지로 이동
