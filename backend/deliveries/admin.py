from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    # Что видим в общей таблице приемок
    list_display = (
        'short_id', 
        'get_product', 
        'get_supplier', 
        'quantity_received', 
        'actual_price', 
        'delivery_date'
    )
    
    # Фильтры справа (по дате и по поставщику из заказа)
    list_filter = ('delivery_date', 'order__supplier')
    
    # Поиск по товару, накладной или ID
    search_fields = ('order__product__name', 'comment', 'id')
    
    # Цена и дата заполняются автоматически, делаем их "только для чтения" в форме
    readonly_fields = ('delivery_date', 'actual_price')

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Связь с заказом', {
            'fields': ('order',)
        }),
        ('Данные поставки', {
            'description': "Цена за единицу подтянется из заявки автоматически при сохранении.",
            'fields': (('quantity_received', 'actual_price'), 'comment', 'delivery_date')
        }),
    )

    # --- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ---

    @admin.display(description="ID Приемки")
    def short_id(self, obj):
        return str(obj.id)[:8]

    @admin.display(description="Товар")
    def get_product(self, obj):
        return obj.order.product.name

    @admin.display(description="Поставщик")
    def get_supplier(self, obj):
        return obj.order.supplier.name

    # Метод, чтобы при создании новой приемки цена сразу отображалась, если заказ выбран
    # (но сработает полностью только после нажатия Save)
    def save_model(self, request, obj, form, change):
        if not obj.actual_price and obj.order:
            obj.actual_price = obj.order.price
        super().save_model(request, obj, form, change)
