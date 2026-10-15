"""Core domain model: one rotating savings group (susu)."""

from .errors import DuplicateMemberError, InvalidMemberNameError, UnknownMemberError
from .money import parse_amount


class SusuGroup:
    """A rotating savings group with a fixed weekly contribution.

    Members are kept in the order they joined; that order is the payout order.
    Member names are unique ignoring case and surrounding spaces, so "Ama" and
    " ama " are treated as the same person.
    """

    def __init__(self, weekly_amount):
        self.weekly_amount = parse_amount(weekly_amount)  # pesewas
        self._members: list[str] = []

    @property
    def members(self) -> list[str]:
        """Member names in join (= payout) order."""
        return list(self._members)

    def add_member(self, name: str) -> str:
        """Add a member to the end of the payout order and return the stored name."""
        clean = (name or "").strip()
        if not clean:
            raise InvalidMemberNameError("Member name cannot be empty")
        if self._find(clean) is not None:
            raise DuplicateMemberError(f"Member '{clean}' already exists")
        self._members.append(clean)
        return clean

    def resolve_member(self, name: str) -> str:
        """Return the stored spelling of a member's name, or raise if unknown."""
        found = self._find((name or "").strip())
        if found is None:
            raise UnknownMemberError(f"Unknown member '{name}'")
        return found

    def _find(self, name: str):
        key = name.casefold()
        for member in self._members:
            if member.casefold() == key:
                return member
        return None
