import uuid
from django.db import models

class ProductUnit(models.Model):
    """Конкретный экземпляр товара на складе (Инвентарная единица)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Ссылка на карточку товара из приложения products
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        related_name="units", 
        verbose_name="Товар"
    )
    
    # Ссылка на заказ из приложения orders, по которому пришел этот юнит
    source_order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="units",
        verbose_name="Заказ-основание"
    )
    
    on_stock = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата приемки")

    def __str__(self):
        return f"{self.product.name} (Unit: {self.id})"

    class Meta:
        verbose_name = "Единица товара"
        verbose_name_plural = "Единицы товара"
