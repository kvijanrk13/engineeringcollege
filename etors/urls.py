from django.urls import path

from . import views

app_name = "etors"

urlpatterns = [
    path("", views.home, name="home"),
    path("documentation/", views.documentation, name="documentation"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("logout/", views.logout_view, name="logout"),
    path("book/<int:train_id>/<str:journey_date>/", views.book, name="book"),
    path("payment/", views.payment, name="payment"),
    path("pnr/", views.pnr_search, name="pnr_search"),
    path("pnr/<str:pnr>/", views.pnr_detail, name="pnr_detail"),
    path("pnr/<str:pnr>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("cab/dispatch/<uuid:dispatch_token>/", views.cab_dispatch, name="cab_dispatch"),
    path("cab/payment/<str:reference>/", views.cab_payment, name="cab_payment"),
    path("cab/dispatch/<uuid:dispatch_token>/call/", views.cab_call_start, name="cab_call_start"),
    path("cab/dispatch/<uuid:dispatch_token>/call/<str:call_reference>/", views.cab_call_session, name="cab_call_session"),
]
