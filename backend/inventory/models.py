# app/inventory/models.py
import uuid
from django.db import models
from django.utils import timezone

class ProductUnit(models.Model):
    """Конкретный экземпляр товара на складе (Инвентарная единица)"""
    
    class ProductUnitCardStatus(models.TextChoices):
        """Статус документооборота"""
        CANDIDATE_IN_REQUEST = 'CANDIDATE_IN_REQUEST', 'Кандидат в заявку'  # нужен заказ
        IN_REQUEST = 'IN_REQUEST', 'В заявке'          # заказали у поставщика
        IN_DELIVERY = 'IN_DELIVERY', 'В доставке'     # поставщик отправил
        ARRIVED = 'ARRIVED', 'Прибыл'                 # товар на складе
    
    class ProductUnitPhysicalStatus(models.TextChoices):
        """Физическое состояние товара"""
        NOT_ARRIVED = 'NOT_ARRIVED', 'Ещё не прибыл'
        IN_STORE = 'IN_STORE', 'На складе'
        SOLD = 'SOLD', 'Продан'
        CREDIT = 'CREDIT', 'В кредит'
        LOST = 'LOST', 'Потерян'
        IN_DISASSEMBLED = 'IN_DISASSEMBLED', 'Разобран'
        IN_COLLECTED = 'IN_COLLECTED', 'Собран'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # --- Основные связи ---
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        related_name="units", 
        verbose_name="Товар"
    )
    
    # Ссылаемся на позицию в заявке
    source_order_item = models.ForeignKey(
        'orders.OrderItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="units",
        verbose_name="Позиция в заявке"
    )
    
    # --- Цены ---
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Цена закупки (ед)"
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Цена продажи"
    )
    
    # --- Статусы ---
    status_card = models.CharField(
        max_length=30, 
        choices=ProductUnitCardStatus.choices, 
        default=ProductUnitCardStatus.CANDIDATE_IN_REQUEST,
        verbose_name="Статус документооборота"
    )
    status_physical = models.CharField(
        max_length=30, 
        choices=ProductUnitPhysicalStatus.choices, 
        default=ProductUnitPhysicalStatus.NOT_ARRIVED,
        verbose_name="Физический статус"
    )
    on_stock = models.BooleanField(default=False, verbose_name="На складе")
    
    # --- Контрагенты (ИСПРАВЛЕНО: теперь Supplier и Customer) ---
    supplier = models.ForeignKey(
        'orders.Supplier', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='supplied_units',
        verbose_name="Поставщик"
    )
    customer = models.ForeignKey(
        'orders.Customer', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='customer_units',
        verbose_name="Покупатель (если предзаказ)"
    )
    
    # --- Даты ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата приёмки")
    sold_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата продажи")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата возврата")
    credit_paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты кредита")
    
    # --- Кэшированные поля ---
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Серийный номер")
    product_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Код товара (кэш)")
    product_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Название товара (кэш)")
    
    # --- Вспомогательные свойства ---
    @property
    def source_order(self):
        """Возвращаем заявку через OrderItem"""
        return self.source_order_item.order if self.source_order_item else None
    
    def __str__(self):
        sn = f" SN:{self.serial_number}" if self.serial_number else ""
        return f"{self.product.name} [{str(self.id)[:8]}{sn}]"
    
    def save(self, *args, **kwargs):
        # Кэшируем данные товара при сохранении
        if self.product:
            self.product_code = self.product.code
            self.product_name = self.product.name
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Единица товара"
        verbose_name_plural = "Единицы товара"
        ordering = ['-created_at']