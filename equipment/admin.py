from django.contrib import admin

from .models import Category, Item, Manufacturer, EquipmentBooking


class CustomItemAdmin(admin.ModelAdmin):
    model = Item
    list_display = ('name', 'created_at', 'updated_at', 'serial_number', 'barcode', 'status')
    search_fields = ('name', 'serial_number')
    ordering = ('created_at',)


class CustomEquipmentBookingAdmin(admin.ModelAdmin):
    model = Item
    list_display = ('job_reference', 'created_at', 'created_by')
    search_fields = ('job_reference',)
    ordering = ('created_at',) 


admin.site.register(Category)
admin.site.register(Item, CustomItemAdmin)
admin.site.register(Manufacturer)
admin.site.register(EquipmentBooking, CustomEquipmentBookingAdmin)