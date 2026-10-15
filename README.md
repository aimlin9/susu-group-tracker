# Susu Group Tracker

A small Python command-line program that manages one rotating savings group (susu).
Every member pays the same fixed amount each week; each week the whole pot goes to
one member, in the order they joined.

## Requirements

- Python 3.10 or newer
- pytest (only for running the tests)

No other dependencies. The program uses only the Python standard library.

## Running the program

From the project folder:

```
python -m susu create 50.00        # create a group with a weekly contribution of GHS 50.00
python -m susu add Ama             # add members (payout order = join order)
python -m susu add Kofi
python -m susu add Esi
python -m susu pay Ama 50          # record a contribution for the current week
python -m susu pay Esi 30          # partial payments are allowed
python -m susu pay Esi 20 --week 1 # --week is optional; only the open week is accepted
python -m susu close               # close the week: pay out, or report who still owes
python -m susu report              # current week, who has paid, who owes, payout history
python -m susu --help              # all commands and options
```

The group is saved to `susu_state.json` in the current folder after every command,
so state carries over between runs. Use `--file PATH` (before the command) to work
with a different file, e.g. `python -m susu --file club.json report`.

### Example (the scenario from the brief)

```
> python -m susu create 50.00
Created group with weekly contribution GHS 50.00
> python -m susu add Ama
> python -m susu add Kofi
> python -m susu add Esi
> python -m susu pay Ama 50
> python -m susu pay Kofi 50
> python -m susu pay Esi 30
Recorded 30.00 from Esi for week 1 (total 30.00); still owes 20.00
> python -m susu close
Week 1 cannot close: Esi owes 20.00
> python -m susu pay Esi 20
Recorded 20.00 from Esi for week 1 (total 50.00); paid in full
> python -m susu close
Week 1 closed: Ama receives 150.00
Week 2 begins; Kofi is next.
```

Invalid input prints `Error: <reason>` and exits with code 1, for example
`Error: Unknown member 'Yaw'` or `Error: Esi only owes 20.00 for week 1, cannot pay 25.00`.

## Running the tests

```
pip install pytest
python -m pytest
```

The tests cover money parsing, members, contributions (including partial payments
and overpayment), closing a week (including the "week cannot close" case and the full
example above), the report, saving/loading, and the CLI end to end.

## Project layout

```
susu/
  money.py     exact money: amounts stored as integer pesewas, parsed via Decimal
  errors.py    one exception type per rule violation (all subclass SusuError)
  group.py     SusuGroup: members, contributions, closing weeks, payout rotation
  models.py    Payout and CloseResult records
  report.py    plain-text report
  storage.py   save/load the group as JSON
  cli.py       argparse command-line interface
tests/         pytest test suite
NOTES.md       assumptions, decisions and future improvements
```
