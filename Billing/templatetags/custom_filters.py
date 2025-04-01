from django import template

register = template.Library()

@register.filter
def financial_year(date):
    """Returns the financial year in 'YYYY-YY' format based on the given date."""
    if not date:
        return ""

    year = date.year
    if date.month < 4:  # Before April, belongs to the previous financial year
        start_year = year - 1
    else:
        start_year = year

    return f"{start_year}-{str(start_year + 1)[-2:]}"  # Example: 2024-25
