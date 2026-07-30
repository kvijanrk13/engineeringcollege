from django.contrib import admin

from .models import Booking, Passenger, Station, Train


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city")
    search_fields = ("code", "name", "city")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "name",
        "source",
        "destination",
        "departure_time",
        "active",
    )
    list_filter = ("active", "source", "destination")
    search_fields = ("number", "name")


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "pnr",
        "train",
        "journey_date",
        "contact_name",
        "status",
        "total_fare",
    )
    list_filter = ("status", "travel_class", "journey_date")
    search_fields = ("pnr", "contact_name", "contact_email", "contact_phone")
    inlines = (PassengerInline,)
