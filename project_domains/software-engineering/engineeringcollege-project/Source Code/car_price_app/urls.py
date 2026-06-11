from django.urls import path

from .views import (
    apriori_execution,
    execution_overview,
    execution_step,
    maruti_prices,
    registration,
    research_paper,
)

urlpatterns = [
    path('', registration, name='registration'),
    path('execution/', execution_overview, name='execution-overview'),
    path('execution/<slug:step_slug>/', execution_step, name='execution-step'),
    path('apriori/', apriori_execution, name='apriori-execution'),
    path('maruti-prices/', maruti_prices, name='maruti-prices'),
    path('research-paper/', research_paper, name='research-paper'),
]
