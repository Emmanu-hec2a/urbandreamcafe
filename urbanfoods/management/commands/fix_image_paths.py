from django.core.management.base import BaseCommand
from urbanfoods.models import FoodItem

class Command(BaseCommand):
    help = 'Fix Cloudinary image paths'

    def handle(self, *args, **options):
        items = FoodItem.objects.filter(image__startswith='media/')
        count = 0
        for item in items:
            old_path = str(item.image)
            new_path = old_path.replace('media/', '', 1)
            item.image = new_path
            item.save()
            self.stdout.write(f'Fixed: {item.name}')
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Fixed {count} items!'))