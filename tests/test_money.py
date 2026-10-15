from decimal import Decimal

import pytest

from susu.errors import InvalidAmountError
from susu.money import format_amount, parse_amount


@pytest.mark.parametrize(
    "value, expected",
    [("50", 5000), ("50.00", 5000), ("50.5", 5050), ("0.01", 1), (20, 2000), (Decimal("12.34"), 1234)],
)
def test_parse_amount_converts_to_pesewas(value, expected):
    assert parse_amount(value) == expected


@pytest.mark.parametrize("value", ["0", "0.00", "-5", "-0.01"])
def test_parse_amount_rejects_zero_and_negative(value):
    with pytest.raises(InvalidAmountError):
        parse_amount(value)


@pytest.mark.parametrize("value", ["abc", "", "NaN", "Infinity", "10.005", 10.5, True])
def test_parse_amount_rejects_malformed_or_inexact(value):
    with pytest.raises(InvalidAmountError):
        parse_amount(value)


def test_no_rounding_errors_when_summing():
    # 0.1 + 0.2 is 0.30000000000000004 with floats; must be exact here.
    assert parse_amount("0.10") + parse_amount("0.20") == parse_amount("0.30")


@pytest.mark.parametrize("pesewas, text", [(15000, "150.00"), (5, "0.05"), (0, "0.00"), (-2000, "-20.00")])
def test_format_amount(pesewas, text):
    assert format_amount(pesewas) == text
