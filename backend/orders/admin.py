from django.contrib import admin
from .models import Counterparty, Order

@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_supplier', 'is_customer')
    list_filter = ('is_supplier', 'is_customer')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Что отображать в списке
    list_display = ('product', 'supplier', 'quantity_ordered', 'quantity_received', 'created_at')
    # Фильтры справа
    list_filter = ('supplier', 'is_custom_order')
    # Поиск по названию товара или артикулу (через связь с моделью Product)
    search_fields = ('product__name', 'product__code')
