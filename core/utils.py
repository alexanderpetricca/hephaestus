from datetime import timedelta

from django.utils import timezone, dateformat


def get_date_periods():
    """
    Returns dict of assorted useful dates.
    """

    today = timezone.now().date()
    yesterday = dateformat.format(today - timedelta(1), 'Y-m-d')
    base_date = dateformat.format(today, 'Y-m-d').split('-')
    current_week = today.isocalendar()
    
    week_start = dateformat.format(today.fromisocalendar(current_week[0], current_week[1], 1), 'Y-m-d')
    week_end = dateformat.format(today.fromisocalendar(current_week[0], current_week[1], 7), 'Y-m-d')
    last_week_start = dateformat.format(today - timedelta(days=today.weekday() + 7), 'Y-m-d')
    last_week_end = dateformat.format(today - timedelta(days=today.weekday() + 1), 'Y-m-d')
    
    month_start = f'{base_date[0]}-{base_date[1]}-01'
    next_month = today.replace(day=28) + timedelta(days=4)
    month_end = dateformat.format(next_month - timedelta(days=next_month.day), 'Y-m-d')
    
    year_start = f'{base_date[0]}-01-01'

    date_periods = {
        'today': dateformat.format(today, 'Y-m-d'),  
        'yesterday': yesterday, 
        'week_start': week_start,
        'week_end': week_end,
        'last_week_start': last_week_start,
        'last_week_end': last_week_end,        
        'month_start': month_start,
        'month_end': month_end,
        'year_start': year_start,
    }

    return date_periods


def convert_duration_to_hours(days, seconds):
    """
    Converts days and seconds to hours.
    """
    
    hours = (days * 24) + seconds / 3600
    return hours