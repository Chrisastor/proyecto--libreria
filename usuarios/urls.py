# PROYECTO TALLER/usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta es la URL a la que LOGIN_REDIRECT_URL apunta desde settings.py
    path('dashboard_redirect/', views.redireccionar_dashboard, name='dashboard_redirect'),

    # URLs de los dashboards específicos
    path('dashboard/jefe_bodega/', views.dashboard_jefe_bodega, name='jefe_bodega_dashboard'),
    path('dashboard/bodeguero/', views.dashboard_bodeguero, name='bodeguero_dashboard'),
    # CUIDADO: La vista es views.dashboard_admin, así que su nombre de URL debería ser 'dashboard_admin'
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'), # ¡CAMBIADO AQUÍ!
    path('dashboard/otro_usuario/', views.dashboard_otro_usuario, name='dashboard_otro_usuario'), # Si tienes este grupo/dashboard

    # URLs para Gestión de Usuarios
    path('listado/', views.listado_usuarios_view, name='listado_usuarios'),
    path('crear/', views.crear_usuario_view, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario_view, name='editar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario_view, name='eliminar_usuario'),
]
    

