from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm # Importa UserChangeForm

# --- Formulario para CREAR NUEVOS Usuarios ---
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    # Cambiamos el nombre del campo a 'groups' para que coincida con el modelo User
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by('name'), # Ordenar grupos
        required=False, # Los grupos no son obligatorios al crear
        widget=forms.CheckboxSelectMultiple,
        label="Roles/Grupos"
    )

    class Meta(UserCreationForm.Meta): # Hereda de UserCreationForm.Meta
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'groups'] # Añade first_name y last_name
        # 'password' y 'password2' ya vienen de UserCreationForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir first_name y last_name para que aparezcan en el formulario de creación
        self.fields['first_name'] = forms.CharField(max_length=150, required=False, label="Nombre")
        self.fields['last_name'] = forms.CharField(max_length=150, required=False, label="Apellido")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
            # Guardar las relaciones ManyToMany (grupos) después de que el usuario sea guardado
            # save_m2m() es llamado automáticamente por ModelForm en save() si commit=True
            # Para UserCreationForm, lo hacemos explícitamente si manejamos M2M custom
            if self.cleaned_data.get('groups'):
                user.groups.set(self.cleaned_data['groups'])
            else:
                user.groups.clear()
        return user

# --- Formulario para EDITAR Usuarios EXISTENTES (sin cambiar contraseña) ---
class UserEditForm(forms.ModelForm):
    # Campo para seleccionar grupos
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Roles/Grupos"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'groups']
        labels = {
            'username': 'Nombre de Usuario*',
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'is_active': 'Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un usuario existente, pre-seleccionar sus grupos
        if self.instance and self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()
        # Eliminar el campo de password de la edición si no lo necesitamos
        # self.fields.pop('password', None) # Esto es si Meta tuviera 'password'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # save_m2m() es llamado automáticamente por ModelForm en save() si commit=True
            # Si el formulario es un ModelForm (como este UserEditForm), se encarga de M2M
            if self.cleaned_data.get('groups') is not None: # Verifica si el campo 'groups' fue enviado
                user.groups.set(self.cleaned_data['groups'])
            # else: user.groups.clear() # No borrar todos los grupos si el campo no se envía (caso de PATCH)
        return user
