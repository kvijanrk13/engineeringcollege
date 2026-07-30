from datetime import date

from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingForm, PNRForm, SearchForm
from .models import Booking, Passenger, Train
from .services import fare_for, seat_number, train_availability


def home(request):
    search_form = SearchForm(request.GET or None)
    pnr_form = PNRForm()
    trains = None
    search = None

    if request.GET and search_form.is_valid():
        source = search_form.cleaned_data["source"]
        destination = search_form.cleaned_data["destination"]
        journey_date = search_form.cleaned_data["journey_date"]
        queryset = Train.objects.select_related("source", "destination").filter(
            source=source,
            destination=destination,
            active=True,
        )
        trains = [
            {
                "train": train,
                "available": train_availability(train, journey_date),
            }
            for train in queryset
        ]
        search = {
            "source": source,
            "destination": destination,
            "journey_date": journey_date,
        }

    return render(
        request,
        "etors/home.html",
        {
            "search_form": search_form,
            "pnr_form": pnr_form,
            "trains": trains,
            "search": search,
        },
    )


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out of ETORS.")
    return redirect("etors:home")


@transaction.atomic
def book(request, train_id, journey_date):
    train = get_object_or_404(
        Train.objects.select_for_update().select_related("source", "destination"),
        pk=train_id,
        active=True,
    )
    try:
        journey_date = date.fromisoformat(journey_date)
    except ValueError as exc:
        raise Http404("Invalid journey date") from exc
    if journey_date < date.today():
        messages.error(request, "Past journeys cannot be booked.")
        return redirect("etors:home")

    form = BookingForm(request.POST or None)
    available = train_availability(train, journey_date)
    if request.method == "POST" and form.is_valid():
        if available < 1:
            messages.error(request, "No seats are available for this train.")
        else:
            travel_class = form.cleaned_data["travel_class"]
            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                train=train,
                journey_date=journey_date,
                travel_class=travel_class,
                contact_name=form.cleaned_data["contact_name"],
                contact_email=form.cleaned_data["contact_email"],
                contact_phone=form.cleaned_data["contact_phone"],
                total_fare=fare_for(train, travel_class),
            )
            Passenger.objects.create(
                booking=booking,
                name=form.cleaned_data["passenger_name"],
                age=form.cleaned_data["passenger_age"],
                gender=form.cleaned_data["passenger_gender"],
                berth_preference=form.cleaned_data["berth_preference"],
                seat_number=seat_number(train, journey_date),
            )
            messages.success(request, f"Ticket confirmed. PNR: {booking.pnr}")
            return redirect("etors:pnr_detail", pnr=booking.pnr)

    return render(
        request,
        "etors/book.html",
        {
            "form": form,
            "train": train,
            "journey_date": journey_date,
            "available": available,
        },
    )


def pnr_search(request):
    form = PNRForm(request.GET or None)
    if form.is_valid():
        return redirect("etors:pnr_detail", pnr=form.cleaned_data["pnr"])
    messages.error(request, "Enter a valid 10-digit PNR.")
    return redirect("etors:home")


def pnr_detail(request, pnr):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "train", "train__source", "train__destination"
        ).prefetch_related("passengers"),
        pnr=pnr,
    )
    return render(request, "etors/pnr_detail.html", {"booking": booking})


@transaction.atomic
def cancel_booking(request, pnr):
    if request.method != "POST":
        raise Http404()
    booking = get_object_or_404(
        Booking.objects.select_for_update(), pnr=pnr
    )
    if booking.status == "CONFIRMED":
        booking.status = "CANCELLED"
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=["status", "cancelled_at"])
        messages.success(request, f"PNR {pnr} was cancelled successfully.")
    else:
        messages.info(request, "This booking is already cancelled.")
    return redirect("etors:pnr_detail", pnr=pnr)
