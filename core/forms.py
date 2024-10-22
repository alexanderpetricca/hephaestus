from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'


class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'