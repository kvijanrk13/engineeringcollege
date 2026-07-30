from django.urls import path

from . import views

app_name = "etors"

urlpatterns = [
    path("", views.home, name="home"),
    path("book/<int:train_id>/<str:journey_date>/", views.book, name="book"),
    path("pnr/", views.pnr_search, name="pnr_search"),
    path("pnr/<str:pnr>/", views.pnr_detail, name="pnr_detail"),
    path("pnr/<str:pnr>/cancel/", views.cancel_booking, name="cancel_booking"),
]
