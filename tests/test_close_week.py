import pytest

from susu import SusuGroup
from susu.errors import GroupStateError, MembershipClosedError


@pytest.fixture
def group():
    g = SusuGroup("50.00")
    for name in ["Ama", "Kofi", "Esi"]:
        g.add_member(name)
    return g


def pay_in_full(group, *names):
    for name in names:
        group.record_contribution(name, "50.00")


def test_week_cannot_close_when_someone_owes(group):
    pay_in_full(group, "Ama", "Kofi")
    group.record_contribution("Esi", "30")

    result = group.close_week()

    assert not result.closed
    assert result.outstanding == {"Esi": 2000}
    assert result.message() == "Week 1 cannot close: Esi owes 20.00"
    assert group.current_week == 1
    assert group.payouts == []


def test_week_cannot_close_lists_every_debtor(group):
    group.record_contribution("Kofi", "10")
    result = group.close_week()
    assert result.outstanding == {"Ama": 5000, "Kofi": 4000, "Esi": 5000}


def test_full_example_from_spec(group):
    pay_in_full(group, "Ama", "Kofi")
    group.record_contribution("Esi", "30")
    assert not group.close_week().closed

    group.record_contribution("Esi", "20")
    result = group.close_week()

    assert result.closed
    assert result.message() == "Week 1 closed: Ama receives 150.00"
    assert group.current_week == 2
    assert group.next_recipient == "Kofi"
    assert group.owed("Ama") == 5000  # new week, everyone owes again


def test_pot_rotates_in_join_order_and_cycle_completes(group):
    for _ in range(3):
        pay_in_full(group, "Ama", "Kofi", "Esi")
        assert group.close_week().closed

    assert [(p.week, p.recipient, p.amount) for p in group.payouts] == [
        (1, "Ama", 15000),
        (2, "Kofi", 15000),
        (3, "Esi", 15000),
    ]
    assert group.is_complete
    assert group.next_recipient is None
    with pytest.raises(GroupStateError):
        group.record_contribution("Ama", "50")
    with pytest.raises(GroupStateError):
        group.close_week()


def test_cannot_close_week_with_no_members():
    with pytest.raises(GroupStateError):
        SusuGroup("50").close_week()


def test_membership_locked_after_week_closes():
    g = SusuGroup("50")
    g.add_member("Ama")
    g.record_contribution("Ama", "50")
    g.close_week()
    with pytest.raises(MembershipClosedError):
        g.add_member("Kofi")
