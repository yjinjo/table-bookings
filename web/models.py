import uuid

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(null=False, max_length=30)
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

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name=_("이름"))
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name=_("카테고리")
    )
    main_image = models.ForeignKey(
        "RestaurantImage",
        related_name="main_image",
        on_delete=models.CASCADE,
        verbose_name=_("메인 이미지"),
    )
    address = models.CharField(max_length=300, db_index=True, verbose_name=_("주소"))
    phone = models.CharField(max_length=20, verbose_name=_("연락처"))
    # 만약 해당 식당이 이슈가 있거나 했을 때 사용자에게 보여질/안보여질 flag 설정
    visible = models.BooleanField(default=True, verbose_name=_("표시 여부"))
    latitude = models.FloatField(null=True, default=None, verbose_name=_("위도"))
    longitude = models.FloatField(null=True, default=None, verbose_name=_("경도"))
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("생성일시")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("수정일시"))
    menu_info = models.TextField(null=True, verbose_name=_("메뉴 정보"))
    description = models.TextField(null=True, verbose_name=_("설명"))


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


class AvailableSeat(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    remain = models.IntegerField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        unique_together = ("restaurant", "table", "datetime")


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    seat = models.ForeignKey(AvailableSeat, on_delete=models.CASCADE)

    class PayMethod(models.TextChoices):
        CARD = "CARD", _("카드")

    class PayStatus(models.TextChoices):
        READY = "READY", _("결제대기")
        PAID = "PAID", _("결제완료")
        FAILED = "FAILED", _("예약실패")
        CANCELED = "CANCELED", _("예약취소")

    order_number = models.CharField(max_length=20)
    pg_transaction_number = models.CharField(max_length=50, null=True, default=None)
    method = models.CharField(
        max_length=4, choices=PayMethod.choices, default=PayMethod.CARD
    )
    status = models.CharField(
        max_length=10, choices=PayStatus.choices, default=PayStatus.READY
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    paid_at = models.DateTimeField(null=True, default=None)
    canceled_at = models.DateTimeField(null=True, default=None)

    booker_name = models.CharField(max_length=20, default=None, null=True)
    booker_phone = models.CharField(max_length=20, default=None, null=True)
    booker_comment = models.CharField(max_length=200, default=None, null=True)

    review = models.OneToOneField(
        "Review", on_delete=models.SET_NULL, null=True, default=None
    )


class PayHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=False)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000, verbose_name=_("코멘트"))
    ratings = models.PositiveIntegerField(
        verbose_name=_("평점"), validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)


# ---------------------------------
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email[:30]  # 필드 자체가 30 까지 밖에 못들어가므로
        if User.objects.filter(username=user.username).exists():
            # 만약 이메일이 이미 존재한다면 uuid4를 이용해서 고유한 usernmae으로 만들기
            user.username = str(uuid.uuid4())
        return user


@receiver(post_save, sender=User)
def on_save_user(sender, instance, **kwargs):
    profile = UserProfile.objects.filter(user=instance).first()
    social_account = SocialAccount.objects.filter(user=instance).first()

    # 일반 로그인이 아닌 소셜 계정으로 로그인되었을 시
    if profile is None and social_account is not None:
        nickname = instance.email.split("@")[0]
        UserProfile.objects.create(
            user=instance,
            nickname=nickname,
            profile_image=None,
        )
