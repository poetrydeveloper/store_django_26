from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Product, Category 

class ProductDBTest(TestCase):
    def test_create_product_with_code(self):
        """Проверка создания товара с полем code"""
        product = Product.objects.create(
            code="ABC-123",
            name="Кроссовки",
            brand="Бренд"
        )
        self.assertEqual(product.code, "ABC-123")

    def test_duplicate_code_error(self):
        """Проверка уникальности поля code"""
        Product.objects.create(code="UNIQUE-01", name="Первый", brand="B")
        with self.assertRaises(IntegrityError):
            Product.objects.create(code="UNIQUE-01", name="Второй", brand="B")

    def test_product_category_relation(self):
        """Проверка связи товара с категорией"""
        cat = Category.objects.create(name="Обувь", slug="shoes")
        prod = Product.objects.create(
            code="SH-001", 
            name="Кеды", 
            brand="Converse",
            category=cat
        )
        self.assertEqual(prod.category.name, "Обувь")
        # Проверка обратной связи: сколько товаров в категории?
        self.assertEqual(cat.products.count(), 1)