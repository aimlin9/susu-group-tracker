"""Core domain model: one rotating savings group (susu)."""

from .errors import (
    DuplicateMemberError,
    GroupStateError,
    InvalidMemberNameError,
    InvalidWeekError,
    MembershipClosedError,
    OverpaymentError,
    UnknownMemberError,
)
from .models import CloseResult, Payout
from .money import format_amount, parse_amount


class SusuGroup:
    """A rotating savings group with a fixed weekly contribution.

    Members are kept in the order they joined; that order is the payout order.
    Member names are unique ignoring case and surrounding spaces, so "Ama" and
    " ama " are treated as the same person.

    Only the current week accepts payments. Membership is locked as soon as
    the first contribution is recorded, so the payout order never changes
    once money is in the pot. The cycle is complete once every member has
    received the pot exactly once; after that no more payments are accepted.
    """

    def __init__(self, weekly_amount):
        self.weekly_amount = parse_amount(weekly_amount)  # pesewas
        self._members: list[str] = []
        self.current_week = 1
        self._paid: dict[str, int] = {}  # member -> pesewas paid this week
        self._started = False
        self._payouts: list[Payout] = []

    @property
    def members(self) -> list[str]:
        """Member names in join (= payout) order."""
        return list(self._members)

    def add_member(self, name: str) -> str:
        """Add a member to the end of the payout order and return the stored name."""
        if self._started:
            raise MembershipClosedError(
                "Members cannot be added after the first contribution is recorded"
            )
        clean = (name or "").strip()
        if not clean:
            raise InvalidMemberNameError("Member name cannot be empty")
        if self._find(clean) is not None:
            raise DuplicateMemberError(f"Member '{clean}' already exists")
        self._members.append(clean)
        return clean

    @property
    def payouts(self) -> list[Payout]:
        """Payout history, oldest first."""
        return list(self._payouts)

    @property
    def is_complete(self) -> bool:
        """True once every member has received the pot."""
        return bool(self._members) and len(self._payouts) == len(self._members)

    @property
    def pot(self) -> int:
        """Pesewas paid out when a week closes: everyone's full contribution."""
        return self.weekly_amount * len(self._members)

    @property
    def next_recipient(self) -> str | None:
        """Member who receives the pot when the current week closes."""
        if self.is_complete or not self._members:
            return None
        return self._members[len(self._payouts)]

    def resolve_member(self, name: str) -> str:
        """Return the stored spelling of a member's name, or raise if unknown."""
        found = self._find((name or "").strip())
        if found is None:
            raise UnknownMemberError(f"Unknown member '{name}'")
        return found

    def paid(self, name: str) -> int:
        """Pesewas the member has paid towards the current week."""
        return self._paid.get(self.resolve_member(name), 0)

    def owed(self, name: str) -> int:
        """Pesewas the member still owes for the current week."""
        return self.weekly_amount - self.paid(name)

    def record_contribution(self, name: str, amount, week: int | None = None) -> int:
        """Record a (possibly partial) payment and return what the member still owes.

        `week` defaults to the current week; any other week is rejected.
        """
        member = self.resolve_member(name)
        pesewas = parse_amount(amount)
        if self.is_complete:
            raise GroupStateError("The cycle is complete; every member has been paid")
        if week is not None and week != self.current_week:
            raise InvalidWeekError(
                f"Week {self.current_week} is the open week; cannot pay for week {week}"
            )
        owed = self.owed(member)
        if owed == 0:
            raise OverpaymentError(f"{member} has already paid in full for week {self.current_week}")
        if pesewas > owed:
            raise OverpaymentError(
                f"{member} only owes {format_amount(owed)} for week {self.current_week}, "
                f"cannot pay {format_amount(pesewas)}"
            )
        self._paid[member] = self._paid.get(member, 0) + pesewas
        self._started = True
        return self.owed(member)

    def outstanding(self) -> dict[str, int]:
        """Members who have not paid in full this week -> pesewas owed, in join order."""
        return {m: self.owed(m) for m in self._members if self.owed(m) > 0}

    def close_week(self) -> CloseResult:
        """Close the current week.

        If everyone has paid in full, pay the pot to the next member in join
        order and open the next week. Otherwise nothing changes and the result
        lists who still owes what.
        """
        if not self._members:
            raise GroupStateError("Cannot close a week in a group with no members")
        if self.is_complete:
            raise GroupStateError("The cycle is complete; every member has been paid")

        week = self.current_week
        outstanding = self.outstanding()
        if outstanding:
            return CloseResult(week=week, outstanding=outstanding)

        payout = Payout(week=week, recipient=self.next_recipient, amount=self.pot)
        self._payouts.append(payout)
        self._paid = {}
        if not self.is_complete:
            self.current_week += 1
        return CloseResult(week=week, payout=payout)

    def _find(self, name: str):
        key = name.casefold()
        for member in self._members:
            if member.casefold() == key:
                return member
        return None
