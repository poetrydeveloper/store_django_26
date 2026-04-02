import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
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
    """Заявка на поставку (План закупки)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Counterparty, 
        on_delete=models.PROTECT, 
        limit_choices_to={'is_supplier': True},
        verbose_name="Поставщик"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Ориентировочная цена (ед)"
    )
    
    quantity_ordered = models.PositiveIntegerField(default=1, verbose_name="Заказано (шт)")
    
    is_custom_order = models.BooleanField(default=False, verbose_name="Заказной товар")
    customer = models.ForeignKey(
        Counterparty, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'is_customer': True},
        related_name="customer_orders", 
        verbose_name="Клиент-заказчик"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def clean(self):
        """Валидация черновика заявки"""
        # Защита от дублей при случайном двойном клике (в пределах 1 минуты)
        duplicate = Order.objects.filter(
            supplier=self.supplier,
            product=self.product,
            quantity_ordered=self.quantity_ordered,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).exclude(id=self.id).exists()

        if duplicate:
            raise ValidationError("Похожая заявка уже создана минуту назад.")

    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Подтягиваем цену из продукта, если не указана вручную
        if self.price == 0 and self.product:
            try:
                self.price = getattr(self.product, 'price', 0.00)
            except AttributeError:
                pass
        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        """Планируемая сумма закупки"""
        return self.quantity_ordered * self.price

    @property
    def total_received(self):
        """Считает общее количество реально полученного товара по всем актам приемки"""
        # Эта функция будет ходить в приложение deliveries и суммировать приходы
        return self.deliveries.aggregate(models.Sum('quantity_received'))['quantity_received__sum'] or 0

    def __str__(self):
        return f"Заявка #{str(self.id)[:8]} | {self.product.name} ({self.quantity_ordered} шт)"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
