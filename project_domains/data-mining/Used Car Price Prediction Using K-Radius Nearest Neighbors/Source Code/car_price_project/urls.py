from __future__ import annotations

from django.contrib import admin
from django.urls import path

from car_price_app.views import apriori_execution, execution_overview, execution_step, gmail_sign_in, maruti_prices, registration, research_paper


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", registration, name="registration"),
    path("gmail/sign-in/", gmail_sign_in, name="gmail-sign-in"),
    path("execution/", execution_overview, name="execution-overview"),
    path("execution/<slug:step_slug>/", execution_step, name="execution-step"),
    path("apriori/", apriori_execution, name="apriori-execution"),
    path("maruti-prices/", maruti_prices, name="maruti-prices"),
    path("research-paper/", research_paper, name="research-paper"),
]
