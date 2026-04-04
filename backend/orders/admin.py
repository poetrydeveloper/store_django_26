# app/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Supplier, Customer, Order, OrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity_ordered', 'price')
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'short_id', 'supplier', 'customer', 'get_total_cost', 
        'is_custom_order', 'created_at'
    )
    list_filter = ('is_custom_order', 'supplier', 'created_at')
    search_fields = ('id', 'supplier__name')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'is_custom_order')
        }),
        ('Заказчик', {
            'description': "Заполняется, если товар везется под конкретного клиента",
            'fields': ('customer',)
        }),
        ('Комментарий', {
            'fields': ('comment',)
        }),
    )

    @admin.display(description="ID Заявки")
    def short_id(self, obj):
        return str(obj.id)[:8]

    @admin.display(description="Итоговая сумма")
    def get_total_cost(self, obj):
        return f"{obj.total_cost} руб."


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity_ordered', 'price', 'total_cost', 'total_received')
    list_filter = ('order__supplier',)
    search_fields = ('product__name',)
    readonly_fields = ('total_received',)
    
    @admin.display(description="Сумма")
    def total_cost(self, obj):
        return f"{obj.total_cost} руб."
    
    @admin.display(description="Получено")
    def total_received(self, obj):
        received = obj.total_received
        ordered = obj.quantity_ordered
        if received >= ordered:
            color = "green"
        elif received > 0:
            color = "orange"
        else:
            color = "red"
        return format_html('<b style="color: {};">{} из {}</b>', color, received, ordered)