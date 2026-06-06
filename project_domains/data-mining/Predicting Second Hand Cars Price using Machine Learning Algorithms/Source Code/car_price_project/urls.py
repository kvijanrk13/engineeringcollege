from __future__ import annotations

from django.contrib import admin
from django.urls import path

from car_price_app.views import index


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="car-price-home"),
]
