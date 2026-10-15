"""Exceptions raised by the susu tracker.

Every rule violation raises a subclass of SusuError, so callers (the CLI,
tests) can catch one type and show the message to the user.
"""


class SusuError(Exception):
    """Base class for all susu rule violations."""


class InvalidAmountError(SusuError):
    """Amount is zero, negative, malformed or has more than 2 decimal places."""


class DuplicateMemberError(SusuError):
    """A member with the same name already exists in the group."""


class UnknownMemberError(SusuError):
    """The named member is not part of the group."""


class InvalidMemberNameError(SusuError):
    """Member name is empty or blank."""


class OverpaymentError(SusuError):
    """Payment is more than the member still owes for the week."""


class InvalidWeekError(SusuError):
    """Payment is for a week other than the one currently open."""


class MembershipClosedError(SusuError):
    """Members cannot be added once the first contribution has been recorded."""
