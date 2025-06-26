from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from inventario.models import Bodega, Producto, Movimiento

@receiver(post_migrate)
def crear_grupos(sender, **kwargs):
    if sender.name == "usuarios":

        # Jefe de Bodega
        jefe_group, _ = Group.objects.get_or_create(name='Jefe de Bodega')
        jefe_perms = Permission.objects.filter(
            content_type__model__in=['bodega', 'producto']
        )
        jefe_group.permissions.set(jefe_perms)

        # Bodeguero
        bodeguero_group, _ = Group.objects.get_or_create(name='Bodeguero')
        bodeguero_perms = Permission.objects.filter(
            content_type__model='movimiento'
        )
        bodeguero_group.permissions.set(bodeguero_perms)

        # Admin (todos los permisos por defecto)

        print("✔️ Grupos creados o actualizados.")
