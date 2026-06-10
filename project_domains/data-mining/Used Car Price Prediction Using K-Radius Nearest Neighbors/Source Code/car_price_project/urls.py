from __future__ import annotations

from django.contrib import admin
from django.urls import path

from car_price_app.views import apriori_execution, execution_overview, execution_step, registration


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", registration, name="registration"),
    path("execution/", execution_overview, name="execution-overview"),
    path("execution/<slug:step_slug>/", execution_step, name="execution-step"),
    path("apriori/", apriori_execution, name="apriori-execution"),
]
