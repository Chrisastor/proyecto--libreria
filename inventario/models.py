from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

class Editorial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    class Meta:
        unique_together = ('nombre', 'apellido')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Producto(models.Model):
    TIPOS_PRODUCTO = [
        ('LIBRO', 'Libro'),
        ('REVISTA', 'Revista'),
        ('DVD', 'DVD'),
        ('CD', 'CD'),
        ('OTRO', 'Otro'),
    ]
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPOS_PRODUCTO)
    editorial = models.ForeignKey(Editorial, on_delete=models.SET_NULL, null=True, blank=True)
    autores = models.ManyToManyField(Autor, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"

class Bodega(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Stock(models.Model):
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='stocks')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('bodega', 'producto')
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return f"{self.cantidad} unidades de {self.producto.titulo} en {self.bodega.nombre}"
    
    @staticmethod
    def actualizar_stock(bodega, producto, cantidad):
        stock_entry, created = Stock.objects.select_for_update().get_or_create(
            bodega=bodega,
            producto=producto,
            defaults={'cantidad': 0}
        )
        stock_entry.cantidad += cantidad
        if stock_entry.cantidad < 0:
            raise ValidationError(
                f"Stock insuficiente para {producto.titulo} en {bodega.nombre}. "
                f"Cantidad actual: {stock_entry.cantidad - cantidad}. Intento de reducir en: {cantidad}."
            )
        stock_entry.save()

class Movimiento(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('TRASLADO', 'Traslado'),
    ]
    
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='movimientos_salida', null=True, blank=True)
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='movimientos_entrada', null=True, blank=True)
    
    tipo_movimiento = models.CharField(max_length=10, editable=False, default='TRASLADO')

    def save(self, *args, **kwargs):
        if not self.bodega_origen and self.bodega_destino:
            self.tipo_movimiento = 'ENTRADA'
        elif self.bodega_origen and not self.bodega_destino:
            self.tipo_movimiento = 'SALIDA'
        elif self.bodega_origen and self.bodega_destino:
            self.tipo_movimiento = 'TRASLADO'
        else:
            raise ValidationError("Un movimiento debe tener al menos una bodega de origen o destino.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Movimiento #{self.id} de {self.tipo_movimiento} el {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class MovimientoDetalle(models.Model):
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        unique_together = ('movimiento', 'producto')
        verbose_name = "Detalle de Movimiento"
        verbose_name_plural = "Detalles de Movimiento"

    def __str__(self):
        return f"{self.cantidad} de {self.producto.titulo} en Movimiento #{self.movimiento.id}"
