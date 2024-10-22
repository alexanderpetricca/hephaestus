from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from equipment.models import (
    Item, 
    Category, 
    Manufacturer, 
    EquipmentBooking, 
    EquipmentBookingItem
)


class EquipmentModelsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Create Test User        
        cls.user = get_user_model().objects.create_user(
            first_name = 'Test',
            last_name = 'User',
            email = 'testuser@email.com',
            password = 'testpass123'
        )

        # Create Manufacturer
        cls.manufacturer = Manufacturer.objects.create(
            name = 'Test Manufacturer',
        )

        # Create Category
        cls.category = Category.objects.create(
            name = 'Test Category',
        )        

        # Create Test Item 1
        cls.item = Item.objects.create(
            created_by = cls.user,
            category = cls.category,
            manufacturer = cls.manufacturer,
            name = 'Test Item 1',
            model_number = 'TI',
            serial_number = 'TI-123',
            notes = 'Some useful test notes.',
        )

        # Create Test Item 2
        cls.item_two = Item.objects.create(
            created_by = cls.user,
            category = cls.category,
            manufacturer = cls.manufacturer,
            name = 'Test Item 2',
            model_number = 'TI',
            serial_number = 'TI-456',
            notes = 'Some more useful test notes.',
        )

        # Create Test Booking
        cls.booking = EquipmentBooking.objects.create(
            created_by = cls.user,
            job_reference = 'Test Job',
            start_at = timezone.now() + timedelta(days=3, hours=9),
            end_at = timezone.now() + timedelta(days=4, hours=9),
            status = 'CONFIRMED',
        )

        # Permissions
        cls.view_item = Permission.objects.get(codename='view_item')
        cls.add_item = Permission.objects.get(codename='add_item')
        cls.change_item = Permission.objects.get(codename='change_item')    
        cls.delete_item = Permission.objects.get(codename='delete_item')

        cls.view_booking = Permission.objects.get(codename='view_equipmentbooking')
        cls.add_booking = Permission.objects.get(codename='add_equipmentbooking')
        cls.change_booking = Permission.objects.get(codename='change_equipmentbooking')
        cls.delete_booking = Permission.objects.get(codename='delete_equipmentbooking')

    
    # Equipment Dashboard View
    def test_equipment_dashboard_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the equipment dashboard.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_equipment_dashboard_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the equipment dashboard.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_dashboard'))
        self.assertEqual(response.status_code, 403)


    def test_equipment_dashboard_logged_in_with_perm(self):
        """
        Tests manage equipment dashboard page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/dashboard.html')
        self.assertContains(response, 'Equipment Dashboard | Hephaestus')


    # Equipment Query View
    def test_item_query_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the item query page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_item_query'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/item-query/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/item-query/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_item_query_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the item query page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_item_query'))
        self.assertEqual(response.status_code, 403)


    def test_item_query_logged_in_with_perm(self):
        """
        Tests manage item query page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_item)
        self.client.login(email="testuser@email.com", password="testpass123")
        
        response = self.client.get(reverse('equipment_item_query'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/item-query.html')
        self.assertContains(response, 'Equipment Query | Hephaestus')
        
        # Test Filter
        # response = self.client.get(f'{reverse("equipment_item_query")}?department={self.department.id}')

        # self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Test Item 1')
        # self.assertNotContains(response, 'Test Item 2')

        # Test Search
        response = self.client.get(f'{reverse("equipment_item_query")}?search=2')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item 2')
        self.assertNotContains(response, 'Test Item 1')


    # Equipment Item Detail
    def test_item_detail_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the item detail page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_item_detail', kwargs={'pk':self.item.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/item-detail/{str(self.item.id)}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/item-detail/{str(self.item.id)}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_item_detail_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the item detail page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_item_detail', kwargs={'pk':self.item.pk}))
        self.assertEqual(response.status_code, 403)


    def test_item_detail_logged_in_with_perm(self):
        """
        Tests manage item detail page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_item_detail', kwargs={'pk':self.item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/item-detail.html')
        self.assertContains(response, 'Item Information | Hephaestus')
        self.assertContains(response, 'Test Item 1')
        
   
    # Equipment Create Item View
    def test_equipment_create_item_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the create item page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_create_item'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/create-item/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/create-item/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_equipment_create_item_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the create item page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_create_item'))
        self.assertEqual(response.status_code, 403)


    def test_equipment_create_item_logged_in_with_perm(self):
        """
        Tests manage create item page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.add_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # GET
        response = self.client.get(reverse('equipment_create_item'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/create-item.html')
        self.assertContains(response, 'Equipment Create Item | Hephaestus')
        
        # POST
        data = {
            'category': self.category.id,
            'manufacturer': self.manufacturer.id,
            'name': 'Test Item 3',
            'purchase_cost': 100.00,            
            'hire_day_rate': 50.00,
        }

        response = self.client.post(reverse('equipment_create_item'), data=data)
        self.assertEqual(response.status_code, 302)

        try:
            new_item = Item.objects.get(name='Test Item 3')
        except Item.DoesNotExist:
            self.fail("Item was not created.")
        except Item.MultipleObjectsReturned:
            self.fail("Multiple instances of Item were created.")
        

    # Equipment Update Item View
    def test_equipment_update_item_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the update item page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_update_item', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/update-item/{self.item.pk}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/update-item/{self.item.pk}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_equipment_update_item_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the update item page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_update_item', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 403)


    def test_equipment_update_item_logged_in_with_perm(self):
        """
        Tests manage update item page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.change_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # GET
        response = self.client.get(reverse('equipment_update_item', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/update-item.html')
        self.assertContains(response, 'Equipment Update Item | Hephaestus')

        # POST
        data = {
            'category': self.category.id,
            'manufacturer': self.manufacturer.id,
            'name': 'Test Item 1 (Updated)',
            'purchase_cost': 100.00,
            'hire_day_rate': 50.00,
        }

        response = self.client.post(reverse('equipment_update_item', kwargs={'pk': self.item.pk}), data=data)
        self.assertEqual(response.status_code, 302)

        try:
            updated_item = Item.objects.get(name='Test Item 1 (Updated)')
        except Item.DoesNotExist:
            self.fail("Item was not updated.")


    # Equipment Update Item Service Date View
    def test_equipment_update_item_service_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the update item service date page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_update_service', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/update-item-service/{self.item.pk}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/update-item-service/{self.item.pk}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_equipment_update_item_service_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the update item page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_update_service', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 403)


    def test_equipment_update_item_service_logged_in_with_perm(self):
        """
        Tests manage update item service date page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.change_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # GET
        response = self.client.get(reverse('equipment_update_service', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/update-item-service.html')
        self.assertContains(response, 'Equipment Update Service Date | Hephaestus')

        # POST
        data = {
            'last_service_date': timezone.now().date() - timedelta(days=1),
        }

        response = self.client.post(reverse('equipment_update_service', kwargs={'pk': self.item.pk}), data=data)
        self.assertEqual(response.status_code, 302)

        updated_item = Item.objects.get(name='Test Item 1')
        self.assertTrue(updated_item.last_service_date == timezone.now().date() - timedelta(days=1))
        

    # Equipment Delete Item View
    def test_delete_item_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the item delete page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_delete_item', kwargs={'pk': str(self.item.id)}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/delete-item/{self.item.id}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/delete-item/{self.item.id}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_delete_item_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the item delete page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_delete_item', kwargs={'pk': str(self.item.id)}))
        self.assertEqual(response.status_code, 403)


    def test_delete_item_logged_in_with_perm(self):
        """
        Tests manage item delete page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.delete_item)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # GET
        response = self.client.get(reverse('equipment_delete_item', kwargs={'pk': str(self.item.id)}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/delete-item.html')
        self.assertContains(response, 'Equipment Delete Item | Hephaestus')

        # POST
        response = self.client.post(reverse('equipment_delete_item', kwargs={'pk': str(self.item.id)}))
        self.assertEqual(response.status_code, 302)

        try:
            deleted_item = Item.objects.get(name='Test Item 1', deleted=True)
        except Item.DoesNotExist:
            self.fail("Item was not deleted.")       
       
    
    # !! TODO Equipment Assign Item View
    
    # !! TODO Equipment Unassign Item View
    

    # Booking Summary (View / Create)
    def test_booking_summary_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking summary page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_summary'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-summary/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-summary/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_summary_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking summary page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_summary'))
        self.assertEqual(response.status_code, 403)


    def test_booking_summary_logged_in_with_perm(self):
        """
        Tests manage booking summary page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.add_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-summary.html')
        self.assertContains(response, 'Booking Summary | Hephaestus')
        
        # Test new booking form rendered if no pending booking
        self.assertContains(response, 'New Booking')

        # Test existing booking rendered if pending booking
        self.booking.status = 'PENDING'
        self.booking.save()

        response = self.client.get(reverse('equipment_booking_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')


    # Summary Confirm
    def test_booking_summary_confirm_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the confirm booking page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-summary-confirm/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-summary-confirm/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_summary_confirm_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the confirm booking page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 403)


    def test_booking_summary_confirm_logged_in_with_perm(self):
        """
        Tests manage confirm booking page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.add_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # Test returns 404 if no pending booking
        response = self.client.get(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 404)

        # GET (with pending booking)
        self.booking.status = 'PENDING'
        self.booking.save()

        # Tests view redirects if no items on booking
        response = self.client.get(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 302)

        # Tests view renders confirm page if item exists
        booking_item = EquipmentBookingItem.objects.create(
            equipment_booking = self.booking,
            item = self.item,
        ) 

        response = self.client.get(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-confirm.html')
        self.assertContains(response, 'Confirm Booking | Hephaestus')        
        
        # POST
        response = self.client.post(reverse('equipment_booking_summary_confirm'))
        self.assertEqual(response.status_code, 302)

        try:
            booking = EquipmentBooking.objects.get(job_reference='Test Job', status='CONFIRMED')
        except EquipmentBooking.DoesNotExist:
            self.fail("Booking was not confirmed.")     


    # Summary Cancel
    # Factor in in booking is already confirmed or not
    def test_booking_summary_cancel_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking summary cancel page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-summary-cancel/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-summary-cancel/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_summary_cancel_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking summary cancel page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 403)


    def test_booking_summary_cancel_logged_in_with_perm(self):
        """
        Tests booking summary cancel is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.add_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # Test 404 returned if no pending booking
        response = self.client.get(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 404)    

        # GET - Test confirm page is rendered if pending booking
        self.booking.status = 'PENDING'
        self.booking.save() 

        response = self.client.get(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-cancel.html')
        self.assertContains(response, 'Cancel Booking | Hephaestus')

        # POST - Test booking is cancelled if booking IS pre-confirmed
        self.booking.confirmed = True
        self.booking.save()

        response = self.client.post(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 302)

        try:
            booking = EquipmentBooking.objects.get(job_reference='Test Job', status='CANCELLED')
        except EquipmentBooking.DoesNotExist:
            self.fail("Booking was not cancelled.")      
        
        # POST - Test booking is deleted if IS NOT pre-confirmed
        self.booking.status = 'PENDING'
        self.booking.confirmed = False
        self.booking.save() 

        response = self.client.post(reverse('equipment_booking_summary_cancel'))
        self.assertEqual(response.status_code, 302)

        booking = EquipmentBooking.objects.filter(job_reference='Test Job')
        if booking.exists():
            self.fail("Booking was not deleted.")


    # Update Booking Meta
    def test_booking_update_meta_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the update booking meta page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_update_meta', kwargs={'pk': self.booking.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-update-meta/{self.booking.id}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-update-meta/{self.booking.id}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_update_meta_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the update booking meta page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_update_meta', kwargs={'pk': self.booking.pk}))
        self.assertEqual(response.status_code, 403)


    def test_booking_update_meta_logged_in_with_perm(self):
        """
        Tests manage update booking meta page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.change_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        # Test returns 404 if no pending booking
        response = self.client.get(reverse('equipment_booking_update_meta', kwargs={'pk': self.booking.pk}))
        self.assertEqual(response.status_code, 404)

        # GET (with pending booking)
        self.booking.status = 'PENDING'
        self.booking.save()

        response = self.client.get(reverse('equipment_booking_update_meta', kwargs={'pk': self.booking.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-update-meta.html')
        self.assertContains(response, 'Equipment Update Booking Meta | Hephaestus')
        
        # POST
        data = {
            'job_reference': 'Test Job (updated)',
            'start_at': timezone.now() + timedelta(days=3, hours=9),
            'end_at': timezone.now() + timedelta(days=4, hours=9),
        }

        response = self.client.post(reverse('equipment_booking_update_meta', kwargs={'pk': self.booking.pk}), data=data)
        self.assertEqual(response.status_code, 302)

        try:
            booking = EquipmentBooking.objects.get(job_reference='Test Job (updated)')
        except EquipmentBooking.DoesNotExist:
            self.fail("Booking was not updated.")                    

  
    # Booking Calendar View
    def test_booking_calendar_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking calendar page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_calendar'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-calendar/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-calendar/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_calendar_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking calendar page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_calendar'))
        self.assertEqual(response.status_code, 403)


    def test_booking_calendar_logged_in_with_perm(self):
        """
        Tests booking calendar page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-calendar.html')
        self.assertContains(response, 'Booking Calendar | Hephaestus')


    # Booking Query View
    def test_booking_query_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking query page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_query'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-query/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-query/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_query_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking query page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_item_query'))
        self.assertEqual(response.status_code, 403)


    def test_booking_query_logged_in_with_perm(self):
        """
        Tests manage booking query page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_query'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-query.html')
        self.assertContains(response, 'Booking Query | Hephaestus')
        
        # Test Filter
        date_range_start = timezone.now().date() - timedelta(days=2)
        date_range_end = timezone.now().date() + timedelta(days=5)

        response = self.client.get(f'{reverse("equipment_booking_query")}?date_range_start={date_range_start}&date_range_end={date_range_end}')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

        # # Test Search
        response = self.client.get(f'{reverse("equipment_booking_query")}?search=Test')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')


    # Booking Detail
    def test_booking_detail_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking detail page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_detail', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-detail/{str(self.booking.id)}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-detail/{str(self.booking.id)}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_detail_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking detail page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_detail', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 403)


    def test_booking_detail_logged_in_with_perm(self):
        """
        Tests manage booking detail page is returned when user is logged in 
        with permission.
        """

        self.user.user_permissions.add(self.view_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_detail', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-detail.html')
        self.assertContains(response, 'Booking Information | Hephaestus')
        self.assertContains(response, 'Overview')           
        self.assertContains(response, self.booking.job_reference)


    # Booking Costs
    def test_booking_costs_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking information costs page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_cost', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-cost/{str(self.booking.id)}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-cost/{str(self.booking.id)}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_costs_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking information costs page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_cost', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 403)


    def test_booking_costs_logged_in_with_perm(self):
        """
        Tests manage booking information costs page is returned when user is 
        logged in with permission.
        """

        self.user.user_permissions.add(self.view_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_cost', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-cost.html')
        self.assertContains(response, 'Booking Information | Hephaestus')    
        self.assertContains(response, 'Costs')    
        self.assertContains(response, self.booking.job_reference)


    # Booking Invoice
    def test_booking_costs_logged_out(self):
        """
        Tests if user is redirected to login when signed out whilst trying to 
        access the booking information invoice page.
        """
        
        self.client.logout()
        
        response = self.client.get(reverse('equipment_booking_invoice', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/booking-invoice/{str(self.booking.id)}/")
        
        response = self.client.get(f"{reverse('account_login')}?next=/booking-invoice/{str(self.booking.id)}/")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Login | Hephaestus')


    def test_booking_costs_logged_in_no_perm(self):
        """
        Tests 403 response is returned when user is logged in without 
        permission and tries to access the booking information invoice page.
        """

        self.client.login(email="testuser@email.com", password="testpass123")        
        
        response = self.client.get(reverse('equipment_booking_invoice', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 403)


    def test_booking_costs_logged_in_with_perm(self):
        """
        Tests manage booking information invoice page is returned when user is 
        logged in with permission.
        """

        self.user.user_permissions.add(self.view_booking)
        self.client.login(email="testuser@email.com", password="testpass123")       
        
        response = self.client.get(reverse('equipment_booking_invoice', kwargs={'pk': self.booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/booking-invoice.html')
        self.assertContains(response, f'Invoice - {self.booking.job_reference}')
        self.assertContains(response, 'Invoice')    
        self.assertContains(response, self.booking.job_reference)