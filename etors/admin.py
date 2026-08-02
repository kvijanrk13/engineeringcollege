from django.contrib import admin

from .models import Booking, CabBooking, Passenger, Station, Train


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


class CabBookingInline(admin.StackedInline):
    model = CabBooking
    extra = 0
    max_num = 1


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
    inlines = (PassengerInline, CabBookingInline)


@admin.register(CabBooking)
class CabBookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "booking",
        "cab_type",
        "pickup_station",
        "cab_arrival_at",
        "vehicle_number",
        "status",
    )
    list_filter = ("status", "cab_type", "pickup_station")
    search_fields = ("reference", "booking__pnr", "driver_name", "vehicle_number")
