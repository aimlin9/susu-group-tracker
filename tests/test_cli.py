import pytest

from susu.cli import main


@pytest.fixture
def susu(tmp_path, capsys):
    """Run a CLI command against a temp state file; return (exit code, stdout, stderr)."""
    state = str(tmp_path / "state.json")

    def run(*args):
        code = main(["--file", state, *args])
        out, err = capsys.readouterr()
        return code, out.strip(), err.strip()

    return run


def test_cli_spec_example_end_to_end(susu):
    assert susu("create", "50.00")[0] == 0
    for name in ["Ama", "Kofi", "Esi"]:
        assert susu("add", name)[0] == 0
    susu("pay", "Ama", "50")
    susu("pay", "Kofi", "50")
    susu("pay", "Esi", "30")

    code, out, _ = susu("close")
    assert code == 0
    assert out == "Week 1 cannot close: Esi owes 20.00"

    susu("pay", "Esi", "20")
    code, out, _ = susu("close")
    assert "Week 1 closed: Ama receives 150.00" in out
    assert "Week 2 begins; Kofi is next." in out

    code, out, _ = susu("report")
    assert "Current week: 2" in out
    assert "Week 1: Ama received GHS 150.00" in out


def test_cli_reports_errors_with_exit_code_1(susu):
    susu("create", "50")
    susu("add", "Ama")
    code, _, err = susu("pay", "Yaw", "10")
    assert code == 1
    assert err == "Error: Unknown member 'Yaw'"

    code, _, err = susu("pay", "Ama", "60")
    assert code == 1
    assert "only owes 50.00" in err


def test_cli_refuses_to_overwrite_existing_group(susu):
    susu("create", "50")
    code, _, err = susu("create", "20")
    assert code == 1
    assert "already exists" in err
    assert susu("create", "20", "--force")[0] == 0


def test_cli_commands_need_a_group_first(susu):
    code, _, err = susu("report")
    assert code == 1
    assert "Create one first" in err
