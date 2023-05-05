from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from web.models import Review, Booking


class ReviewCreateView(CreateView):
    model = Review
    fields = ["comment", "ratings"]
    template_name = "review/create.html"
    success_url = reverse_lazy("history")

    def form_valid(self, form):
        booking_id = self.kwargs["booking_id"]
        booking = get_object_or_404(Booking, pk=booking_id)
        # 만약 이미 review를 남겼었다면 이제 남길 수 없으므로 PermissionDenied
        if booking.review:
            raise PermissionDenied()
        if booking.user != self.request.user:
            raise PermissionDenied()
        # 아직 시간이 안지났다면
        if booking.seat.datetime > timezone.now():
            raise PermissionDenied()

        data = form.save(commit=False)
        data.user = self.request.user
        data.restaurant = booking.restaurant
        data.save()
        booking.review = data
        booking.save()

        return super().form_valid(form)
