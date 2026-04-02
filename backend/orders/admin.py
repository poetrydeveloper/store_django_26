from django.contrib import admin
from django.utils.html import format_html
from .models import Counterparty, Order

@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_supplier', 'is_customer')
    list_filter = ('is_supplier', 'is_customer')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Добавили 'display_received' для отслеживания прогресса поставок
    list_display = (
        'short_id', 'product', 'supplier', 'price', 
        'quantity_ordered', 'display_received', 'get_total_cost', 
        'is_custom_order', 'created_at'
    )
    
    list_filter = ('is_custom_order', 'supplier', 'created_at')
    search_fields = ('id', 'product__name')
    
    # В fieldsets удалено поле quantity_received — теперь форма только для заказа
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'product', 'price')
        }),
        ('Количество и тип', {
            'fields': ('quantity_ordered', 'is_custom_order')
        }),
        ('Заказчик', {
            'description': "Заполняется, если товар везется под конкретного клиента",
            'fields': ('customer',)
        }),
    )

    @admin.display(description="ID Заявки")
    def short_id(self, obj):
        return str(obj.id)[:8]

    @admin.display(description="Итоговая сумма")
    def get_total_cost(self, obj):
        return f"{obj.total_cost} руб."

    @admin.display(description="Получено (факт)")
    def display_received(self, obj):
        """Отображает сколько принято товара с цветовой индикацией"""
        received = obj.total_received
        ordered = obj.quantity_ordered
        
        if received >= ordered:
            color = "green"
        elif received > 0:
            color = "orange"
        else:
            color = "red"
            
        return format_html(
            '<b style="color: {};">{} из {}</b>',
            color, received, ordered
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "supplier":
            kwargs["queryset"] = Counterparty.objects.filter(is_supplier=True)
        if db_field.name == "customer":
            kwargs["queryset"] = Counterparty.objects.filter(is_customer=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
