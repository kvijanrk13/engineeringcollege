from django.urls import path

from .views import apriori_execution, execution_overview, execution_step, registration

urlpatterns = [
    path('', registration, name='car_price_registration'),
    path('execution/', execution_overview, name='car_price_execution_overview'),
    path('execution/<slug:step_slug>/', execution_step, name='car_price_execution_step'),
    path('apriori/', apriori_execution, name='car_price_apriori_execution'),
]
