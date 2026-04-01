from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Автоматическое заполнение слага из названия (удобно!)
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Поля, которые будут видны в таблице товаров
    list_display = ('brand', 'name', 'code', 'category', 'created_at')
    # Фильтры справа
    list_filter = ('category', 'brand')
    # Поиск по названию и артикулу
    search_fields = ('name', 'code', 'brand')
