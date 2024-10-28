import random

from django.utils import timezone

from equipment.models import Manufacturer, Category, Item


today = timezone.now().date()

items = [
    {
        'manufacturer': 'Sony',
        'category': 'Camera',
        'name': 'A7S',
        'mount': 'E',        
        'purchase_date': today,
        'purchase_cost': 3500.00,
        'hire_day_rate': 50.00,
    },
    {
        'manufacturer': 'Sony',
        'category': 'Camera',
        'name': 'A7R',
        'mount': 'E',
        'purchase_date': today,
        'purchase_cost': 3500.00,
        'hire_day_rate': 50.00,
    },
    {
        'manufacturer': 'GoPro',
        'category': 'Camera',
        'name': 'Hero 10',
        'purchase_date': today,
        'purchase_cost': 400.00,
        'hire_day_rate': 25.00,
    },
    {
        'manufacturer': 'Sony',
        'category': 'Lens',
        'name': '16-35mm',
        'mount': 'E',
        'purchase_date': today,
        'purchase_cost': 1200.00,
        'hire_day_rate': 30.00,
    },
    {
        'manufacturer': 'Sony',
        'category': 'Lens',
        'name': '24-70mm',
        'mount': 'E',
        'purchase_date': today,
        'purchase_cost': 1200.00,
        'hire_day_rate': 30.00,
    }, 
    {
        'manufacturer': 'Sony',
        'category': 'Lens',
        'name': '70-200mm',
        'mount': 'E',
        'purchase_date': today,
        'purchase_cost': 1200.00,
        'hire_day_rate': 30.00,
    },
    {
        'manufacturer': 'Arri',
        'category': 'Lighting',
        'name': 'Sky Panel X',
        'purchase_date': today,
        'purchase_cost': 2500.00,
        'hire_day_rate': 40.00,
    },
    {
        'manufacturer': 'Sony',
        'category': 'Power',
        'name': 'Battery',
        'purchase_date': today,
        'purchase_cost': 50.00,
        'hire_day_rate': 5.00,
    },
]


# python manage.py runscript seeds

def run():
    """
    Creates random items for development.
    """

    for i in range(750):
        
        random_item = random.choices(items)[0]

        category, created = Category.objects.get_or_create(
            name = random_item.get('category', None)
        ) 

        manufacturer, created = Manufacturer.objects.get_or_create(
            name = random_item.get('manufacturer', None)
        )
        
        numbers = range(0,9)
        serial = ''.join([str(random.choices(numbers)[0]) for i in range(10)])

        new_item = Item.objects.create(
            manufacturer = manufacturer,
            category = category,
            name = random_item.get('name', None),
            mount = random_item.get('mount', None),
            serial_number = serial,
            purchase_date = random_item.get('purchase_date', None),
            hire_day_rate = random_item.get('hire_day_rate', None),
        )

        print(f'Created {new_item}...')
