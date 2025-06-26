from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm # Importa UserCreationForm y UserChangeForm

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
        # UserCreationForm ya los tiene en su `fields` por defecto si los añades a Meta.
        # Si no aparecen por defecto, puedes añadirlos aquí, pero no es lo usual.
        # Por simplicidad y para evitar duplicidad, los campos 'first_name' y 'last_name'
        # deberían ser gestionados por la lista 'fields' en Meta.
        # Si quieres que sean opcionales en UserCreationForm, puedes hacer esto:
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
            # Guardar las relaciones ManyToMany (grupos) después de que el usuario sea guardado
            if self.cleaned_data.get('groups') is not None: 
                user.groups.set(self.cleaned_data['groups'])
            else:
                user.groups.clear() # Si no se seleccionan grupos, asegúrate de que no tenga ninguno

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
        # Puedes añadir más personalizaciones para campos aquí si es necesario
        # Por ejemplo, hacer el email opcional para edición si lo permites
        # self.fields['email'].required = False 

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Guardar las relaciones ManyToMany (grupos)
            if self.cleaned_data.get('groups') is not None:
                user.groups.set(self.cleaned_data['groups'])
            # else: user.groups.clear() # No borrar todos los grupos si el campo no se envía (caso de PATCH o si se omite)
        return user
