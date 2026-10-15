import pytest

from susu import SusuGroup
from susu.errors import (
    InvalidAmountError,
    InvalidWeekError,
    MembershipClosedError,
    OverpaymentError,
    UnknownMemberError,
)


@pytest.fixture
def group():
    g = SusuGroup("50.00")
    for name in ["Ama", "Kofi", "Esi"]:
        g.add_member(name)
    return g


def test_full_payment_leaves_nothing_owed(group):
    assert group.record_contribution("Ama", "50") == 0
    assert group.paid("Ama") == 5000


def test_partial_payments_add_up(group):
    assert group.record_contribution("Esi", "30") == 2000
    assert group.owed("Esi") == 2000
    assert group.record_contribution("Esi", "20.00") == 0
    assert group.paid("Esi") == 5000


def test_payment_above_amount_owed_rejected(group):
    group.record_contribution("Esi", "30")
    with pytest.raises(OverpaymentError):
        group.record_contribution("Esi", "20.01")
    assert group.paid("Esi") == 3000  # rejected payment changes nothing


def test_payment_after_paying_in_full_rejected(group):
    group.record_contribution("Ama", "50")
    with pytest.raises(OverpaymentError):
        group.record_contribution("Ama", "0.01")


@pytest.mark.parametrize("amount", ["0", "-10", "abc"])
def test_zero_negative_or_malformed_payment_rejected(group, amount):
    with pytest.raises(InvalidAmountError):
        group.record_contribution("Ama", amount)


def test_payment_from_unknown_member_rejected(group):
    with pytest.raises(UnknownMemberError):
        group.record_contribution("Yaw", "50")


def test_payment_for_other_week_rejected(group):
    group.record_contribution("Ama", "50", week=1)
    with pytest.raises(InvalidWeekError):
        group.record_contribution("Kofi", "50", week=2)


def test_cannot_add_member_after_first_contribution(group):
    group.record_contribution("Ama", "10")
    with pytest.raises(MembershipClosedError):
        group.add_member("Yaw")
