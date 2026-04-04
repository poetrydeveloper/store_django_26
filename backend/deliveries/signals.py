#app/deliveries/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import DeliveryItem
from inventory.models import ProductUnit

@receiver(post_save, sender=DeliveryItem)
def update_units_on_delivery_item(sender, instance, created, **kwargs):
    """При создании позиции приемки обновляем существующие ProductUnit"""
    if not created:
        return
    
    # Находим единицы товара по этой позиции заявки, которые ещё не на складе
    units_to_update = ProductUnit.objects.filter(
        source_order_item=instance.order_item,
        on_stock=False
    )[:instance.quantity_received]
    
    for unit in units_to_update:
        unit.on_stock = True
        unit.purchase_price = instance.actual_price
        unit.status_card = ProductUnit.ProductUnitCardStatus.ARRIVED
        unit.status_physical = ProductUnit.ProductUnitPhysicalStatus.IN_STORE
        unit.received_at = timezone.now()
        unit.save()