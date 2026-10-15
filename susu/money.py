"""Exact money handling.

All amounts are stored internally as whole pesewas (int). 1 GHS = 100 pesewas.
Integer arithmetic never rounds, so totals are always exact. Input is parsed
through Decimal (never float) and anything finer than 1 pesewa is rejected
instead of being silently rounded.
"""

from decimal import Decimal, InvalidOperation

from .errors import InvalidAmountError

PESEWAS_PER_CEDI = 100


def parse_amount(value) -> int:
    """Convert a GHS amount such as "50", "50.5" or "50.00" into pesewas.

    Accepts str, int or Decimal. Floats are rejected because they cannot
    represent most decimal amounts exactly (0.1 + 0.2 != 0.3).
    The amount must be positive and have at most 2 decimal places.
    """
    if isinstance(value, bool) or isinstance(value, float):
        raise InvalidAmountError(
            f"Amount must be given as text or Decimal, not {type(value).__name__}"
        )

    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise InvalidAmountError(f"'{value}' is not a valid amount") from None

    if not amount.is_finite():
        raise InvalidAmountError(f"'{value}' is not a valid amount")

    pesewas = amount * PESEWAS_PER_CEDI
    if pesewas != pesewas.to_integral_value():
        raise InvalidAmountError(
            f"'{value}' has more than 2 decimal places (smallest unit is 0.01 GHS)"
        )
    if pesewas <= 0:
        raise InvalidAmountError(f"Amount must be greater than zero, got '{value}'")

    return int(pesewas)


def format_amount(pesewas: int) -> str:
    """Format pesewas as a GHS string with exactly 2 decimals, e.g. 15000 -> "150.00"."""
    sign = "-" if pesewas < 0 else ""
    cedis, rest = divmod(abs(pesewas), PESEWAS_PER_CEDI)
    return f"{sign}{cedis}.{rest:02d}"
