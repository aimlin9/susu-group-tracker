"""Plain data records returned by SusuGroup. All amounts are in pesewas."""

from dataclasses import dataclass, field

from .money import format_amount


@dataclass(frozen=True)
class Payout:
    """One week's pot paid to one member."""

    week: int
    recipient: str
    amount: int


@dataclass(frozen=True)
class CloseResult:
    """Outcome of trying to close a week.

    Either `payout` is set (week closed) or `outstanding` lists who still owes
    what (week stays open). Not closing is a normal outcome, not an error.
    """

    week: int
    payout: Payout | None = None
    outstanding: dict[str, int] = field(default_factory=dict)

    @property
    def closed(self) -> bool:
        return self.payout is not None

    def message(self) -> str:
        if self.payout:
            return (
                f"Week {self.week} closed: {self.payout.recipient} receives "
                f"{format_amount(self.payout.amount)}"
            )
        debts = ", ".join(
            f"{name} owes {format_amount(amount)}" for name, amount in self.outstanding.items()
        )
        return f"Week {self.week} cannot close: {debts}"
