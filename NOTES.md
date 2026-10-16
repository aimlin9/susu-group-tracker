# Notes

## Assumptions

Rules the brief does not cover, and what the program does:

1. **Members can only be added before the first contribution.** Once any money is
   recorded, the member list (and so the payout order) is locked. Adding someone
   mid-cycle would change the pot size and break the "everyone pays everyone" fairness
   of a susu, so a new member waits for a new group.
2. **Only the current week accepts payments.** Paying for a past week is not possible
   because a week only closes once it is fully paid. Paying ahead for a future week is
   rejected to keep the records simple; a member who wants to pay ahead can pay once
   the week opens.
3. **One cycle per group.** With N members there are N weeks. After everyone has
   received the pot once, the cycle is complete and further payments or closes are
   rejected.
4. **Member names are unique ignoring case and surrounding spaces.** "Ama", "ama" and
   " Ama " are the same person. The spelling used when the member was added is the one
   shown in reports. Blank names are rejected.
5. **Amounts have at most 2 decimal places** (1 pesewa = GHS 0.01). `10.005` is rejected
   rather than rounded, because silently changing someone's payment is worse than
   asking them to re-enter it.
6. **A week that cannot close is not an error.** Closing with money outstanding leaves
   everything unchanged and lists every member who still owes, in join order.
7. **A group with no members cannot close a week.**
8. **Creating a group refuses to overwrite an existing saved group** unless `--force`
   is given, to avoid wiping real records by accident.

## Decisions

- **Language: Python**, standard library only, so it runs anywhere with Python 3.10+.
- **Exact money:** all amounts are stored and added as integer pesewas. Input is parsed
  with `Decimal`, never `float` (floats are rejected outright, since `0.1 + 0.2 != 0.3`).
  Formatting back to `150.00` is done with integer division, so no rounding happens
  anywhere.
- **Domain logic is separate from input/output.** `SusuGroup` knows nothing about the
  command line or files; `cli.py`, `report.py` and `storage.py` sit on top of it. This
  keeps the rules easy to test directly, and a small API could reuse the same class.
- **One exception class per rule** (`UnknownMemberError`, `OverpaymentError`, ...), all
  subclasses of `SusuError`. The CLI catches `SusuError` and prints the message; tests
  check the specific type.
- **Rejected actions change nothing.** Every check runs before any state is modified.
- **CLI with a JSON state file** rather than an interactive menu: each command is one
  line, which is easy to script, test and demonstrate. Writes go to a temporary file
  that is then swapped in, so a crash cannot leave a half-written file.
- **Loading replays history through the public API** instead of writing fields directly.
  A hand-edited or corrupted file is checked by the same rules as live input (e.g. a
  saved payment larger than the weekly amount is rejected on load).

## What I would improve with more time

- Keep a full payment log (who paid what, when) instead of only running totals, so
  every contribution can be audited and an incorrect payment can be reversed.
- Support several groups and multiple cycles, with an option to start a new cycle with
  the same members.
- Handle real-world situations: a member dropping out, swapping payout positions,
  penalties for late payment, or allowing payment in advance.
- A small HTTP API (e.g. FastAPI) on top of the same `SusuGroup` class.
- Store state in SQLite with transactions instead of a JSON file, which would also
  make concurrent use safe.
- Add type checking (mypy) and linting (ruff) to the GitHub Actions workflow.

## References

- Python `decimal` module, for exact parsing of amounts:
  https://docs.python.org/3/library/decimal.html
- Python tutorial, "Floating-Point Arithmetic: Issues and Limitations", on why floats
  are unsafe for money: https://docs.python.org/3/tutorial/floatingpoint.html
- `argparse` subcommands, for the CLI: https://docs.python.org/3/library/argparse.html
- pytest fixtures, `tmp_path` and `capsys`, used in the storage and CLI tests:
  https://docs.pytest.org/en/stable/how-to/fixtures.html
- GitHub Actions Python workflow guide:
  https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python
- Background on how susu groups work: rotating savings and credit associations (ROSCAs),
  https://en.wikipedia.org/wiki/Rotating_savings_and_credit_association
