import uuid

from django.core.management.base import BaseCommand
from faker import Faker

from product.models import Product, Category

fake = Faker()

class Command(BaseCommand):
    help = "Заполняет базу тестовыми товарами"

    def handle(self, *args, **kwargs):
        category = Category.objects.get(id=2)
        products = [
            Product(name=fake.word(), slug=fake.slug(), sku=uuid.uuid4().hex[:8].upper(), price=fake.random_int(50, 500), discount=fake.random_int(0, 100), stock_quantity=fake.random_int(1, 100), category=category)
            for _ in range(100)
        ]
        Product.objects.bulk_create(products)
        self.stdout.write(self.style.SUCCESS("✅ 100 товаров добавлено!"))
