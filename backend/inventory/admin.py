from django.contrib import admin
from .models import ProductUnit

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    # Добавляем цену и заказ в список, чтобы видеть всю картину сразу
    list_display = (
        'short_id', 
        'product', 
        'purchase_price',  # Видим цену закупки
        'on_stock', 
        'source_order_link', # Видим ссылку на заказ
        'created_at'
    )
    
    # Фильтры: добавили фильтр по наличию и дате приемки
    list_filter = ('on_stock', 'created_at', 'product__brand')
    
    # Поиск: добавили поиск по ID и названию товара
    search_fields = ('id', 'product__name', 'product__code')
    
    # Поля только для чтения
    readonly_fields = ('id', 'created_at', 'source_order', 'purchase_price')

    # Удобная группировка полей в карточке юнита
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'product', 'on_stock')
        }),
        ('Экономика и происхождение', {
            'fields': ('purchase_price', 'source_order', 'created_at'),
            'description': "Данные заполняются автоматически при приемке товара по заявке."
        }),
    )

    # Метод для красивого отображения короткого ID
    @admin.display(description="ID Юнита")
    def short_id(self, obj):
        return str(obj.id)[:8]

    # Метод для отображения ссылки на заказ (если он есть)
    @admin.display(description="Заказ-основание")
    def source_order_link(self, obj):
        if obj.source_order:
            return f"Заявка #{str(obj.source_order.id)[:8]}"
        return "—"

    # Запрещаем создавать юниты вручную через админку (они должны лететь из Заявок)
    # Если хочешь оставить возможность ручного создания, просто удали этот метод
    def has_add_permission(self, request):
        return False 
