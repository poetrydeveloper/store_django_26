#app/deliveries/models.py
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from orders.models import Order, OrderItem

class Delivery(models.Model):
    """Документ приемки — может принимать несколько позиций"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="deliveries",
        verbose_name="Заявка"
    )
    
    delivery_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время приемки")
    comment = models.TextField(blank=True, verbose_name="Комментарий (номер накладной и т.д.)")
    
    def __str__(self):
        return f"Приемка #{str(self.id)[:8]} | Заявка #{str(self.order.id)[:8]}"
    
    class Meta:
        verbose_name = "Приемка товара"
        verbose_name_plural = "Приемки товара"
        ordering = ['-delivery_date']


class DeliveryItem(models.Model):
    """Позиция в приёмке (конкретный товар и количество)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    delivery = models.ForeignKey(
        Delivery, 
        on_delete=models.CASCADE, 
        related_name="items",
        verbose_name="Приемка"
    )
    
    order_item = models.ForeignKey(
        OrderItem, 
        on_delete=models.CASCADE, 
        related_name="delivery_items",
        verbose_name="Позиция заявки"
    )
    
    quantity_received = models.PositiveIntegerField(verbose_name="Количество получено (шт)")
    
    actual_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Фактическая цена закупки (ед)",
        blank=True,
        null=True
    )
    
    def clean(self):
        """Проверка: нельзя принять больше, чем осталось допоставить по позиции"""
        if self.order_item:
            # Считаем, сколько уже принято по этой позиции
            already_received = self.order_item.total_received
            if self._state.adding:  # Если это новая запись
                remaining = self.order_item.quantity_ordered - already_received
            else:  # Если редактируем существующую
                old_instance = DeliveryItem.objects.get(pk=self.pk)
                remaining = self.order_item.quantity_ordered - (already_received - old_instance.quantity_received)

            if self.quantity_received > remaining:
                raise ValidationError(
                    f"Ошибка! По позиции '{self.order_item.product.name}' осталось принять {remaining} шт. "
                    f"Вы пытаетесь принять {self.quantity_received} шт."
                )
    
    def save(self, *args, **kwargs):
        # Автоматика: берем цену из позиции заявки, если не указана вручную
        if not self.actual_price and self.order_item:
            self.actual_price = self.order_item.price
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_item.product.name} x{self.quantity_received} (приемка #{str(self.delivery.id)[:8]})"
    
    class Meta:
        verbose_name = "Позиция приемки"
        verbose_name_plural = "Позиции приемки"