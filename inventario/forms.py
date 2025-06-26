print("<<<<< inventario/forms.py cargado CORRECTAMENTE  SIN EL UNIQUE>>>>>")

from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Movimiento, MovimientoDetalle, Bodega, Stock, Editorial, Autor
from django.core.exceptions import ValidationError

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['titulo', 'tipo', 'editorial', 'autores', 'descripcion']
        widgets = {
            'autores': forms.SelectMultiple(),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'titulo': 'Título del producto*',
            'tipo': 'Tipo de producto*',
            'editorial': 'Editorial*',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['editorial'].queryset = Editorial.objects.all().order_by('nombre')

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['bodega_origen', 'bodega_destino']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['bodega_origen'].queryset = Bodega.objects.filter(
                stocks__cantidad__gt=0
            ).distinct().order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('bodega_origen') == cleaned_data.get('bodega_destino'):
            raise forms.ValidationError("Las bodegas de origen y destino deben ser diferentes")
        return cleaned_data

class MovimientoDetalleForm(forms.ModelForm):
    class Meta:
        model = MovimientoDetalle
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        self.bodega_origen_instance = kwargs.pop('bodega_origen_instance', None)
        super().__init__(*args, **kwargs)
        
        self.fields['producto'].queryset = Producto.objects.none() 
        
        if self.bodega_origen_instance:
             self.fields['producto'].queryset = Producto.objects.filter(
                stocks__bodega=self.bodega_origen_instance,
                stocks__cantidad__gt=0
            ).distinct().order_by('titulo')

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        producto = self.cleaned_data.get('producto')
        
        bodega_origen = self.bodega_origen_instance 
        if not bodega_origen and self.instance and self.instance.movimiento and self.instance.movimiento.pk:
            bodega_origen = self.instance.movimiento.bodega_origen
        
        if producto and bodega_origen:
            stock = Stock.objects.filter(
                producto=producto,
                bodega=bodega_origen
            ).first()
            if stock is None:
                raise forms.ValidationError(
                    f"El producto '{producto.titulo}' no tiene stock registrado en la bodega de origen seleccionada."
                )
            if cantidad > stock.cantidad:
                raise forms.ValidationError(
                    f"Stock insuficiente. Máximo disponible de '{producto.titulo}': {stock.cantidad}"
                )
        elif producto:
            raise forms.ValidationError("No se pudo determinar la bodega de origen para validar el stock del producto. Por favor, selecciona una bodega de origen válida.")
            
        return cantidad

MovimientoDetalleFormSet = inlineformset_factory(
    Movimiento, 
    MovimientoDetalle, 
    form=MovimientoDetalleForm,
    extra=1, 
    can_delete=True 
)

# Formulario para la gestión de stock manual (sumar/restar)
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['bodega', 'producto', 'cantidad']
        labels = {
            'bodega': 'Bodega*',
            'producto': 'Producto*',
            'cantidad': 'Cantidad a Añadir/Restar*', 
        }
        # unique_together = [] # Puedes quitar esta línea si lo deseas, validate_unique es más explícito
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bodega'].queryset = Bodega.objects.all().order_by('nombre')
        self.fields['producto'].queryset = Producto.objects.all().order_by('titulo')
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad == 0:
            raise forms.ValidationError("La cantidad a añadir/restar no puede ser cero.")
        return cantidad

    # ¡IMPORTANTE! Sobreescribimos este método para deshabilitar la validación de unique_together
    # Esto le dice al ModelForm que NO ejecute la validación de unicidad del modelo.
    def validate_unique(self):
        pass # No hacemos nada aquí, deshabilitando la validación de unicidad del formulario


class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre de la Editorial*',
        }

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre', 'apellido']
        labels = {
            'nombre': 'Nombre del Autor*',
            'apellido': 'Apellido del Autor*',
        }

class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'direccion']
        labels = {
            'nombre': 'Nombre de la Bodega*',
            'direccion': 'Dirección',
        }

class InformeStockForm(forms.Form):
    bodega = forms.ModelChoiceField(
        queryset=Bodega.objects.all().order_by('nombre'),
        required=False,
        label="Filtrar por Bodega"
    )
    editorial = forms.ModelChoiceField(
        queryset=Editorial.objects.all().order_by('nombre'),
        required=False,
        label="Filtrar por Editorial"
    )
