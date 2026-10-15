"""Command-line interface. Each command loads the group, acts, and saves it.

    python -m susu create 50.00
    python -m susu add Ama
    python -m susu pay Esi 30 [--week 1]
    python -m susu close
    python -m susu report
"""

import argparse
import sys
from pathlib import Path

from .errors import SusuError
from .group import SusuGroup
from .money import format_amount, parse_amount
from .report import build_report
from .storage import load, save

DEFAULT_FILE = "susu_state.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susu", description="Manage one rotating savings group (susu).")
    parser.add_argument(
        "--file", default=DEFAULT_FILE, help=f"where the group is saved (default: {DEFAULT_FILE})"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="create a new group")
    create.add_argument("amount", help="fixed weekly contribution in GHS, e.g. 50.00")
    create.add_argument("--force", action="store_true", help="overwrite an existing group")

    add = commands.add_parser("add", help="add a member (only before the first payment)")
    add.add_argument("name")

    pay = commands.add_parser("pay", help="record a full or partial contribution")
    pay.add_argument("name")
    pay.add_argument("amount", help="amount in GHS, e.g. 20 or 12.50")
    pay.add_argument("--week", type=int, help="week being paid for (default: current week)")

    commands.add_parser("close", help="close the current week and pay out if everyone has paid")
    commands.add_parser("report", help="show current week, who has paid, who owes and payouts")
    return parser


def run(args) -> str:
    path = Path(args.file)

    if args.command == "create":
        if path.exists() and not args.force:
            raise SusuError(f"A group already exists at {path}. Use --force to replace it.")
        group = SusuGroup(args.amount)
        save(group, path)
        return f"Created group with weekly contribution GHS {format_amount(group.weekly_amount)}"

    group = load(path)

    if args.command == "add":
        name = group.add_member(args.name)
        message = f"Added {name} (position {len(group.members)} in payout order)"
    elif args.command == "pay":
        member = group.resolve_member(args.name)
        owed = group.record_contribution(member, args.amount, week=args.week)
        status = "paid in full" if owed == 0 else f"still owes {format_amount(owed)}"
        message = (
            f"Recorded {format_amount(parse_amount(args.amount))} from {member} for week "
            f"{group.current_week} (total {format_amount(group.paid(member))}); {status}"
        )
    elif args.command == "close":
        result = group.close_week()
        message = result.message()
        if result.closed and not group.is_complete:
            message += f"\nWeek {group.current_week} begins; {group.next_recipient} is next."
        elif result.closed:
            message += "\nCycle complete: every member has received the pot."
    else:  # report
        return build_report(group)

    save(group, path)
    return message


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(run(args))
    except SusuError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
