from django.contrib import admin
from .models import ProductUnit

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'id', 'on_stock', 'created_at')
    list_filter = ('on_stock', 'product__brand')
    # Позволяет быстро найти юнит по ID или артикулу товара
    search_fields = ('id', 'product__name', 'product__code')
    # Сделаем поле ID доступным только для чтения, так как это UUID
    readonly_fields = ('id', 'created_at')
