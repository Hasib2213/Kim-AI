def mortgage_payment(principal: float, annual_rate_percent: float, years: int) -> dict:
    if principal <= 0 or years <= 0 or annual_rate_percent < 0:
        raise ValueError('Invalid mortgage inputs')
    n = years * 12
    r = annual_rate_percent / 100 / 12
    payment = principal / n if r == 0 else principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total = payment * n
    return {'monthly_payment': round(payment, 2), 'total_payment': round(total, 2), 'total_interest': round(total - principal, 2), 'months': n}
