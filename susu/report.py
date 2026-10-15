"""Plain-text report of a group's current state."""

from .group import SusuGroup
from .money import format_amount


def build_report(group: SusuGroup) -> str:
    """Current week, who has paid in full, who owes what, and payout history."""
    lines = [f"Weekly contribution: GHS {format_amount(group.weekly_amount)}"]

    if group.is_complete:
        lines.append(f"Cycle complete after {len(group.payouts)} week(s); every member has been paid.")
    else:
        lines.append(f"Current week: {group.current_week}")
        if group.members:
            lines.append(
                f"Next payout: {group.next_recipient} receives GHS {format_amount(group.pot)}"
            )

        if not group.members:
            lines.append("No members yet.")
        else:
            paid = [m for m in group.members if group.owed(m) == 0]
            lines.append("")
            lines.append("Paid in full:")
            if paid:
                lines.extend(f"  {m}" for m in paid)
            else:
                lines.append("  (nobody yet)")

            owing = group.outstanding()
            lines.append("")
            lines.append("Still owes:")
            if owing:
                for member, amount in owing.items():
                    lines.append(
                        f"  {member}: {format_amount(amount)} "
                        f"(paid {format_amount(group.paid(member))})"
                    )
            else:
                lines.append("  (nobody - week can be closed)")

    lines.append("")
    lines.append("Payout history:")
    if group.payouts:
        lines.extend(
            f"  Week {p.week}: {p.recipient} received GHS {format_amount(p.amount)}"
            for p in group.payouts
        )
    else:
        lines.append("  (no payouts yet)")

    return "\n".join(lines)
