import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import math

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import (
    Value, 
    BooleanField, 
    OuterRef, 
    Case, 
    When, 
    Exists, 
    Sum,
    F,
    ExpressionWrapper,
    FloatField
)
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Item, EquipmentBooking, EquipmentBookingItem
from . import filters
from . import forms
from .utils import get_cached_equipment_filterables, has_pending_booking
from core.utils import get_date_periods, convert_duration_to_hours


@login_required
@permission_required('equipment.view_item', raise_exception=True)
def equipment_dashboard_view(request):

    today = timezone.now().date()

    todays_bookings = EquipmentBooking.objects.select_related('created_by'
    ).filter(
        start_at__date=today,
        status='CONFIRMED',
        cancelled=False,
    ).order_by('start_at')[0:10]

    recent_bookings = EquipmentBooking.objects.select_related('created_by'
        ).filter(status='CONFIRMED').order_by('-created_at')[0:10]

    context = {
        'pending_booking': has_pending_booking(request.user),
        'todays_bookings': todays_bookings,
        'recent_bookings': recent_bookings,
        'module': 'dashboard',
    }
    context.update(get_cached_equipment_filterables())
    context.update(get_date_periods())

    return render(request, 'equipment/dashboard.html', context)


@login_required
@permission_required('equipment.view_item', raise_exception=True)
def item_query_view(request):
    """
    Query / search all equipment.
    """    

    pending_booking = has_pending_booking(request.user)

    if pending_booking:
        booking_start = pending_booking.start_at
        booking_end = pending_booking.end_at
        
        # Subquery to check if the item is booked during the current active booking period
        booked_items_subquery = EquipmentBookingItem.objects.filter(
            item=OuterRef('pk'),
            equipment_booking__start_at__lt=booking_end,
            equipment_booking__end_at__gt=booking_start,
            equipment_booking__status__in=['PENDING', 'CONFIRMED'],
        )

        # Annotate the queryset with availability status
        items = Item.objects.select_related('manufacturer', 'category', 'assigned_to'
            ).filter(deleted=False
            ).annotate(
                available=Case(
                    When(
                        Exists(booked_items_subquery), then=Value(False)  # Mark as unavailable if booked
                    ),
                    When(
                        assigned_to__isnull=False, then=Value(False)  # Mark as unavailable if assigned
                    ),
                    default=Value(True),  # Otherwise, mark as available
                    output_field=BooleanField()
                )
            ).order_by('created_at')
    else:
        # If no active booking exists, set all items as available
        items = Item.objects.select_related('manufacturer', 'category', 'assigned_to'
            ).filter(deleted=False
            ).annotate(
                available=Case(
                    When(assigned_to__isnull=True, then=Value(True)),  # Available if not assigned
                    default=Value(False),  # Unavailable if assigned
                    output_field=BooleanField()
                )
            ).order_by('created_at')
        
    equipment_filter = filters.ItemFilter(request.GET, queryset=items)

    paginator = Paginator(equipment_filter.qs, 40)
    page = request.GET.get('page')

    try:
        item_query = paginator.page(page)
    except PageNotAnInteger:
        item_query = paginator.page(1)
    except EmptyPage:
        item_query = paginator.page(paginator.num_pages)     

    context = {
        'item_query': item_query,
        'pending_booking': pending_booking,
        'module': 'equipment',
    }
    context.update(get_cached_equipment_filterables())
    context.update(get_date_periods())

    return render(request, 'equipment/item-query.html', context)


@login_required
@permission_required('equipment.view_item', raise_exception=True)
def item_detail_view(request, pk):

    item = get_object_or_404(
        Item.objects.select_related(
            'created_by',
            'updated_by',
            'assigned_to', 
            'category', 
            'manufacturer',
        ), 
        id=pk,
    )
    item.depreciated_value = round(item.calculate_depreciation(), 2)

    now = timezone.now()
    upcoming_bookings = EquipmentBooking.objects.select_related('created_by'
        ).filter(
            booking_items__item=item,
            start_at__gte=now, 
            status='CONFIRMED'
        ).order_by('start_at')

    context = {
        'item': item,
        'upcoming_bookings': upcoming_bookings,
        'module': 'equipment',
    }

    return render(request, 'equipment/item-detail.html', context)



@login_required
@permission_required('equipment.add_item', raise_exception=True)
def create_item_view(request):
    
    form = forms.CreateUpdateItemForm()

    if request.method == 'POST':
        form = forms.CreateUpdateItemForm(request.POST)

        if form.is_valid():
            new_item = form.save(commit=False)

            if new_item.last_service_date and new_item.service_interval_period:
                new_item.service_due_date = new_item.last_service_date + new_item.service_interval_period

            new_item.save()

            messages.success(request, 'Successfully created new item.')
            return redirect(reverse('equipment_dashboard'))

    context = {
        'form': form,
        'module': 'equipment',
    }
    return render(request, 'equipment/create-item.html', context)


@login_required
@permission_required('equipment.change_item', raise_exception=True)
def update_item_view(request, pk):
    
    item = get_object_or_404(Item, id=pk)

    form = forms.CreateUpdateItemForm(instance=item)

    if request.method == 'POST':
        form = forms.CreateUpdateItemForm(request.POST, instance=item)

        if form.is_valid():
            new_item = form.save(commit=False)

            if new_item.last_service_date and new_item.service_interval_period:
                new_item.service_due_date = new_item.last_service_date + new_item.service_interval_period

            new_item.save()

            messages.success(request, 'Successfully updated item.')
            next = request.GET.get('next', reverse('equipment_dashboard'))
            return redirect(next)

    context = {
        'form': form,
        'item': item,
        'module': 'equipment',
    }
    return render(request, 'equipment/update-item.html', context)


@login_required
@permission_required('equipment.delete_item', raise_exception=True)
def delete_item_view(request, pk):
    
    item = get_object_or_404(Item, id=pk)

    if request.method == 'POST':
        
        item.soft_delete()
        
        messages.success(request, 'Successfully deleted item.')
        next = request.GET.get('next', reverse('equipment_dashboard'))
        return redirect(next)

    context = {
        'item': item,
        'module': 'equipment',
    }
    return render(request, 'equipment/delete-item.html', context)


@login_required
@permission_required('equipment.assign_item', raise_exception=True)
def assign_item_view(request, pk):
    
    item = get_object_or_404(Item, id=pk)

    # Check for conflicting bookings
    conflicting_bookings = EquipmentBookingItem.objects.filter(
        item=item,
        equipment_booking__start_at__gte=timezone.now(),
        equipment_booking__status__in=['PENDING', 'CONFIRMED'],
    )

    if conflicting_bookings.exists():
        messages.error(request, 'This item appears in an upcoming booking, and cannot currently be assigned.')
        next = request.GET.get('next', reverse('equipment_dashboard'))
        return redirect(next)
    
    else:
        form = forms.AssignItemForm()

        if request.method == 'POST':

            form = forms.AssignItemForm(request.POST)
            
            if form.is_valid():

                user = form.cleaned_data.get('assigned_user')
                item.assign_item(user)

                messages.success(request, 'Successfully assigned item.')
                next = request.GET.get('next', reverse('equipment_dashboard'))
                return redirect(next)

        context = {
            'form': form,
        }

        return render(request, 'equipment/assign-item.html', context)


@login_required
@permission_required('equipment.assign_item', raise_exception=True)
def unassign_item_view(request, pk):
    
    item = get_object_or_404(Item, id=pk)

    if request.method == 'POST':
        item.unassign_item()
        
        messages.success(request, 'Successfully unassigned item.')
        next = request.GET.get('next', reverse('equipment_dashboard'))
        return redirect(next)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
@permission_required('equipment.change_item', raise_exception=True)
def update_item_service_view(request, pk):
    
    item = get_object_or_404(Item, id=pk)
    form = forms.UpdateItemServiceDateForm()

    if request.method == 'POST':

        form = forms.UpdateItemServiceDateForm(request.POST, instance=item)

        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated item.')
            next = request.GET.get('next', reverse('equipment_dashboard'))
            return redirect(next)

    context = {
        'form': form,
        'item': item,
    }

    return render(request, 'equipment/update-item-service.html', context)

@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def add_to_booking_view(request, pk):
    
    if request.method == 'POST':
        
        # Predefine next url so it can be used in both success and error blocks
        next = request.POST.get('next', reverse('equipment_item_query'))
        
        try:            
            pending_booking = EquipmentBooking.objects.get(
                created_by=request.user, 
                status='PENDING'
            )

            booking_start = pending_booking.start_at
            booking_end = pending_booking.end_at

            item = get_object_or_404(Item, id=pk)

            if not item.assigned_to and not EquipmentBookingItem.objects.filter(
                item=item,
                equipment_booking__start_at__lt=booking_end,
                equipment_booking__end_at__gt=booking_start,
                equipment_booking__status='CONFIRMED',
            ).exists():
                booking_item, created = EquipmentBookingItem.objects.get_or_create(
                    equipment_booking=pending_booking,
                    item=item,
                )
            else:
                messages.error(request, 'This item cannot currently be booked.')

            return redirect(next)

        except ObjectDoesNotExist:
            return redirect(f"{reverse('equipment_booking_summary')}?next={next}")

    else:
        return HttpResponseNotAllowed(['POST'])
    

@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def remove_from_booking_view(request, pk):
    
    if request.method == 'POST':

        open_booking = request.POST.get('open_booking')
        booking_item = get_object_or_404(
            EquipmentBookingItem, 
            equipment_booking=open_booking,
            id=pk,
        )
        booking_item.delete()
        return redirect(reverse('equipment_booking_summary'))

    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def booking_summary_view(request):
    """
    Allows users to view their current pending booking, or if they do not 
    have one, create one.
    """

    try:
        pending_booking = EquipmentBooking.objects.get(
            created_by=request.user, 
            status='PENDING'
        )

        booking_start = pending_booking.start_at
        booking_end = pending_booking.end_at
        
        # Subquery to check if the item is booked during the current active booking period
        booked_items_subquery = EquipmentBookingItem.objects.filter(
            item=OuterRef('item__pk'),
            equipment_booking__start_at__lt=booking_end,
            equipment_booking__end_at__gt=booking_start,
            equipment_booking__status='CONFIRMED'
        )
        
        booking_items = EquipmentBookingItem.objects.select_related(
            'item', 
            'item__manufacturer', 
            'item__category'
            ).filter(
                equipment_booking=pending_booking,
            ).annotate(
                available=Case(
                    When(
                        Exists(booked_items_subquery), then=Value(False)  # Mark as unavailable if booked
                    ),
                    default=Value(True),  # Otherwise, mark as available
                    output_field=BooleanField()
                )
        ).order_by('created_at')
        
        form = None

    except ObjectDoesNotExist:
        pending_booking = None
        booking_items = None
        form = forms.CreateUpdateBookingForm()

        if request.method == 'POST':
            form = forms.CreateUpdateBookingForm(request.POST)

            if form.is_valid():
                new_booking = form.save(commit=False)
                new_booking.created_by = request.user
                new_booking.save()

                return redirect(reverse('equipment_item_query'))

    context = {
        'pending_booking': pending_booking,
        'booking_items': booking_items,
        'form': form,
        'module': 'summary',
    }
    context.update(get_cached_equipment_filterables())
    context.update(get_date_periods())
    
    return render(request, 'equipment/booking-summary.html', context)


@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def booking_summary_confirm_view(request):
    """
    Allows the user to confirm a booking from the booking summary page.
    """    

    pending_booking = get_object_or_404(
        EquipmentBooking, 
        created_by=request.user, 
        status='PENDING',
    )

    try:
        if pending_booking.verify_booking():
            if request.method == 'POST':
                pending_booking.confirm()
                messages.success(request, 'Your booking has been successfully created.')
                return redirect(reverse('equipment_dashboard')) 

            context = {
                'pending_booking': pending_booking,
            }

            return render(request, 'equipment/booking-confirm.html', context)                           

    except ValidationError as e:

        errors = ', '.join(e)

        messages.error(request, errors)
        return redirect(reverse('equipment_booking_summary'))        


@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def booking_summary_cancel_view(request):
    """
    Allows the user to cancel an unconfirmed booking from the booking summary 
    page.
    """
    
    booking = get_object_or_404(
        EquipmentBooking, 
        created_by=request.user, 
        status='PENDING',
    )

    if request.method == 'POST':

        # If booking has confirmed == True (it's already been confirmed), 
        # then cancel, otherwise delete (unconfirmed bookings.)
        if booking.confirmed:
            booking.cancel()
        else:
            booking.delete()
        messages.success(request, 'Booking successfully cancelled.')
        return redirect(reverse('equipment_dashboard'))

    context = {
        'booking': booking,
    }

    return render(request, 'equipment/booking-cancel.html', context)


@login_required
@permission_required('equipment.change_equipmentbooking', raise_exception=True)
def booking_update_view(request, pk):

    open_pending_bookings = EquipmentBooking.objects.filter(
        created_by=request.user, 
        status='PENDING'
    )

    if not open_pending_bookings.exists():

        booking = get_object_or_404(EquipmentBooking, id=pk)

        if booking.start_at > timezone.now():
            booking.revert_to_pending()
            return redirect(reverse('equipment_booking_summary'))
        else:
            error = 'Bookings cannot be updated if they occurred in the past.'

    else:
        error = 'You cannot update a booking whilst you have one outstanding.'

    messages.error(request, error)
    next = request.GET.get('next', reverse('equipment_dashboard'))
    return redirect(next)


@login_required
@permission_required('equipment.change_equipmentbooking', raise_exception=True)
def booking_update_meta_view(request, pk):
    
    booking = get_object_or_404(EquipmentBooking, id=pk, created_by=request.user, status='PENDING')
    
    if request.method == 'POST':
        form = forms.CreateUpdateBookingForm(request.POST, instance=booking)

        if form.is_valid():
            form.save()
            messages.success(request, 'Booking details successfully updated.')
            return redirect('equipment_booking_summary')
        
    # Format the start and date for the widgets, and convert to local time.
    booking.start_at = timezone.localtime(booking.start_at).strftime('%Y-%m-%dT%H:%M')
    booking.end_at = timezone.localtime(booking.end_at).strftime('%Y-%m-%dT%H:%M')
    form = forms.CreateUpdateBookingForm(instance=booking)

    context = {
        'form': form,
        'booking': booking,
    }

    return render(request, 'equipment/booking-update-meta.html', context)


@login_required
@permission_required('equipment.add_equipmentbooking', raise_exception=True)
def booking_cancel_view(request, pk):
    """
    Allows user to cancel a booking.
    """
    
    booking = get_object_or_404(EquipmentBooking, id=pk)

    if request.method == 'POST':
        booking.cancel()
        messages.success(request, 'Booking successfully cancelled.')
        return redirect(reverse('equipment_dashboard'))        

    context = {
        'booking': booking,
    }

    return render(request, 'equipment/booking-cancel.html', context)


@login_required
@permission_required('equipment.view_equipmentbooking', raise_exception=True)
def booking_query_view(request):
    """
    Query / search all bookings.
    """

    bookings = EquipmentBooking.objects.select_related(
        'created_by',
        ).all().exclude(status='PENDING').order_by('-start_at', 'created_at')

    booking_filter = filters.EquipmentBookingFilter(request.GET, queryset=bookings)

    paginator = Paginator(booking_filter.qs, 40)
    page = request.GET.get('page')

    try:
        booking_query = paginator.page(page)
    except PageNotAnInteger:
        booking_query = paginator.page(1)
    except EmptyPage:
        booking_query = paginator.page(paginator.num_pages)       

    pending_booking = has_pending_booking(request.user)

    context = {
        'booking_query': booking_query,
        'pending_booking': pending_booking,
        'module': 'bookings',
    }
    context.update(get_date_periods())
    context.update(get_cached_equipment_filterables())

    return render(request, 'equipment/booking-query.html', context)


@login_required
@permission_required('equipment.view_equipmentbooking', raise_exception=True)
def booking_calendar_view(request):

    period = request.GET.get('period')
    
    if period:
        target_year, target_month = map(int, period.split('-'))
    else:
        target_year = datetime.now().year
        target_month = datetime.now().month

    # Create a Calendar object
    cal = calendar.Calendar()

    today = datetime.now().date()

    # Get the weeks of the current month (as lists of day numbers)
    month_weeks = cal.monthdayscalendar(target_year, target_month)

    # Fetch bookings that occur within the target month
    bookings = EquipmentBooking.objects.filter(start_at__year=target_year, start_at__month=target_month, status="CONFIRMED")

    # Organize bookings into a set of days for fast lookup
    booking_days = {booking.start_at.day for booking in bookings}

    # Initialize the month dictionary to store weeks and days
    month_obj = {}

    # Iterate over the weeks, building the month dictionary
    for counter, week in enumerate(month_weeks, start=1):
        week_days = {
            f'week_{counter}': {
                day_num: {
                    'day': day,
                    'date': (day_date := date(target_year, target_month, day)).strftime('%Y-%m-%d') if day != 0 else None,  # Include full date
                    'has_booking': day in booking_days and day != 0,  # Mark if the day has a booking
                    'is_today': day_date == today if day != 0 else False  # Check if the date is today
                }
                for day_num, day in enumerate(week, start=1)  # Start from 1 for weekday numbering
            }
        }
        month_obj.update(week_days)


    # Calculate previous and next months
    current_date = date(target_year, target_month, 1)
    next_month_date = current_date + relativedelta(months=1)
    prev_month_date = current_date - relativedelta(months=1)

    # Format the previous and next months as 'YYYY-MM' for URL or form usage
    prev_month = prev_month_date.strftime('%Y-%m')
    next_month = next_month_date.strftime('%Y-%m')

    pending_booking = has_pending_booking(request.user)     

    context = {
        'pending_booking': pending_booking,
        'month_obj': month_obj,
        'month_name': calendar.month_name[target_month],
        'year_name': target_year,
        'current_month_start': current_date.strftime('%Y-%m-%d'),
        'next_month_start': next_month,
        'prev_month_start': prev_month,
        'module': 'calendar',
    }

    return render(request, 'equipment/booking-calendar.html', context)


@login_required
@permission_required('equipment.view_equipmentbooking', raise_exception=True)
def booking_detail_view(request, pk):
    """
    View booking information with list of associated items.
    """

    booking = get_object_or_404(
        EquipmentBooking.objects.select_related(
            'created_by',
            'updated_by',
        ),
        id=pk,
    )
    
    booking_items = EquipmentBookingItem.objects.select_related(
        'item',
        'item__manufacturer', 
        'item__category'
        ).filter(equipment_booking=booking,).order_by('created_at')    

    context = {
        'booking': booking,
        'booking_items': booking_items,
    }

    return render(request, 'equipment/booking-detail.html', context)


@login_required
@permission_required('equipment.view_equipmentbooking', raise_exception=True)
def booking_cost_view(request, pk):
    """
    View booking information with list of associated items, and cost summaries.
    """

    booking = get_object_or_404(
        EquipmentBooking.objects.select_related(
            'created_by',
            'updated_by',
        ),
        id=pk,
    )

    hours = convert_duration_to_hours(booking.duration.days, booking.duration.seconds)
    chargeable_days = math.ceil(hours / 24)

    booking_items = EquipmentBookingItem.objects.select_related(
        'item',
        'item__manufacturer', 
        'item__category'
        ).filter(equipment_booking=booking,).annotate(
            total=ExpressionWrapper(F('value') * chargeable_days, output_field=FloatField())
        ).order_by('created_at')
    
    sub_total = booking_items.aggregate(Sum('total', default=0.0))['total__sum']
    vat_percentage = float(booking.vat_value)
    vat_total = (sub_total/100) * (vat_percentage)
    total_cost_vat = sub_total + vat_total
    insure_value = booking_items.aggregate(insure_value=Sum('item__purchase_cost', default=0.0))['insure_value']

    context = {
        'booking': booking,
        'chargeable_days': chargeable_days,
        'booking_items': booking_items,
        'sub_total': sub_total,
        'vat_percentage': vat_percentage,
        'vat_total': vat_total,
        'total_cost_vat': total_cost_vat,
        'insure_value': insure_value,
    }

    return render(request, 'equipment/booking-cost.html', context)


@login_required
@permission_required('equipment.view_equipmentbooking', raise_exception=True)
def booking_invoice_view(request, pk):
    
    booking = get_object_or_404(
        EquipmentBooking.objects.select_related(
            'created_by',
            'updated_by',
        ),
        id=pk,
    )

    hours = convert_duration_to_hours(booking.duration.days, booking.duration.seconds)
    chargeable_days = math.ceil(hours / 24)

    booking_items = EquipmentBookingItem.objects.select_related(
        'item',
        'item__manufacturer', 
        'item__category'
        ).filter(equipment_booking=booking,).annotate(
            total=ExpressionWrapper(F('value') * chargeable_days, output_field=FloatField())
        ).order_by('created_at')
    

    sub_total = booking_items.aggregate(Sum('total', default=0.0))['total__sum']
    vat_percentage = float(booking.vat_value)
    vat_total = (sub_total/100) * (vat_percentage)
    total_cost_vat = sub_total + vat_total

    context = {
        'booking': booking,
        'chargeable_days': chargeable_days,
        'booking_items': booking_items,
        'sub_total': sub_total,
        'vat_percentage': vat_percentage,
        'vat_total': vat_total,
        'total_cost_vat': total_cost_vat,
    }

    return render(request, 'equipment/booking-invoice.html', context)