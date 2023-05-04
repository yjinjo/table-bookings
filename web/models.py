from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(null=False, max_length=20)
    profile_image = models.ImageField(upload_to="uploads/%Y/%m/%d/", null=True)
    verified = models.BooleanField(default=False)


class UserVerification(models.Model):
    """새로운 계정을 생성할 때 고유한 문자열을 하나 생성하는 모델"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(null=False, max_length=200, unique=True)
    verified = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=False)
    verified_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=False)


class Restaurant(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    main_image = models.ForeignKey(
        "RestaurantImage",
        related_name="main_image",
        null=True,
        on_delete=models.CASCADE,
    )
    address = models.CharField(max_length=300, db_index=True)
    phone = models.CharField(max_length=20)
    # 만약 해당 식당이 이슈가 있거나 했을 때 사용자에게 보여질/안보여질 flag 설정
    visible = models.BooleanField(default=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True)
    menu_info = models.TextField(null=True)
    description = models.TextField(null=True)


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True, null=False)


class RestaurantTable(models.Model):
    """예약 가능한 테이블 자리수 등을 정의"""

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    class Weekday(models.TextChoices):
        MONDAY = "MON", _("월요일")
        TUESDAY = "TUE", _("화요일")
        WEDNESDAY = "WEB", _("수요일")
        THURSDAY = "THU", _("목요일")
        FRIDAY = "FRI", _("금요일")
        SATURDAY = "SAT", _("토요일")
        SUNDAY = "SUN", _("일요일")

    weekday = models.CharField(
        max_length=3, choices=Weekday.choices, default=Weekday.MONDAY
    )
    time = models.TimeField()
    available = models.IntegerField()
    # 달러의 경우 소수점 둘째자리까지 표시 (만약 한국 원화만 할 경우 decimal_places=0으로 해도 됨
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        unique_together = ["restaurant", "weekday", "time"]


class Recommendation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    # 1, 2, 3, ... 이런식으로 정렬하는데 아무것도 넣지 않는다면 9999 즉, 제일 뒤의 것을 의미할 것입니다.
    sort = models.IntegerField(default=9999)
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
