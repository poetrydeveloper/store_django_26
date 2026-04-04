from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem
from inventory.models import ProductUnit

@receiver(post_save, sender=OrderItem)
def create_units_on_order_item(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.units.exists():
        return
    
    units = []
    for _ in range(instance.quantity_ordered):
        units.append(
            ProductUnit(
                product=instance.product,
                source_order_item=instance,
                purchase_price=instance.price,
                status_card=ProductUnit.ProductUnitCardStatus.IN_REQUEST,
                status_physical=ProductUnit.ProductUnitPhysicalStatus.NOT_ARRIVED,
                on_stock=False,
                supplier=instance.order.supplier,
                customer=instance.order.customer,
            )
        )
    ProductUnit.objects.bulk_create(units)