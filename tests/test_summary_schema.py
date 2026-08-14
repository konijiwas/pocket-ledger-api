from app.schemas.summary import SummaryRead


def test_summary_read_accepts_totals() -> None:
    summary = SummaryRead(
        income_total="5000.00",
        expense_total="1250.50",
        balance="3749.50",
    )

    assert str(summary.income_total) == "5000.00"
    assert str(summary.expense_total) == "1250.50"
    assert str(summary.balance) == "3749.50"