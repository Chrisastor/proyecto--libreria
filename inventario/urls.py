from django.urls import path
from . import views
from .views import DetalleMovimientoView 

urlpatterns = [

    # URLs para Productos
    path('productos/', views.listado_productos, name='listado_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # URLs para Autores
    path('autores/', views.listado_autores, name='listado_autores'),
    path('autores/crear/', views.crear_autor, name='crear_autor'),
    path('autores/editar/<int:pk>/', views.editar_autor, name='editar_autor'),
    path('autores/eliminar/<int:pk>/', views.eliminar_autor, name='eliminar_autor'),

    # URLs para Editoriales
    path('editoriales/', views.listado_editoriales, name='listado_editoriales'),
    path('editoriales/crear/', views.crear_editorial, name='crear_editorial'),
    path('editoriales/editar/<int:pk>/', views.editar_editorial, name='editar_editorial'),
    path('editoriales/eliminar/<int:pk>/', views.eliminar_editorial, name='eliminar_editorial'),

    # URLs para Bodegas
    path('bodegas/', views.listado_bodegas, name='listado_bodegas'),
    path('bodegas/crear/', views.crear_bodega, name='crear_bodega'),
    path('bodegas/editar/<int:pk>/', views.editar_bodega, name='editar_bodega'),
    path('bodegas/eliminar/<int:pk>/', views.eliminar_bodega, name='eliminar_bodega'),

    # URLs para Movimientos
    path('movimientos/', views.listado_movimientos, name='listado_movimientos'),
    path('movimientos/crear/', views.crear_movimiento, name='crear_movimiento'),
    path('movimientos/<int:pk>/', DetalleMovimientoView.as_view(), name='detalle_movimiento'),
    path('movimientos/<int:pk>/pdf/', views.generar_pdf_movimiento, name='generar_pdf_movimiento'),

    # URLs para Informes
    path('informes/stock/', views.informe_stock, name='informe_stock'),
    path('informes/movimientos/', views.informe_movimientos, name='informe_movimientos'),
    path('informes/exportar/', views.exportar_informe, name='exportar_informe'),

    # URL para Stock (Asegúrate de que este path sea 'stock/' para que coincida con lo que esperas)
    path('stock/', views.listado_stock, name='listado_stock'), 

    # URL para HTMX (obtener productos por bodega)
    path('get-productos-bodega/', views.get_productos_bodega_htmx, name='get_productos_bodega_htmx'),
]
