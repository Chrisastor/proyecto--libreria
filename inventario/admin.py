

from django.contrib import admin
from .models import Editorial, Autor, Producto
from .models import Bodega, Movimiento, MovimientoDetalle, Stock

admin.site.register(Editorial)
admin.site.register(Autor)
admin.site.register(Producto)


admin.site.register(Bodega)
admin.site.register(Movimiento)
admin.site.register(MovimientoDetalle)
admin.site.register(Stock)