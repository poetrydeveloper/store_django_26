from django.apps import AppConfig

class DeliveriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deliveries'
    verbose_name = 'Приемка товаров'

    def ready(self):
        # Вот здесь теперь живет магия создания товара!
        import deliveries.signals 
