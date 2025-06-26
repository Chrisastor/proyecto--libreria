# PROYECTO TALLER/usuarios/utils.py

from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

def grupo_permitido(*grupos_requeridos):
    """
    Decorador que verifica si el usuario pertenece a alguno de los grupos requeridos.
    Si el usuario es un superusuario o parte del grupo 'Administrador de Sistema',
    se le concede acceso universal.
    """
    if not isinstance(grupos_requeridos, (list, tuple)):
        grupos_requeridos = [grupos_requeridos]

    def decorator(view_func):
        # NOTA: Tus vistas ya tienen @login_required, así que este decorador se ejecuta después de la autenticación.
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Permiso universal para Superusuarios O Administradores de Sistema
                # ESTA ES LA LÍNEA CRÍTICA CORREGIDA:
                if request.user.is_superuser or request.user.groups.filter(name='Administrador de Sistema').exists():
                    return view_func(request, *args, **kwargs)

                # Si no es Superusuario ni Administrador de Sistema,
                # comprobar los grupos específicos que requiere la vista
                for group_name in grupos_requeridos:
                    if request.user.groups.filter(name=group_name).exists():
                        return view_func(request, *args, **kwargs)
                
                # Si el usuario está autenticado pero no tiene los grupos requeridos, denegar acceso.
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect(reverse('home')) # Redirige al home o a una página de acceso denegado
            else:
                # Si el usuario no está autenticado, redirigir al login
                messages.warning(request, "Por favor, inicia sesión para acceder a esta página.")
                return redirect(f"{reverse('login')}?next={request.path}")
        return wrap
    return decorator

# Función auxiliar para obtener el grupo o crearlo si no existe
def get_or_create_group(group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Grupo '{group_name}' creado.")
    return group