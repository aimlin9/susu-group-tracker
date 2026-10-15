"""Save and load a SusuGroup as JSON so the CLI keeps state between runs.

Amounts are stored as whole pesewas (integers), so nothing is lost or
rounded on the way to and from disk.
"""

import json
from pathlib import Path

from .errors import StorageError, SusuError
from .group import SusuGroup
from .models import Payout
from .money import format_amount

FORMAT_VERSION = 1


def to_dict(group: SusuGroup) -> dict:
    return {
        "version": FORMAT_VERSION,
        "weekly_amount_pesewas": group.weekly_amount,
        "members": group.members,
        "current_week": group.current_week,
        "paid_pesewas": {m: group.paid(m) for m in group.members if group.paid(m)},
        "payouts": [
            {"week": p.week, "recipient": p.recipient, "amount_pesewas": p.amount}
            for p in group.payouts
        ],
    }


def from_dict(data: dict) -> SusuGroup:
    """Rebuild a group by replaying its history through the public API.

    Replaying (instead of setting fields directly) means a hand-edited or
    corrupted file is checked by the same rules as live input.
    """
    try:
        if data.get("version") != FORMAT_VERSION:
            raise StorageError(f"Unsupported file version {data.get('version')!r}")
        group = SusuGroup(format_amount(int(data["weekly_amount_pesewas"])))
        for name in data["members"]:
            group.add_member(name)
        week_amount = format_amount(group.weekly_amount)
        for _ in data["payouts"]:
            for member in group.members:
                group.record_contribution(member, week_amount)
            group.close_week()
        for member, pesewas in data["paid_pesewas"].items():
            group.record_contribution(member, format_amount(int(pesewas)))
    except StorageError:
        raise
    except (KeyError, TypeError, ValueError, SusuError) as exc:
        raise StorageError(f"Saved group file is invalid: {exc}") from None

    saved = [(p["week"], p["recipient"], p["amount_pesewas"]) for p in data["payouts"]]
    rebuilt = [(p.week, p.recipient, p.amount) for p in group.payouts]
    if saved != rebuilt or data["current_week"] != group.current_week:
        raise StorageError("Saved group file is invalid: payout history does not match members")
    return group


def save(group: SusuGroup, path: Path) -> None:
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(to_dict(group), indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic swap so a crash never leaves a half-written file


def load(path: Path) -> SusuGroup:
    path = Path(path)
    if not path.exists():
        raise StorageError(f"No group found at {path}. Create one first with: create <amount>")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StorageError(f"Could not read {path}: {exc}") from None
    return from_dict(data)
