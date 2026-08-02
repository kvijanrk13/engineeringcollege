import re
from functools import lru_cache
from html import unescape
from pathlib import Path

from django.urls import URLPattern, URLResolver


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "etors"

ROUTE_DESCRIPTIONS = {
    "home": "Search active trains by source, destination, and journey date.",
    "book": "Reserve one passenger, choose Sleeper or AC 3 Tier, and receive a confirmed ticket.",
    "payment": "Complete a safe dummy payment simulation before ETORS confirms the reservation and assigns a seat.",
    "pnr_search": "Look up a booking using its 10-digit PNR.",
    "pnr_detail": "View booking status, journey, passenger, seat, class, fare, and contact details.",
    "cancel_booking": "Cancel a confirmed ETORS reservation and release its seat.",
    "logout": "Sign out of the ETORS account safely.",
}

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
        "Search for a train, choose Book Ticket, enter the contact and passenger details, "
        "select Sleeper or AC 3 Tier, and continue to dummy payment. After the simulated payment succeeds, "
        "ETORS assigns a seat and generates a 10-digit PNR."
    ),
    "fare": (
        "ETORS displays the Sleeper and AC 3 Tier fares on the booking page. "
        "It is an academic prototype and does not collect real payment."
    ),
    "pnr": (
        "Open PNR Status on the ETORS home page and enter the 10-digit PNR from the confirmation. "
        "The result shows booking status, train, route, journey, class, fare, passenger, seat, and contact details."
    ),
    "cancel": (
        "Find the reservation using its 10-digit PNR, then choose Cancel Ticket on a confirmed booking. "
        "ETORS marks it cancelled and releases the seat. This prototype does not process real payments or refunds."
    ),
    "login": (
        "Choose Login with Gmail in the ETORS navigation bar. ETORS accepts the configured verified Gmail accounts. "
        "Train search, booking, and PNR services are also available in the current demonstration workflow."
    ),
    "passenger": (
        "The current ETORS release supports one passenger per booking, including name, age, gender, "
        "berth preference, contact details, and an assigned seat number."
    ),
    "payment": (
        "ETORS provides a dummy payment interface for UPI, card, or net banking. Clicking Pay & Reserve displays "
        "PAYMENT SUCCESSFULL, assigns a dummy seat, and generates a PNR. No real money is collected and no real "
        "railway ticket or refund is issued."
    ),
    "admin": (
        "Authorized administrators can manage ETORS stations, trains, bookings, and passengers through Django admin."
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
    features = list(template_features())
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
        "PNR status, cancellation, passengers, Gmail login, or whether real payment is supported."
    )
