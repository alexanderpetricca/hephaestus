import datetime

import django_filters
from django.db.models import Q

from equipment.models import Item, EquipmentBooking


class EquipmentBookingFilter(django_filters.FilterSet):
    
    search = django_filters.CharFilter(method='custom_search_filter')
    date_range_start = django_filters.DateFilter(method='custom_date_range_start_filter')
    date_range_end = django_filters.DateFilter(method='custom_date_range_end_filter')


    class Meta:
        model = EquipmentBooking
        fields = [
            'status',
        ]


    def custom_search_filter(self, queryset, name, value):

        return queryset.filter(
            Q(job_reference__icontains=value)
        )
    

    def custom_date_range_start_filter(self, queryset, name, value):
        value = datetime.datetime.strptime(str(value), '%Y-%m-%d')
        
        return queryset.filter(
            Q(start_at__date__gte=value)
        ).distinct()


    def custom_date_range_end_filter(self, queryset, name, value):
        value = datetime.datetime.strptime(str(value), '%Y-%m-%d')

        return queryset.filter(
            Q(start_at__date__lte=value)
        ).distinct()


class ItemFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='custom_search_filter')
    quickfind = django_filters.CharFilter(method='custom_quickfind_filter')

    class Meta:
        model = Item
        fields = [
            'category',
            'manufacturer',
        ]


    def custom_search_filter(self, queryset, name, value):

        return queryset.filter(
            Q(barcode__iexact=value) |
            Q(name__icontains=value) |
            Q(category__name__icontains=value) |
            Q(manufacturer__name__iexact=value)
        )
    

    def custom_quickfind_filter(self, queryset, name, value):

        return queryset.filter(
            Q(category__name__icontains=value)
        )        