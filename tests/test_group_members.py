import pytest

from susu import SusuGroup
from susu.errors import (
    DuplicateMemberError,
    InvalidAmountError,
    InvalidMemberNameError,
    UnknownMemberError,
)


def test_create_group_with_weekly_amount():
    group = SusuGroup("50.00")
    assert group.weekly_amount == 5000
    assert group.members == []


@pytest.mark.parametrize("amount", ["0", "-50", "50.001"])
def test_create_group_rejects_invalid_weekly_amount(amount):
    with pytest.raises(InvalidAmountError):
        SusuGroup(amount)


def test_members_keep_join_order():
    group = SusuGroup("50")
    for name in ["Ama", "Kofi", "Esi"]:
        group.add_member(name)
    assert group.members == ["Ama", "Kofi", "Esi"]


def test_duplicate_member_rejected_ignoring_case_and_spaces():
    group = SusuGroup("50")
    group.add_member("Ama")
    with pytest.raises(DuplicateMemberError):
        group.add_member(" ama ")


@pytest.mark.parametrize("name", ["", "   ", None])
def test_blank_member_name_rejected(name):
    with pytest.raises(InvalidMemberNameError):
        SusuGroup("50").add_member(name)


def test_resolve_unknown_member_rejected():
    group = SusuGroup("50")
    group.add_member("Ama")
    assert group.resolve_member("AMA") == "Ama"
    with pytest.raises(UnknownMemberError):
        group.resolve_member("Yaw")
