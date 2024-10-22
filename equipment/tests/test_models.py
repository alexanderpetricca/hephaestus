from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from equipment.models import (
    Manufacturer, 
    Category, 
    Item, 
    EquipmentBooking, 
    EquipmentBookingItem
)

class EquipmentModelsTest(TestCase):
    
    def setUp(self):

        # Create User
        self.test_user = get_user_model().objects.create_user(
            first_name = 'Test',
            last_name = 'User',
            email = 'testuser@email.com',
            password = 'testpass123'
        )

        # Create Manufacturer
        self.manufacturer = Manufacturer.objects.create(
            name = 'Test Manufacturer',
        )

        # Create Category
        self.category = Category.objects.create(
            name = 'Test Category',
        )

        # Create Item
        self.item = Item.objects.create(
            created_by = self.test_user,
            category = self.category,
            manufacturer = self.manufacturer,
            name = 'Test Item',
            mount = 'TM',
            model_number = 'TI',
            serial_number = 'TI-1234567',
            notes = 'Some useful test notes.',
            assigned_to = self.test_user,
            purchase_date = timezone.now().date(),
            purchase_cost = 200.00,
            hire_day_rate = 50.00
        )

        # Create Booking
        self.booking = EquipmentBooking.objects.create(
            created_by = self.test_user,
            job_reference = 'Test Booking',
            job_number = 'TJ-123',
            start_at = timezone.now(),
            end_at = timezone.now() + timedelta(days=1),
            vat_value = 17.50
        )

        # Create Booking Item
        self.booking_item = EquipmentBookingItem.objects.create(
            equipment_booking = self.booking,
            item = self.item,
        )               


    def test_manufacturer_model(self):
        """
        Test manufacturer objects are created correctly.
        """
        
        self.assertIsNotNone(self.manufacturer.created_at)
        self.assertEqual(self.manufacturer.name, 'Test Manufacturer')


    def test_manufacturer_string_method(self):
        """
        Tests manufacturer object string method.
        """
        
        self.assertEqual(str(self.manufacturer), 'Test Manufacturer')


    def test_category_model(self):
        """
        Test manufacturer objects are created correctly.
        """

        self.assertIsNotNone(self.category.created_at)
        self.assertEqual(self.category.name, 'Test Category')


    def test_category_string_method(self):
        """
        Tests category object string method.
        """
        
        self.assertEqual(str(self.category), 'Test Category')


    def test_item_model(self):
        """
        Test item objects are created correctly.
        """

        self.assertIsNotNone(self.item.created_at)
        self.assertEqual(self.item.created_by, self.test_user)
        self.assertEqual(self.item.category, self.category)
        self.assertEqual(self.item.manufacturer, self.manufacturer)
        self.assertEqual(self.item.name, 'Test Item')
        self.assertEqual(self.item.mount, 'TM')
        self.assertEqual(self.item.model_number, 'TI')
        self.assertEqual(self.item.serial_number, 'TI-1234567')
        self.assertEqual(self.item.status, 'POOL')
        self.assertIsNotNone(self.item.barcode)
        self.assertEqual(self.item.notes, 'Some useful test notes.')
        self.assertEqual(self.item.assigned_to, self.test_user)
        self.assertEqual(self.item.purchase_date, timezone.now().date())
        self.assertEqual(self.item.purchase_cost, 200.00)
        self.assertEqual(self.item.hire_day_rate, 50.00)


    def test_item_string_method(self):
        """
        Tests item object string method.
        """
        
        self.assertEqual(str(self.item), str(self.item.id))


    def test_booking_model(self):
        """
        Test booking objects are created correctly.
        """

        self.assertIsNotNone(self.booking.created_at)
        self.assertEqual(self.booking.created_by, self.test_user)
        self.assertEqual(self.booking.job_reference, 'Test Booking')
        self.assertEqual(self.booking.job_number, 'TJ-123')
        self.assertEqual(self.booking.start_at.date(), timezone.now().date())
        self.assertEqual(self.booking.end_at.date(), timezone.now().date() + timedelta(days=1))
        self.assertFalse(self.booking.confirmed)


    def test_booking_string_method(self):
        """
        Tests booking object string method.
        """
        
        self.assertEqual(str(self.booking), str(self.booking.job_reference))


    def test_booking_item_model(self):
        """
        Test equipment booking item objects are created correctly.
        """

        self.assertIsNotNone(self.booking_item.created_at)
        self.assertEqual(self.booking_item.equipment_booking, self.booking)
        self.assertEqual(self.booking_item.item, self.item)
        self.assertEqual(self.booking_item.value, 50.00)


    def test_booking_item_string_method(self):
        """
        Tests equipment booking item object string method.
        """
        
        self.assertEqual(str(self.booking_item), str(self.booking_item.id))  