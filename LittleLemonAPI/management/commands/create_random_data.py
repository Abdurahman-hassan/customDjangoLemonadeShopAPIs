import random
import string

from django.core.management.base import BaseCommand

from LittleLemonAPI.models import MenuItem, Category


class Command(BaseCommand):
    help = 'Create random menu items'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of menu items to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        for i in range(total):
            # Get a random category
            category = Category.objects.order_by('?').first()
            if category is not None:
                MenuItem.objects.create(title=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                                        inventory=random.randint(1, 100),
                                        price=random.uniform(10, 100),
                                        category=category)
            else:
                print("No categories available. Please create some categories before creating menu items.")
                break