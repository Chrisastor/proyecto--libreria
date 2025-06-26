from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Movimiento, MovimientoDetalle, Stock


@receiver(post_save, sender=Movimiento)
def actualizar_stock(sender, instance, created, **kwargs):
    if created:
        for detalle in instance.detalles.all():
            # Reducir stock en bodega origen
            stock_origen, _ = Stock.objects.get_or_create(
                bodega=instance.bodega_origen,
                producto=detalle.producto,
                defaults={'cantidad': 0}
            )
            if stock_origen.cantidad < detalle.cantidad:
                raise ValidationError(f'Stock insuficiente de {detalle.producto.titulo} en bodega origen.')

            stock_origen.cantidad -= detalle.cantidad
            stock_origen.save()

            # Aumentar stock en bodega destino
            stock_destino, _ = Stock.objects.get_or_create(
                bodega=instance.bodega_destino,
                producto=detalle.producto,
                defaults={'cantidad': 0}
            )
            stock_destino.cantidad += detalle.cantidad
            stock_destino.save()

