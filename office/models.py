from django.contrib.auth.models import User
from django.db import models

from web.models import Restaurant


class RestaurantPermission(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
