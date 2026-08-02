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
    MAX_PASSENGERS = 5
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
    book_cab = forms.BooleanField(
        required=False,
        label="Add BOOKMYCAB at destination",
    )
    cab_type = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Select cab type"),
            ("MINI", "Mini - ₹350"),
            ("SEDAN", "Sedan - ₹500"),
            ("SUV", "SUV - ₹750"),
        ),
    )
    cab_drop_address = forms.CharField(
        required=False,
        max_length=240,
        label="Destination drop address",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for number in range(2, self.MAX_PASSENGERS + 1):
            self.fields[f"passenger_{number}_name"] = forms.CharField(
                max_length=100, required=False, label="Passenger name"
            )
            self.fields[f"passenger_{number}_age"] = forms.IntegerField(
                min_value=1, max_value=120, required=False, label="Age"
            )
            self.fields[f"passenger_{number}_gender"] = forms.ChoiceField(
                choices=(("", "Select gender"), *Passenger.GENDER_CHOICES),
                required=False,
                label="Gender",
            )
            self.fields[f"passenger_{number}_berth_preference"] = forms.ChoiceField(
                required=False,
                label="Berth preference",
                choices=self.fields["berth_preference"].choices,
            )
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["book_cab"].widget.attrs["class"] = "cab-checkbox"

    def clean(self):
        cleaned = super().clean()
        passengers = [
            {
                "name": cleaned.get("passenger_name"),
                "age": cleaned.get("passenger_age"),
                "gender": cleaned.get("passenger_gender"),
                "berth_preference": cleaned.get("berth_preference", ""),
            }
        ]
        for number in range(2, self.MAX_PASSENGERS + 1):
            prefix = f"passenger_{number}_"
            values = {
                "name": cleaned.get(prefix + "name"),
                "age": cleaned.get(prefix + "age"),
                "gender": cleaned.get(prefix + "gender"),
                "berth_preference": cleaned.get(prefix + "berth_preference", ""),
            }
            supplied = any(values.values())
            if supplied:
                for key in ("name", "age", "gender"):
                    if not values[key]:
                        self.add_error(prefix + key, "Complete this passenger's details.")
                if values["name"] and values["age"] and values["gender"]:
                    passengers.append(values)
        cleaned["passengers"] = passengers
        if cleaned.get("book_cab"):
            if not cleaned.get("cab_type"):
                self.add_error("cab_type", "Select a BOOKMYCAB vehicle type.")
            if not cleaned.get("cab_drop_address"):
                self.add_error("cab_drop_address", "Enter the destination drop address.")
        else:
            cleaned["cab_type"] = ""
            cleaned["cab_drop_address"] = ""
        return cleaned


class PNRForm(forms.Form):
    pnr = forms.RegexField(
        regex=r"^\d{10}$",
        label="PNR Number",
        error_messages={"invalid": "Enter a valid 10-digit PNR."},
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 10-digit PNR"}
        ),
    )
