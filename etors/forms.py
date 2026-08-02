from datetime import date, timedelta

from django import forms

from .models import Booking, Passenger, Station


class SearchForm(forms.Form):
    source = forms.ModelChoiceField(queryset=Station.objects.none())
    destination = forms.ModelChoiceField(queryset=Station.objects.none())
    journey_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=lambda: date.today() + timedelta(days=1),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stations = Station.objects.all()
        self.fields["source"].queryset = stations
        self.fields["destination"].queryset = stations
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["journey_date"].widget.attrs.update(
            {
                "min": date.today().isoformat(),
                "max": (date.today() + timedelta(days=120)).isoformat(),
            }
        )

    def clean_journey_date(self):
        journey_date = self.cleaned_data["journey_date"]
        if journey_date < date.today():
            raise forms.ValidationError("Journey date cannot be in the past.")
        if journey_date > date.today() + timedelta(days=120):
            raise forms.ValidationError("Bookings open only 120 days in advance.")
        return journey_date

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("source") == cleaned.get("destination"):
            self.add_error("destination", "Source and destination must be different.")
        return cleaned


class BookingForm(forms.Form):
    travel_class = forms.ChoiceField(choices=Booking.CLASS_CHOICES)
    contact_name = forms.CharField(max_length=100)
    contact_email = forms.EmailField()
    contact_phone = forms.RegexField(
        regex=r"^[6-9]\d{9}$",
        error_messages={"invalid": "Enter a valid 10-digit Indian mobile number."},
    )
    passenger_name = forms.CharField(max_length=100)
    passenger_age = forms.IntegerField(min_value=1, max_value=120)
    passenger_gender = forms.ChoiceField(choices=Passenger.GENDER_CHOICES)
    berth_preference = forms.ChoiceField(
        required=False,
        choices=(
            ("", "No preference"),
            ("Lower", "Lower"),
            ("Middle", "Middle"),
            ("Upper", "Upper"),
            ("Side Lower", "Side Lower"),
            ("Side Upper", "Side Upper"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class PNRForm(forms.Form):
    pnr = forms.RegexField(
        regex=r"^\d{10}$",
        label="PNR Number",
        error_messages={"invalid": "Enter a valid 10-digit PNR."},
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 10-digit PNR"}
        ),
    )
