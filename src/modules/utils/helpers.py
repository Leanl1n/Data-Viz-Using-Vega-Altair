"""Utility helpers for formatting and display."""


def format_number(num: int | float) -> str:
    """Format large numbers with K/M/B/T suffix."""
    if num >= 1e12:
        return f"{num / 1e12:.2f}T"
    if num >= 1e9:
        return f"{num / 1e9:.2f}B"
    if num >= 1e6:
        return f"{num / 1e6:.2f}M"
    if num >= 1e3:
        return f"{num / 1e3:.2f}K"
    return f"{num:.2f}"
