from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Управление заказами'

    def ready(self):
        # Мы больше не импортируем сигналы здесь, 
        # так как логика переехала в приложение deliveries
        pass 
