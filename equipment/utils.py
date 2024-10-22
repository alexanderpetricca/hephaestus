from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from equipment.models import Category, Manufacturer, EquipmentBooking


def get_cached_equipment_filterables() -> dict:
    """
    Returns dictionary of equipment data filterables, from cache.
    """

    timeout_period = 60*60*24 #1 day, in mins

    all_equipment_categories = cache.get('all_equipment_categories')
    if not all_equipment_categories:
        all_equipment_categories = Category.objects.all()
        cache.set('all_equipment_categories', all_equipment_categories, timeout=timeout_period) 

    all_equipment_manufacturers = cache.get('all_equipment_manufacturers')
    if not all_equipment_manufacturers:
        all_equipment_manufacturers = Manufacturer.objects.all()
        cache.set('all_equipment_manufacturers', all_equipment_manufacturers, timeout=timeout_period)

    filterable_data = {
        'categories': all_equipment_categories,
        'manufacturers': all_equipment_manufacturers,
    }

    return filterable_data


def has_pending_booking(user):
    """
    Returns pending booking if the user has one, or None if not.
    """

    try:
        has_pending_booking = EquipmentBooking.objects.get(
            created_by=user,
            status='PENDING'
        )

    except ObjectDoesNotExist:
        has_pending_booking = None

    return has_pending_booking