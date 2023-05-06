from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from office.models import RestaurantPermission
from web.models import Booking, Restaurant


class BookingPermissionRequiredMixin(PermissionRequiredMixin):
    check_permission_path_variable = None  # pk_url_kwargs 와 같은 path parameter 변수명

    def has_manager(self):
        # 해당 유저가 매니저 그룹에 속해있다면,
        if self.request.user.is_superuser:
            return True

        # 현재 로그인된 유저의 그룹들을 모두 가져와서,
        groups = self.request.user.groups.all()

        # 매니저를 가진 그룹이 하나라도 존재한다면,
        if any(group.name == "manager" for group in groups):
            return True

        return False

    def get_bookings_has_perms(self):
        """ListView를 구현할 때 현재 로그인된 사용자가 권한을 가진 레스토랑만 필터링"""
        if self.has_manager():
            return Booking.objects.all()

        # 매니저가 아니라 상점주인일 경우 현재 로그인된 유저의 값과 일치하는 레스토랑 permission을 지닌 레스토랑만 필터링,
        restaurants = Restaurant.objects.filter(
            restaurantpermission__user=self.request.user
        )

        return Booking.objects.filter(restaurant__in=restaurants)

    def has_permission(self):
        has_perms = super().has_permission()

        if self.check_permission_path_variable and not self.has_manager():
            booking_id = self.kwargs[self.check_permission_path_variable]
            booking = get_object_or_404(Booking, id=booking_id)

            try:
                # 먼저 permission이 있는지 체크
                RestaurantPermission.objects.get(
                    restaurant=booking.restaurant, user=self.request.user
                )
            except ObjectDoesNotExist:
                return False

        return has_perms
