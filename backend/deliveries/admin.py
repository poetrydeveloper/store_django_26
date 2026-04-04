#app/deliveries/admin.py
from django.contrib import admin
from .models import Delivery, DeliveryItem
from orders.models import OrderItem

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1
    fields = ['order_item', 'quantity_received', 'actual_price']
    raw_id_fields = ['order_item']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order_item__product')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'delivery_date']
    list_filter = ['delivery_date', 'order__supplier']
    inlines = [DeliveryItemInline]
    readonly_fields = ['delivery_date']

@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'delivery', 'order_item', 'quantity_received', 'actual_price']
    list_filter = ['delivery__order__supplier']
    search_fields = ['order_item__product__name']
    raw_id_fields = ['delivery', 'order_item']