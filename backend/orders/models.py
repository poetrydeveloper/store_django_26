import uuid
from django.db import models
from products.models import Product

class Counterparty(models.Model):
    """Поставщики и Клиенты"""
    name = models.CharField(max_length=255, verbose_name="Наименование")
    is_supplier = models.BooleanField(default=True, verbose_name="Поставщик")
    is_customer = models.BooleanField(default=False, verbose_name="Клиент")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"

class Order(models.Model):
    """Заявка на поставку"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Counterparty, on_delete=models.PROTECT, verbose_name="Поставщик")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    
    quantity_ordered = models.PositiveIntegerField(default=1, verbose_name="Заказано (шт)")
    quantity_received = models.PositiveIntegerField(default=0, verbose_name="Получено (шт)")
    
    is_custom_order = models.BooleanField(default=False, verbose_name="Заказной товар")
    # Если товар заказной, привязываем клиента
    customer = models.ForeignKey(
        Counterparty, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name="customer_orders", verbose_name="Клиент-заказчик"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заявка #{self.id} на {self.product.name}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
