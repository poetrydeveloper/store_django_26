#ORDRS/MODEL
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from products.models import Product


class Supplier(models.Model):
    """Поставщик (у кого закупаем)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Наименование")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class Customer(models.Model):
    """Клиент (кто заказал товар)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    def __str__(self):
        return f"{self.name} ({self.phone})"

    @property
    def purchase_history(self):
        """История покупок клиента (проданные ProductUnit)"""
        from inventory.models import ProductUnit
        return ProductUnit.objects.filter(
            customer=self,
            status_physical=ProductUnit.ProductUnitPhysicalStatus.SOLD
        ).select_related('product').order_by('-sold_at')
    
    def get_purchase_history_dates(self):
        """Список дат покупок"""
        return self.purchase_history.values_list('sold_at', flat=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Order(models.Model):
    """Заявка на поставку (План закупки) — у поставщика"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT, 
        verbose_name="Поставщик"
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Клиент (если предзаказ)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_custom_order = models.BooleanField(default=False, verbose_name="Заказ под клиента")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    
    def __str__(self):
        return f"Заявка #{str(self.id)[:8]} | {self.supplier.name}"
    
    @property
    def total_cost(self):
        """Общая сумма заявки"""
        return sum(item.total_cost for item in self.items.all())
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Товарная позиция в заявке"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Заявка"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Товар"
    )
    
    quantity_ordered = models.PositiveIntegerField(default=1, verbose_name="Заказано (шт)")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Цена закупки (ед)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def clean(self):
        """Защита от дублей в рамках одной заявки"""
        if OrderItem.objects.filter(order=self.order, product=self.product).exclude(id=self.id).exists():
            raise ValidationError(f"Товар '{self.product.name}' уже добавлен в эту заявку")
        
        # Защита от случайного двойного клика (в пределах 1 минуты)
        duplicate = OrderItem.objects.filter(
            order=self.order,
            product=self.product,
            quantity_ordered=self.quantity_ordered,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).exclude(id=self.id).exists()
        
        if duplicate:
            raise ValidationError("Похожая позиция уже создана минуту назад.")
    
    def save(self, *args, **kwargs):
        if self.price == 0 and self.product:
            # Можно подтягивать цену из последней закупки
            pass
        super().save(*args, **kwargs)
    
    @property
    def total_cost(self):
        """Сумма по позиции"""
        return self.quantity_ordered * self.price
    
    @property
    def total_received(self):
        """Общее количество полученного товара по этой позиции"""
        return self.delivery_items.aggregate(models.Sum('quantity_received'))['quantity_received__sum'] or 0
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity_ordered}"
    
    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявок"
        ordering = ['order', 'product']