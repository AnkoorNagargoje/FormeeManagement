from django import template

register = template.Library()

@register.filter
def get_month(created_at):
    return created_at.strftime('%B')

@register.filter
def is_month_changed(previous_date, current_date):
    return previous_date.month != current_date.month

