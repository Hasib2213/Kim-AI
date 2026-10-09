from app.finance.mortgage import mortgage_payment


def test_zero_interest():
    result = mortgage_payment(120000, 0, 10)
    assert result['monthly_payment'] == 1000
    assert result['total_interest'] == 0
