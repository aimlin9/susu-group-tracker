from susu import SusuGroup
from susu.report import build_report


def make_group():
    g = SusuGroup("50.00")
    for name in ["Ama", "Kofi", "Esi"]:
        g.add_member(name)
    return g


def test_report_shows_paid_owing_and_week():
    g = make_group()
    g.record_contribution("Ama", "50")
    g.record_contribution("Esi", "30")

    report = build_report(g)

    assert "Current week: 1" in report
    assert "Next payout: Ama receives GHS 150.00" in report
    assert "Paid in full:\n  Ama\n" in report
    assert "  Kofi: 50.00 (paid 0.00)" in report
    assert "  Esi: 20.00 (paid 30.00)" in report
    assert "(no payouts yet)" in report


def test_report_includes_payout_history():
    g = make_group()
    for name in g.members:
        g.record_contribution(name, "50")
    g.close_week()

    report = build_report(g)

    assert "Current week: 2" in report
    assert "Week 1: Ama received GHS 150.00" in report
    assert "Next payout: Kofi receives GHS 150.00" in report


def test_report_for_completed_cycle():
    g = SusuGroup("20")
    g.add_member("Ama")
    g.record_contribution("Ama", "20")
    g.close_week()

    report = build_report(g)

    assert "Cycle complete" in report
    assert "Week 1: Ama received GHS 20.00" in report


def test_report_for_empty_group():
    assert "No members yet." in build_report(SusuGroup("50"))
