import re
from functools import lru_cache
from html import unescape
from pathlib import Path

from django.urls import URLPattern, URLResolver


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "etors"

ROUTE_DESCRIPTIONS = {
    "home": "Search active trains by source, destination, and journey date.",
    "book": "After verified Gmail login, add up to five passengers, select one of six travel classes, include dummy insurance, and optionally add BOOKMYCAB.",
    "payment": "Use dummy UPI, card, or net banking to confirm seats, insurance policies, PNR, and an optional cab.",
    "pnr_search": "Securely look up a booking using its 10-digit PNR and registered mobile number.",
    "pnr_detail": "View booking status, journey, passenger, seat, class, fare, and contact details.",
    "cancel_booking": "Cancel a confirmed ETORS reservation and release its seat.",
    "logout": "Sign out of the ETORS account safely.",
    "cab_dispatch": "Give a cab driver a privacy-protected dispatch view and reveal the drop address only after pickup OTP verification.",
}

FEATURE_CATALOG = (
    "Train search between Khammam, Vijayawada, and Secunderabad with a 120-day calendar",
    "Live dummy seat availability and cancellation-based seat release",
    "Verified Gmail login required before booking or payment",
    "Up to five passengers; ages 1–5 have no berth or fare, while passengers older than 5 receive a berth",
    "General, Sleeper, 1A, 2A, 3A, and 3E travel classes with dummy fares",
    "Dummy UPI, card, and net-banking payment with PNR and seat confirmation",
    "Protected PNR access requiring the PNR and registered mobile number",
    "BOOKMYCAB Bike, Auto, Mini, Sedan, SUV, Tempo Traveller, and Bus options from ₹150 to ₹2,500",
    "Privacy-protected cab dispatch with no passenger identity or PNR and OTP-gated drop-address disclosure",
    "Automatic dummy train and cab insurance premiums, policies, coverage, and claim guidance",
    "Dummy train helpline 1800-000-3877 and BOOKMYCAB helpline 1800-000-2222",
)

INTENT_ANSWERS = {
    "search": (
        "Use Search Trains on the ETORS home page. Select the source, destination, "
        "and journey date; ETORS will show matching active trains, timings, and seat availability."
    ),
    "availability": (
        "Seat availability is calculated for the selected train and journey date. "
        "Cancelled confirmed bookings release their seats back into availability."
    ),
    "booking": (
        "Login with a verified Gmail account, search for a train, and choose Book Ticket. Add up to five passengers; "
        "select General, Sleeper, 1A, 2A, 3A, or 3E; and optionally add BOOKMYCAB. Dummy insurance is included. "
        "After dummy payment, ETORS assigns berths, issues policy references, and generates a 10-digit PNR."
    ),
    "fare": (
        "ETORS displays dummy fares for General, Sleeper, AC First Class (1A), AC 2 Tier (2A), "
        "AC 3 Tier (3A), and AC 3 Economy (3E) on the booking page. "
        "It is an academic prototype and does not collect real payment."
    ),
    "pnr": (
        "Open PNR Status and enter both the 10-digit PNR and its registered mobile number. A PNR alone cannot expose data. "
        "The result shows booking status, train, route, journey, class, fare, passenger, seat, and contact details."
    ),
    "cancel": (
        "Verify the reservation using its PNR and registered mobile number, then choose Cancel Ticket. "
        "ETORS marks it cancelled and releases the seat. This prototype does not process real payments or refunds."
    ),
    "login": (
        "Choose Login with Gmail in the ETORS navigation bar. Ticket booking and payment require a verified Gmail "
        "login; an anonymous or ordinary non-ETORS session cannot book. Train search remains publicly available."
    ),
    "passenger": (
        "ETORS supports up to five dummy passengers per booking. Passengers older than 5 receive a berth "
        "and are charged the selected train fare; children aged 1–5 are listed without a separate berth or fare."
    ),
    "insurance": (
        "Every fare-paying passenger receives ₹0.45 dummy train insurance with demonstration accident, disability, "
        "and hospital coverage. BOOKMYCAB reservations receive ₹10 dummy cab-trip insurance. Policy references "
        "appear after payment and in the protected PNR view. These are academic simulations, not real policies or claims."
    ),
    "helpline": (
        "For this academic demonstration, call the dummy ETORS train-booking helpline 1800-000-3877 "
        "or the dummy BOOKMYCAB helpline 1800-000-2222. These are not real customer-service numbers."
    ),
    "payment": (
        "ETORS provides a dummy payment interface for UPI, card, or net banking. Clicking Pay & Reserve displays "
        "PAYMENT SUCCESSFULL, assigns a dummy seat, and generates a PNR. No real money is collected and no real "
        "railway ticket or refund is issued."
    ),
    "admin": (
        "Authorized administrators can manage ETORS stations, trains, bookings, and passengers through Django admin."
    ),
    "cab": (
        "BOOKMYCAB offers Bike ₹150, Auto ₹250, Mini ₹350, Sedan ₹500, SUV ₹750, Tempo Traveller ₹1,200, "
        "and Bus ₹2,500, with capacity checks from 1 to 30 passengers. Enter the destination drop address; after dummy payment, ETORS assigns a driver and "
        "vehicle and schedules the cab at the destination station 20 minutes before train arrival. The driver uses a "
        "random private dispatch link, receives no passenger identity or PNR, and sees the exact drop address only after pickup OTP verification."
    ),
    "security": (
        "PNR details require the matching registered mobile number; a PNR alone cannot reveal passenger data, and verification attempts are limited. Cab drivers receive no passenger identity. They "
        "receive only a random dispatch reference, station, train number, and arrival time—not the PNR, name, mobile, "
        "email, age, gender, or seat. The exact drop address appears only after a valid short-lived pickup OTP."
    ),
}

INTENT_KEYWORDS = {
    "search": {"search", "find", "route", "train", "trains", "station", "journey"},
    "availability": {"availability", "available", "seat", "seats", "sold", "capacity"},
    "booking": {"book", "booking", "reserve", "reservation", "ticket", "confirm"},
    "fare": {"fare", "cost", "price", "sleeper", "ac", "class"},
    "pnr": {"pnr", "status", "track", "lookup", "retrieve"},
    "cancel": {"cancel", "cancellation", "refund", "release"},
    "login": {"login", "gmail", "account", "logout", "sign"},
    "passenger": {"passenger", "berth", "gender", "age", "contact"},
    "payment": {"payment", "pay", "money", "real", "irctc"},
    "admin": {"admin", "manage", "management"},
    "cab": {"cab", "taxi", "bookmycab", "pickup", "driver", "vehicle", "drop", "doorstep"},
    "insurance": {"insurance", "policy", "premium", "claim", "coverage", "accident"},
    "helpline": {"helpline", "help line", "phone number", "customer care", "support number", "call"},
    "security": {"privacy", "private", "security", "secure", "otp", "tracked", "tracking", "protect", "driver access"},
}

FEATURE_WORDS = {"feature", "features", "service", "services", "help", "offer", "available", "do"}
GREETINGS = {"hi", "hello", "hey", "namaste", "start"}
STOP_WORDS = {
    "a", "an", "and", "are", "can", "does", "for", "how", "i", "in", "is", "it", "me",
    "my", "of", "on", "please", "the", "this", "to", "what", "with", "you",
}


def _words(value):
    return set(re.findall(r"[a-z0-9]+", value.lower())) - STOP_WORDS


def _humanize_route(name):
    return re.sub(r"[_-]+", " ", name).strip().capitalize()


def _walk_patterns(patterns, prefix=""):
    for pattern in patterns:
        route = f"{prefix}{pattern.pattern}"
        if isinstance(pattern, URLResolver):
            yield from _walk_patterns(pattern.url_patterns, route)
        elif isinstance(pattern, URLPattern):
            yield pattern, route


def route_capabilities():
    # Imported lazily to avoid a circular import while etors.urls imports views.
    from .urls import urlpatterns

    capabilities = []
    for pattern, route in _walk_patterns(urlpatterns):
        name = pattern.name or ""
        if not name or name == "chatbot":
            continue
        description = ROUTE_DESCRIPTIONS.get(
            name,
            f"Use the {_humanize_route(name)} service in ETORS.",
        )
        capabilities.append({"name": _humanize_route(name), "description": description, "route": route})
    return capabilities


@lru_cache(maxsize=1)
def template_features():
    """Read visible feature list items so documented additions become searchable."""
    features = []
    for template in TEMPLATE_DIR.glob("*.html"):
        content = template.read_text(encoding="utf-8")
        for item in re.findall(r"<li[^>]*>(.*?)</li>", content, flags=re.I | re.S):
            text = re.sub(r"{%.*?%}|{{.*?}}|<[^>]+>", " ", item, flags=re.S)
            text = re.sub(r"\s+", " ", unescape(text)).strip(" .")
            if text and text not in features:
                features.append(text)
    return features


def feature_summary():
    features = list(FEATURE_CATALOG) + list(template_features())
    normalized = {feature.lower().rstrip(".") for feature in features}
    for item in route_capabilities():
        description = item["description"].strip()
        if description.lower().rstrip(".") not in normalized:
            features.append(description)
            normalized.add(description.lower().rstrip("."))
    return "ETORS currently provides: " + "; ".join(
        feature.rstrip(".") for feature in features
    ) + "."


def answer_question(question):
    question = re.sub(r"\s+", " ", (question or "")).strip()
    words = _words(question)
    if not words:
        return "Ask me about ETORS train search, seat availability, booking, fares, PNR status, cancellation, or login."
    if words <= GREETINGS:
        return "Hello! I’m the ETORS assistant. " + feature_summary()
    if words & FEATURE_WORDS or "what can" in question.lower():
        return feature_summary()

    # Prefer narrow feature intents when a question also contains broad words
    # such as booking, cab, passenger, or PNR.
    for intent in ("helpline", "insurance", "security"):
        if words & INTENT_KEYWORDS[intent]:
            return INTENT_ANSWERS[intent]
    if "bookmycab" in words:
        return INTENT_ANSWERS["cab"]

    scores = {
        intent: len(words & keywords)
        for intent, keywords in INTENT_KEYWORDS.items()
    }
    best_intent = max(scores, key=scores.get)
    if scores[best_intent]:
        return INTENT_ANSWERS[best_intent]

    candidates = route_capabilities()
    ranked = sorted(
        (
            len(words & _words(f"{item['name']} {item['description']}")),
            item,
        )
        for item in candidates
    )
    if ranked and ranked[-1][0] > 0:
        return ranked[-1][1]["description"]
    return (
        "I couldn’t match that to an ETORS service. Ask about train search, availability, booking, fares, "
        "PNR security, cancellation, passengers, travel classes, Gmail login, insurance, BOOKMYCAB privacy, payment, or helplines."
    )
