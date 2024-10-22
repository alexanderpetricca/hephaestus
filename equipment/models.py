import uuid, string, random
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError


class Manufacturer(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)


    class Meta:
        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturers'
        ordering = ['name',]


    def __str__(self):
        return str(self.name)


class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name',]


    def __str__(self):
        return str(self.name)


class Item(models.Model):

    STATUS_CHOICES = (
        ('ASSIGNED', 'Assigned'),
        ('DEPRECIATED', 'Depreciated'),
        ('MISSING', 'Missing'),
        ('POOL', 'Pool'),
        ('REPAIR', 'Repair'),
        ('SOLD', 'Sold'),
    )

    DEPRECIATION_CHOICES = (
        ('DECLINING-BALANCE', 'Declining Balance'),
        ('STRAIGHT-LINE', 'Straight Line'),
        ('SUM-OF-YEARS', 'Sum of Years'),
        ('UNITS-OF-PRODUCTION', 'Units of Production'),
    )

    SERVICE_INTERVAL_CHOICES = [
        (timedelta(days=30), '1 Month'),
        (timedelta(days=90), '3 Months'),
        (timedelta(days=180), '6 Months'),
        (timedelta(days=365), '1 Year'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='item_created_by',
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='item_updated_by',
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
    )
    name = models.CharField(max_length=100)
    mount = models.CharField(max_length=15, null=True, blank=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='POOL')
    barcode = models.CharField(max_length=13, null=True, blank=True, db_index=True)
    notes = models.TextField(max_length=1000, null=True, blank=True)

    assigned_to = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='item_assigned_to',
    )

    purchase_date = models.DateField(null=True, blank=True)    
    purchase_cost = models.FloatField(default=0.00)
    depreciation_method = models.CharField(default="DECLINING-BALANCE", choices=DEPRECIATION_CHOICES, null=True, blank=True)
    hire_day_rate = models.FloatField(default=0.00)

    last_service_date = models.DateField(null=True, blank=True)
    service_interval_period = models.DurationField(choices=SERVICE_INTERVAL_CHOICES, null=True, blank=True)
    service_due_date = models.DateField(null=True, blank=True)
    retired = models.BooleanField(default=False)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        permissions = [            
            ('assign_item', 'Can assign an item to individual.'),
        ]        


    def __str__(self):
        return str(self.id)
    

    def generate_barcode(self):
        """
        Generates a unique barcode number for internal use.
        """
        
        numbers = string.digits
        max_attempts = 100
    
        for attempt in range(max_attempts):
            barcode = ''.join(
                [numbers[random.randint(0, len(numbers)-1)] for i in range(13)]
            )

            if not Item.objects.filter(barcode=barcode).exists():
                return barcode
            
        raise ValueError(
            "Failed to generate a unique barcode after several attempts."
        )
    

    def calculate_depreciation(self):

        # Annual depreciation rate as percentage
        depreciation_rate = 20
        purchase_date = self.purchase_date

        if purchase_date:
            years_owned = (timezone.now().date() - purchase_date).days / 365.25
            depreciated_value = self.purchase_cost * ((1 - depreciation_rate / 100) ** years_owned)
        else:
            depreciated_value = self.purchase_cost

        return depreciated_value
    

    def assign_item(self, user_id):
        """
        Assigns the equipment to specific user.
        """

        self.assigned_to = user_id
        self.status = 'ASSIGNED'
        self.save()


    def unassign_item(self):
        """
        Unassigns the equipment from a user.
        """

        self.assigned_to = None
        if self.status == 'ASSIGNED':
            self.status = 'POOL'
        self.save()


    def soft_delete(self):
        """
        Soft deletes the item, logging the time it was deleted.
        """

        self.deleted = True
        self.deleted_at = timezone.now()
        self.status = 'DEPRECIATED'
        self.save()


    def save(self, *args, **kwargs):

        if not self.barcode:
            self.barcode = self.generate_barcode()

        super(Item, self).save(*args, **kwargs)


class EquipmentBooking(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_booking_created_by',
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_booking_updated_by',
    )

    job_reference = models.CharField(max_length=30)
    job_number = models.CharField(max_length=30, null=True, blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(max_length=300, null=True, blank=True)

    vat_value = models.DecimalField(default=20.00, max_digits=4, decimal_places=2)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    confirmed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)


    class Meta:
        verbose_name = 'Equipment Booking'
        verbose_name_plural = 'Equipment Bookings'

       
    def __str__(self):
        return str(self.job_reference)
    

    def calc_duration(self):
        return self.end_at - self.start_at
    

    def verify_booking(self):
        booked_items = self.booking_items.all()
        booking_start = self.start_at
        booking_end = self.end_at

        # Check if booking contains at least one item
        if booked_items.count() < 1:
            raise ValidationError('Bookings must contain at least one item.')

        # Check if any of the items in the current booking are already booked during the same date and time
        for item in booked_items:
            conflicting_bookings = EquipmentBookingItem.objects.filter(
                item=item.item,
                equipment_booking__start_at__lt=booking_end,
                equipment_booking__end_at__gt=booking_start,
                equipment_booking__status__in=['PENDING', 'CONFIRMED'],
            ).exclude(equipment_booking=self)

            if conflicting_bookings.exists():
                raise ValidationError(f"One or more items is already booked for that period.")

        # If no conflicts, booking is valid
        return True
    

    def revert_to_pending(self):
        self.status = 'PENDING'
        self.save()


    def confirm(self):
        self.status = 'CONFIRMED'
        self.confirmed = True
        self.save()


    def cancel(self):
        """
        Cancels the booking, logging the time it was cancelled.
        """

        self.cancelled = True
        self.cancelled_at = timezone.now()
        self.status = 'CANCELLED'
        self.save()


    def clean(self):
        
        if self.end_at < self.start_at:
            raise ValidationError('Booking end cannot be before booking start.')
        

    def save(self, *args, **kwargs):

        if self.start_at and self.end_at:
            self.duration = self.calc_duration()

        super(EquipmentBooking, self).save(*args, **kwargs)        



class EquipmentBookingItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    equipment_booking = models.ForeignKey(
        EquipmentBooking, 
        on_delete=models.CASCADE,
        related_name='booking_items',
    )
    item = models.ForeignKey(
        Item, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='booked_items',
    )
    value = models.FloatField(default=0.00)


    class Meta:
        verbose_name = 'Equipment Booking Item'
        verbose_name_plural = 'Equipment Booking Items'
        unique_together = ('equipment_booking', 'item')


    def __str__(self):
        return str(self.id)
    

    def save(self, *args, **kwargs):

        if self.item:
            self.value = self.item.hire_day_rate

        super(EquipmentBookingItem, self).save(*args, **kwargs)   