
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError

# Importa el decorador desde utils.py (LA RUTA ESTÁ BIEN ASÍ)
from .utils import grupo_permitido 
# Importa los formularios de usuario
from .forms import UserCreateForm, UserEditForm


@login_required
@grupo_permitido('Administrador de Sistema') 
def crear_usuario_view(request):
    """
    Permite a un 'Administrador de Sistema' crear nuevos usuarios y asignarles roles.
    """
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Usuario '{user.username}' creado exitosamente.")
                return redirect('listado_usuarios')
            except ValidationError as e:
                form.add_error(None, e) 
            except Exception as e:
                messages.error(request, f"Ocurrió un error inesperado al crear el usuario: {e}")
        else:
            messages.error(request, "Error al crear el usuario. Por favor, verifica los datos.")
    else:
        form = UserCreateForm()
    return render(request, 'usuarios/formulario_usuario.html', {'form': form, 'action': 'crear'})

@login_required
@grupo_permitido('Administrador de Sistema') 
def editar_usuario_view(request, pk):
    """
    Permite a un 'Administrador de Sistema' editar usuarios existentes.
    """
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Usuario '{user.username}' actualizado exitosamente.")
                return redirect('listado_usuarios')
            except ValidationError as e:
                form.add_error(None, e)
            except Exception as e:
                messages.error(request, f"Ocurrió un error inesperado al editar el usuario: {e}")
        else:
            messages.error(request, "Error al editar el usuario. Por favor, verifica los datos.")
    else:
        form = UserEditForm(instance=usuario)
    return render(request, 'usuarios/formulario_usuario.html', {'form': form, 'usuario': usuario, 'action': 'editar'})


# Vistas de redirección y dashboards
@login_required
def redireccionar_dashboard(request):
    """
    Redirige al usuario al dashboard correcto basado en su rol.
    Prioridad: Administrador de Sistema > Superusuario (Django) > Jefe de Bodega > Bodeguero > Otros.
    """
    user = request.user
    # 1. Prioridad para el nuevo rol 'Administrador de Sistema'
    if user.groups.filter(name='Administrador de Sistema').exists():
        return redirect('dashboard_admin') 
    # 2. Superusuario de Django (si quieres que tenga un dashboard diferente al 'Administrador de Sistema')
    elif user.is_superuser:
        return redirect('dashboard_admin') # Puedes cambiar esto si quieres un dashboard solo para superuser
    # 3. Roles específicos de tu aplicación
    elif user.groups.filter(name='Jefe de Bodega').exists():
        return redirect('dashboard_jefe_bodega')
    elif user.groups.filter(name='Bodeguero').exists():
        return redirect('dashboard_bodeguero')
    # 4. Otro grupo si lo tienes definido explícitamente
    elif user.groups.filter(name='otros').exists(): # Si tienes un grupo 'otros'
        return redirect('dashboard_otro_usuario')
    else:
        # Fallback para usuarios autenticados sin un rol específico asignado
        messages.warning(request, "No tienes un rol específico asignado. Accediendo al dashboard general.")
        return redirect('dashboard_general') # Redirige al dashboard general

# Dashboards específicos (ahora protegidos por decoradores si es necesario)
@login_required
@grupo_permitido('Administrador de Sistema') # Solo Administrador de Sistema puede acceder a este dashboard
def dashboard_admin(request):
    """
    Dashboard para el rol 'Administrador de Sistema'.
    Contendrá enlaces a todas las funcionalidades, incluida la gestión de usuarios.
    """
    return render(request, 'usuarios/dashboard_admin.html')

@login_required
@grupo_permitido('Bodeguero') # Solo Bodeguero (y Administrador de Sistema) puede acceder
def dashboard_bodeguero(request):
    """
    Dashboard para el Bodeguero.
    """
    return render(request, 'usuarios/dashboard_bodeguero.html')

@login_required
@grupo_permitido('Jefe de Bodega') # Solo Jefe de Bodega (y Administrador de Sistema) puede acceder
def dashboard_jefe_bodega(request):
    """
    Dashboard para el Jefe de Bodega.
    """
    return render(request, 'usuarios/dashboard_jefe_bodega.html')

@login_required
@grupo_permitido('otros') # Si tienes un grupo 'otros' que ve este dashboard
def dashboard_otro_usuario(request):
    """
    Dashboard para usuarios que pertenecen al grupo 'otros'.
    """
    return render(request, 'usuarios/dashboard_otro_usuario.html')

@login_required
def dashboard_general(request):
    """
    Dashboard genérico para usuarios sin un rol específico o como fallback.
    """
    return render(request, 'usuarios/dashboard_general.html')


# Vistas para la Gestión de Usuarios (Accesibles solo por 'Administrador de Sistema')
@login_required
@grupo_permitido('Administrador de Sistema') 
def listado_usuarios_view(request):
    """
    Muestra un listado de todos los usuarios del sistema.
    """
    usuarios = User.objects.all().order_by('username')
    return render(request, 'usuarios/listado_usuarios.html', {'usuarios': usuarios})

@login_required
@grupo_permitido('Administrador de Sistema') 
def eliminar_usuario_view(request, pk):
    """
    Permite a un 'Administrador de Sistema' eliminar usuarios.
    Contiene validaciones para proteger superusuarios y auto-eliminación.
    """
    usuario = get_object_or_404(User, pk=pk)
    
    # Validaciones de seguridad
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar a un superusuario.")
        return redirect('listado_usuarios')
    
    if request.user.pk == usuario.pk:
        messages.error(request, "No puedes eliminar tu propia cuenta desde aquí.")
        return redirect('listado_usuarios')
    
    if request.method == 'POST': 
        try:
            with transaction.atomic():
                usuario.delete()
            messages.success(request, f"Usuario '{usuario.username}' eliminado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {e}")
    else:
        # Si alguien intenta acceder directamente por GET, mostramos la confirmación.
        return render(request, 'usuarios/confirm_delete_usuario.html', {'usuario': usuario}) 

    return redirect('listado_usuarios')