from datetime import date

from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingForm, PNRForm, SearchForm
from .models import Booking, CabBooking, Passenger, Train
from .services import (
    cab_fare_for,
    create_cab_booking,
    fare_for,
    seat_number,
    train_availability,
)
from .chatbot import answer_question


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


@require_POST
def chatbot(request):
    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "Enter a question about ETORS."}, status=400)
    if len(question) > 500:
        return JsonResponse({"error": "Keep your question within 500 characters."}, status=400)
    return JsonResponse({"answer": answer_question(question)})


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
            request.session["etors_pending_booking"] = {
                "train_id": train.pk,
                "journey_date": journey_date.isoformat(),
                **form.cleaned_data,
            }
            return redirect("etors:payment")

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


@transaction.atomic
def payment(request):
    pending = request.session.get("etors_pending_booking")
    if not pending:
        messages.error(request, "Start a reservation before opening dummy payment.")
        return redirect("etors:home")

    train = get_object_or_404(
        Train.objects.select_for_update().select_related("source", "destination"),
        pk=pending["train_id"],
        active=True,
    )
    journey_date = date.fromisoformat(pending["journey_date"])
    train_fare = fare_for(train, pending["travel_class"])
    cab_fare = cab_fare_for(pending.get("cab_type")) if pending.get("book_cab") else 0
    total_fare = train_fare + cab_fare

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        if payment_method not in {"UPI", "CARD", "NETBANKING"}:
            messages.error(request, "Select a dummy payment method.")
        elif train_availability(train, journey_date) < 1:
            request.session.pop("etors_pending_booking", None)
            messages.error(request, "No seats are available for this train now.")
            return redirect("etors:home")
        else:
            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                train=train,
                journey_date=journey_date,
                travel_class=pending["travel_class"],
                contact_name=pending["contact_name"],
                contact_email=pending["contact_email"],
                contact_phone=pending["contact_phone"],
                total_fare=total_fare,
            )
            passenger = Passenger.objects.create(
                booking=booking,
                name=pending["passenger_name"],
                age=pending["passenger_age"],
                gender=pending["passenger_gender"],
                berth_preference=pending["berth_preference"],
                seat_number=seat_number(train, journey_date),
            )
            cab_booking = None
            if pending.get("book_cab"):
                cab_booking = create_cab_booking(
                    booking,
                    pending["cab_type"],
                    pending["cab_drop_address"],
                )
            request.session.pop("etors_pending_booking", None)
            return render(
                request,
                "etors/payment_success.html",
                {
                    "booking": booking,
                    "passenger": passenger,
                    "cab_booking": cab_booking,
                    "payment_method": payment_method,
                },
            )

    return render(
        request,
        "etors/payment.html",
        {
            "train": train,
            "journey_date": journey_date,
            "travel_class": dict(Booking.CLASS_CHOICES)[pending["travel_class"]],
            "passenger_name": pending["passenger_name"],
            "train_fare": train_fare,
            "cab_fare": cab_fare,
            "book_cab": pending.get("book_cab", False),
            "cab_type": dict(CabBooking.CAB_CHOICES).get(pending.get("cab_type"), ""),
            "total_fare": total_fare,
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
            "train", "train__source", "train__destination", "cab_booking", "cab_booking__pickup_station"
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
        if hasattr(booking, "cab_booking"):
            booking.cab_booking.status = "CANCELLED"
            booking.cab_booking.save(update_fields=["status"])
        messages.success(request, f"PNR {pnr} was cancelled successfully.")
    else:
        messages.info(request, "This booking is already cancelled.")
    return redirect("etors:pnr_detail", pnr=pnr)
