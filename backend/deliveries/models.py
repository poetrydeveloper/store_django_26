import uuid
from django.db import models
from django.core.exceptions import ValidationError
from orders.models import Order

class Delivery(models.Model):
    """Документ приемки товара на склад"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="deliveries",
        verbose_name="Заказ-основание"
    )
    
    quantity_received = models.PositiveIntegerField(verbose_name="Количество получено (шт)")
    
    # Делаем поле необязательным для ввода (blank=True), чтобы оно заполнялось само
    actual_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Фактическая цена закупки (ед)",
        blank=True,
        null=True
    )
    
    delivery_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время приемки")
    comment = models.TextField(blank=True, verbose_name="Комментарий (номер накладной и т.д.)")

    def clean(self):
        """Проверка: нельзя принять больше, чем осталось допоставить по заказу"""
        if self.order:
            # Считаем, сколько уже принято по этому заказу (исключая текущую правку)
            already_received = self.order.total_received
            if self._state.adding: # Если это новая запись
                remaining = self.order.quantity_ordered - already_received
            else: # Если редактируем существующую
                old_instance = Delivery.objects.get(pk=self.pk)
                remaining = self.order.quantity_ordered - (already_received - old_instance.quantity_received)

            if self.quantity_received > remaining:
                raise ValidationError(
                    f"Ошибка! По заказу осталось принять {remaining} шт. "
                    f"Вы пытаетесь принять {self.quantity_received} шт."
                )

    def save(self, *args, **kwargs):
        # АВТОМАТИКА: Берем цену из Заявки, если она не введена вручную
        if not self.actual_price and self.order:
            self.actual_price = self.order.price
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Приход по заказу {str(self.order.id)[:8]} ({self.quantity_received} шт)"

    class Meta:
        verbose_name = "Приемка товара"
        verbose_name_plural = "Приемки товара"
