#products/models.py
import uuid
from django.db import models

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    # Slug нужен для красивых URL (например, /category/smartphones/)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Слаг")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products',
        verbose_name="Категория"
    )
    code = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Артикул"
    )
    name = models.CharField(max_length=255, verbose_name="Наименование")
    brand = models.CharField(max_length=255, verbose_name="Бренд")
    description = models.TextField(blank=True, verbose_name="Описание")
    photo = models.ImageField(
        upload_to='products/photos/', 
        blank=True, 
        null=True, 
        verbose_name="Фотокарточка"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} - {self.name} ({self.code})"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"