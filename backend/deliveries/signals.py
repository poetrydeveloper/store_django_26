from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Delivery
from inventory.models import ProductUnit

@receiver(post_save, sender=Delivery)
def create_units_on_delivery(sender, instance, created, **kwargs):
    if created: # Работаем только при создании новой приемки
        new_units = [
            ProductUnit(
                product=instance.order.product,
                source_order=instance.order,
                purchase_price=instance.actual_price, # Берем цену из акта приемки!
                on_stock=True
            )
            for _ in range(instance.quantity_received)
        ]
        ProductUnit.objects.bulk_create(new_units)
