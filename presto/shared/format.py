# format.py
# Defines project-widt conventions for turning raw values into user-facing formatted text

import numbers

def describe_number(number) -> str:
    """
    Given a potentially numeric value, output a user-facing string representing the value.

    Examples:
    1_234_567 -> '1.2M'
    1_250 -> '1.3K'
    0.12345678 -> '0.12'
    '1.234' -> '1.234' (only numbers are converted)
    """
    if not isinstance(number, numbers.Real):
        return number
    if number >= 1_000_000:
        return f'{number/1_000_000:.1f}M'
    if number >= 10_000:
        return f'{round(number/1_000)}K'
    if number >= 1_000:
        return f'{number/1_000:.1f}K'
    if number < 0.1:
        return str(number)
    # value is between 0.1 and 1_000
    if type(number) == int:
        return str(number)
    return f'{number:.2f}'

def to_percent(rate) -> str:
    """
    Given a rate between 0 and 1, output a user-facing percentage string.

    Examples:
    1.0 -> '100%'
    0.111 -> '11%'
    0.0111 -> '1.1%' 
    """
    if not isinstance(rate, numbers.Real):
        return rate  
    pct = rate * 100
    # output whole percentages after 10% (rounded up)
    if pct >= 9.95:
        return f'{round(pct):,d}%'
    # special case: very small numbers
    if pct == 0:
        return '0%'
    if pct < 0.05:
        return '~0%'
    # single-digit percentages: output one decimal
    return f'{pct:.1f}%'