# app/inventory/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ProductUnit


@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = (
        'short_id', 
        'product', 
        'purchase_price',
        'status_card',
        'status_physical',
        'on_stock', 
        'source_order_link',
        'created_at'
    )
    
    list_filter = ('on_stock', 'status_card', 'status_physical', 'created_at', 'product__brand')
    search_fields = ('id', 'product__name', 'product__code', 'serial_number')
    readonly_fields = ('id', 'created_at', 'received_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'product', 'serial_number')
        }),
        ('Статусы', {
            'fields': ('status_card', 'status_physical', 'on_stock')
        }),
        ('Цены', {
            'fields': ('purchase_price', 'sale_price')
        }),
        ('Контрагенты', {
            'fields': ('supplier', 'customer')
        }),
        ('Связи', {
            'fields': ('source_order_item',)
        }),
        ('Даты', {
            'fields': ('created_at', 'received_at', 'sold_at', 'returned_at')
        }),
    )

    @admin.display(description="ID")
    def short_id(self, obj):
        return str(obj.id)[:8]

    @admin.display(description="Заказ-основание")
    def source_order_link(self, obj):
        if obj.source_order_item:
            order = obj.source_order_item.order
            return format_html(
                '<a href="{}">Заявка #{}</a> (позиция: {})',
                reverse('admin:orders_order_change', args=[order.id]),
                str(order.id)[:8],
                obj.source_order_item.product.name
            )
        return "—"
    
    # Разрешаем создание кандидатов вручную
    def has_add_permission(self, request):
        return True