from django import forms
from django.contrib.auth import get_user_model

from .models import Item, EquipmentBooking
from core.forms import DateInput, DateTimeInput


class CreateUpdateItemForm(forms.ModelForm):
    """
    Form used to create or update an item.
    """

    class Meta:
        
        model = Item        
        fields = [
            'category',
            'manufacturer',
            'name',
            'mount',
            'model_number',
            'serial_number',
            'barcode',
            'notes',
            'purchase_date',
            'purchase_cost',
            'depreciation_method',
            'hire_day_rate',
            'last_service_date',
            'service_interval_period',
        ]
        labels = {
            'notes': '',
            'model_number': 'Model Number',
            'serial_number': "Serial Number",
            'purchase_date': "Purchase Date",
            'purchase_cost': "Purchase Cost",
            'depreciation_method': "Depreciation Method",
            'hire_day_rate': 'Hire Day Rate',
            'last_service_date': "Last Service Date",
            'service_interval_period': "Service Interval Period",
        }
        help_texts = {
            'department': 'Required. The department this item is assigned to.',
            'category': 'Required.',
            'manufacturer': 'Required.',
            'name': 'Required. Item name.',
            'mount': 'Optional. e.g. EF.',
            'model_number': 'Optional. Manufacturers model number.',
            'serial_number': 'Optional. Manufacturers unqiue serial number.',
            'barcode': 'Optional. Unique barcode number. Leave blank to auto generate.',
            'notes': 'Optional. Internal notes & references.',
            'hire_day_rate': 'Optional. Leaving this blank will cause it to be valued at 0.0 on invoices.',
            'last_service_date': "Optional.",
            'service_interval_period': "Optional.",
        }
        widgets = {
            'purchase_date': DateInput,
            'last_service_date': DateInput,
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
        }


    def __init__(self, *args, **kwargs):
        super(CreateUpdateItemForm, self).__init__(*args, **kwargs)

        self.fields['category'].required = True
        self.fields['manufacturer'].required = True


class AssignItemForm(forms.ModelForm):
    """
    Form used to assign a user to piece of equipment.
    """

    assigned_user = forms.ModelChoiceField(
        required=True, 
        queryset=get_user_model().objects.all(),
    )
    

    class Meta:
        model = Item
        fields = [
            'assigned_user',
        ]


class CreateUpdateBookingForm(forms.ModelForm):
    """
    Form used to create or update an equipment booking.
    """

    class Meta:
        model = EquipmentBooking
        
        fields = [
            'job_reference',
            'job_number',
            'start_at',
            'end_at',
        ]

        labels = {
            'start_at': 'Booking Start',
            'end_at': 'Booking End',
        }

        help_texts = {
            'job_reference': 'i.e. job name / number.'
        }

        widgets = {
            'start_at': DateTimeInput(),
            'end_at': DateTimeInput(),
        }


class UpdateItemServiceDateForm(forms.ModelForm):

    class Meta:
        model = Item
        
        fields = [
            'last_service_date',
        ]
        
        labels = {
            'last_service_date': 'Last Service Date',
        }
        
        help_texts = {
            'last_service_date': 'Required. The date the item was last serviced.',
        }

        widgets = {
            'last_service_date': DateInput,
        }


    def __init__(self, *args, **kwargs):
        super(UpdateItemServiceDateForm, self).__init__(*args, **kwargs)
        self.fields['last_service_date'].required = True