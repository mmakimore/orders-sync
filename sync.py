"""Normalize and deduplicate raw advertisement orders."""
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


def normalize_phone(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) == 10 and digits.startswith("9"):
        digits = "7" + digits
    elif len(digits) == 11 and digits[0] == "8":
        digits = "7" + digits[1:]
    if len(digits) != 11 or not digits.startswith("79"):
        return None
    return "+" + digits


def _amount(order):
    try:
        return Decimal(str(order.get("amount", 0)))
    except (InvalidOperation, ValueError):
        return Decimal(0)


def _date(order):
    try:
        value = datetime.fromisoformat(str(order.get("created_at", "")).replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def synchronize(orders):
    chosen = {}
    invalid = 0
    for order in orders:
        phone = normalize_phone(order.get("phone"))
        if phone is None:
            invalid += 1
            continue
        previous = chosen.get(phone)
        if previous is None or (_amount(order), _date(order)) > (_amount(previous), _date(previous)):
            chosen[phone] = order

    clients = [
        {"name": row.get("name", ""), "phone": phone,
         "email": row.get("email", ""), "amount": row.get("amount", 0)}
        for phone, row in sorted(chosen.items())
    ]
    return {
        "clients": clients,
        "stats": {
            "received": len(orders),
            "unique": len(clients),
            "duplicates_merged": len(orders) - invalid - len(clients),
            "invalid_dropped": invalid,
        },
    }
