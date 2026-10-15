import json

import pytest

from susu import SusuGroup
from susu.errors import StorageError
from susu.storage import load, save


def test_save_and_load_round_trip(tmp_path):
    g = SusuGroup("50.50")
    for name in ["Ama", "Kofi", "Esi"]:
        g.add_member(name)
    for name in g.members:
        g.record_contribution(name, "50.50")
    g.close_week()
    g.record_contribution("Esi", "0.01")

    path = tmp_path / "group.json"
    save(g, path)
    loaded = load(path)

    assert loaded.weekly_amount == 5050
    assert loaded.members == ["Ama", "Kofi", "Esi"]
    assert loaded.current_week == 2
    assert loaded.paid("Esi") == 1
    assert [(p.week, p.recipient, p.amount) for p in loaded.payouts] == [(1, "Ama", 15150)]


def test_load_missing_file(tmp_path):
    with pytest.raises(StorageError):
        load(tmp_path / "nope.json")


def test_load_rejects_tampered_file(tmp_path):
    g = SusuGroup("50")
    g.add_member("Ama")
    path = tmp_path / "group.json"
    save(g, path)

    data = json.loads(path.read_text())
    data["paid_pesewas"] = {"Ama": 999999}  # more than the weekly amount
    path.write_text(json.dumps(data))

    with pytest.raises(StorageError):
        load(path)
