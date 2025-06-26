from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponse
from django.core.exceptions import ValidationError
from usuarios.utils import grupo_permitido # Asegúrate de que esta importación sea correcta

from .models import Producto, Stock, Movimiento, Autor, Bodega, Editorial
from .forms import (ProductoForm, MovimientoForm, 
                    MovimientoDetalleFormSet, AutorForm, 
                    BodegaForm, InformeStockForm,
                    EditorialForm, StockForm) 
from django.views.generic import DetailView
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from io import BytesIO 

def home_view(request):
    # Obtener los 5 últimos movimientos de bodega
    ultimos_movimientos = Movimiento.objects.select_related(
        'bodega_origen', 'bodega_destino', 'usuario'
    ).order_by('-fecha')[:5]

    # Obtener los 5 productos más recientes (asumiendo que un ID más alto es más reciente)
    ultimos_productos = Producto.objects.select_related('editorial').order_by('-id')[:5]

    context = {
        'ultimos_movimientos': ultimos_movimientos,
        'ultimos_productos': ultimos_productos
    }
    # Esto buscará 'home.html' directamente en las carpetas configuradas en TEMPLATES DIRS
    return render(request, 'home.html', context)


@login_required
@grupo_permitido('Jefe de Bodega')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/productos/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listado_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/productos/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            producto.delete()
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
    return redirect('listado_productos')

@login_required
def listado_productos(request):
    productos = Producto.objects.annotate(
        total_stock=Sum('stocks__cantidad')
    ).select_related('editorial')
    return render(request, 'inventario/productos/listado.html', {
        'productos': productos
    })

@login_required
@grupo_permitido('Jefe de Bodega')
def crear_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_autores')
    else:
        form = AutorForm()
    return render(request, 'inventario/autores/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def editar_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        form = AutorForm(request.POST, instance=autor)
        if form.is_valid():
            form.save()
            return redirect('listado_autores')
    else:
        form = AutorForm(instance=autor)
    return render(request, 'inventario/autores/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def eliminar_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        try:
            autor.delete()
        except ValidationError as e:
            print(f"Error al eliminar autor: {e}")
        except Exception as e:
            print(f"Error inesperado al eliminar autor: {e}")
    return redirect('listado_autores')

@login_required
def listado_autores(request):
    autores = Autor.objects.annotate(
        num_productos=Count('producto')
    ).order_by('apellido', 'nombre')
    return render(request, 'inventario/autores/listado.html', {
        'autores': autores
    })

@login_required
@grupo_permitido('Jefe de Bodega') 
def crear_editorial(request):
    if request.method == 'POST':
        form = EditorialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_editoriales')
    else:
        form = EditorialForm()
    return render(request, 'inventario/editoriales/formulario.html', {'form': form})

@login_required
def listado_editoriales(request):
    editoriales = Editorial.objects.annotate(
        num_productos=Count('producto') 
    ).order_by('nombre')
    return render(request, 'inventario/editoriales/listado.html', {
        'editoriales': editoriales
    })

@login_required
@grupo_permitido('Jefe de Bodega')
def editar_editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    if request.method == 'POST':
        form = EditorialForm(request.POST, instance=editorial)
        if form.is_valid():
            form.save()
            return redirect('listado_editoriales')
    else:
        form = EditorialForm(instance=editorial)
    return render(request, 'inventario/editoriales/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def eliminar_editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    if request.method == 'POST':
        try:
            editorial.delete()
        except Exception as e:
            print(f"Error al eliminar editorial: {e}")
    return redirect('listado_editoriales')

@login_required
@grupo_permitido('Jefe de Bodega')
def crear_bodega(request):
    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_bodegas')
    else:
        form = BodegaForm()
    return render(request, 'inventario/bodegas/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def editar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        form = BodegaForm(request.POST, instance=bodega)
        if form.is_valid():
            form.save()
            return redirect('listado_bodegas')
    else:
        form = BodegaForm(instance=bodega)
    return render(request, 'inventario/bodegas/formulario.html', {'form': form})

@login_required
@grupo_permitido('Jefe de Bodega')
def eliminar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        try:
            bodega.delete()
        except ValidationError as e:
            print(f"Error al eliminar bodega: {e}")
        except Exception as e:
            print(f"Error inesperado al eliminar bodega: {e}")
    return redirect('listado_bodegas')

@login_required
def listado_bodegas(request):
    bodegas = Bodega.objects.annotate(
        total_productos=Sum('stocks__cantidad')
    ).order_by('nombre')
    return render(request, 'inventario/bodegas/listado.html', {
        'bodegas': bodegas
    })

class DetalleMovimientoView( DetailView):
    model = Movimiento
    template_name = 'inventario/movimientos/detalle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] = self.object.detalles.select_related('producto')
        return context

@login_required
@grupo_permitido('Bodeguero')
def crear_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST, user=request.user)
        
        # Pre-procesamos la bodega de origen para pasarla al formset de detalles
        bodega_origen_instance = None
        if 'bodega_origen' in request.POST and request.POST['bodega_origen']:
            try:
                bodega_origen_id = int(request.POST['bodega_origen'])
                bodega_origen_instance = Bodega.objects.get(pk=bodega_origen_id)
            except (ValueError, Bodega.DoesNotExist):
                # Esto será manejado por la validación del formulario principal
                pass

        # Inicializamos el formset con los datos POST y los form_kwargs (si tenemos bodega_origen_instance)
        formset = MovimientoDetalleFormSet(
            request.POST, 
            prefix='detalles',
            form_kwargs={'bodega_origen_instance': bodega_origen_instance} if bodega_origen_instance else {}
        )
        
        # Validamos ambos formularios juntos
        if form.is_valid() and formset.is_valid():
            with transaction.atomic(): # Inicia la transacción atómica
                movimiento = form.save(commit=False) # Crea el objeto en memoria
                movimiento.usuario = request.user
                movimiento.save() # Guarda el movimiento en la DB y obtiene su PK
                
                # Ahora que 'movimiento' tiene un PK, vinculamos explícitamente el formset a esta instancia.
                formset.instance = movimiento
                formset.save() # Guarda los detalles del movimiento (ahora vinculados correctamente)
                
                # Actualiza los stocks en las bodegas
                for detalle in movimiento.detalles.all():
                    Stock.actualizar_stock(
                        bodega=movimiento.bodega_origen,
                        producto=detalle.producto,
                        cantidad=-detalle.cantidad 
                    )
                    Stock.actualizar_stock(
                        bodega=movimiento.bodega_destino,
                        producto=detalle.producto,
                        cantidad=detalle.cantidad 
                    )
                
                return redirect('detalle_movimiento', pk=movimiento.pk)
        else:
            # Si alguno de los formularios no es válido (principal o formset)
            # simplemente re-renderizamos el formulario con los errores.
            return render(request, 'inventario/movimientos/formulario.html', {
                'form': form,
                'formset': formset
            })
    else: # GET request (cuando se carga el formulario por primera vez)
        form = MovimientoForm(user=request.user)
        # Para el GET, el formset inicialmente no tiene una instancia de movimiento vinculada.
        # El queryset de productos en los detalles será vacío hasta que HTMX lo actualice.
        formset = MovimientoDetalleFormSet(prefix='detalles')
    
    return render(request, 'inventario/movimientos/formulario.html', {
        'form': form,
        'formset': formset
    })

@login_required
def listado_movimientos(request):
    movimientos = Movimiento.objects.select_related('bodega_origen', 'bodega_destino', 'usuario').order_by('-fecha')
    return render(request, 'inventario/movimientos/listado.html', {'movimientos': movimientos})

@login_required
@grupo_permitido('Bodeguero')
def generar_pdf_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(inch, A4[1] - inch, f"MOVIMIENTO DE INVENTARIO #{movimiento.id}")
    p.setFont("Helvetica", 12)
    y_offset = A4[1] - 1.8 * inch
    p.drawString(inch, y_offset, f"Fecha: {movimiento.fecha.strftime('%d/%m/%Y %H:%M:%S')}")
    y_offset -= 0.25 * inch
    p.drawString(inch, y_offset, f"Usuario: {movimiento.usuario.username}")
    y_offset -= 0.25 * inch
    p.drawString(inch, y_offset, f"Bodega Origen: {movimiento.bodega_origen.nombre}")
    y_offset -= 0.25 * inch
    p.drawString(inch, y_offset, f"Bodega Destino: {movimiento.bodega_destino.nombre}")
    y_offset -= 0.5 * inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(inch, y_offset, "Productos Movidos:")
    y_offset -= 0.3 * inch

    p.setFont("Helvetica", 12)
    p.drawString(1.2 * inch, y_offset, "Producto")
    p.drawString(5 * inch, y_offset, "Cantidad")
    y_offset -= 0.2 * inch
    p.line(1 * inch, y_offset, 7 * inch, y_offset)
    y_offset -= 0.2 * inch

    for detalle in movimiento.detalles.all():
        p.drawString(1.2 * inch, y_offset, f"{detalle.producto.titulo}")
        p.drawString(5 * inch, y_offset, f"{detalle.cantidad}")
        y_offset -= 0.2 * inch
        
    p.showPage()
    p.save() 
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="movimiento_{movimiento.id}.pdf"'
    return response

@login_required
@grupo_permitido('Jefe de Bodega')
def informe_stock(request):
    form = InformeStockForm(request.GET or None)
    stocks = Stock.objects.select_related('bodega', 'producto')
    
    if form.is_valid():
        if form.cleaned_data['bodega']:
            stocks = stocks.filter(bodega=form.cleaned_data['bodega'])
        if form.cleaned_data['editorial']:
            stocks = stocks.filter(producto__editorial=form.cleaned_data['editorial'])
    
    # La ruta de la plantilla para informe_stock ya es 'inventario/stock/listado.html'
    return render(request, 'inventario/stock/listado.html', {
        'stocks': stocks,
        'form': form
    })

@login_required
@grupo_permitido('Jefe de Bodega')
def informe_movimientos(request):
    movimientos = Movimiento.objects.select_related('bodega_origen', 'bodega_destino', 'usuario').order_by('-fecha')
    # CORRECCIÓN DE LA RUTA DE PLANTILLA PARA INFORME DE MOVIMIENTOS
    # Cambiado a 'inventario/movimientos/formulario.html'
    return render(request, 'inventario/movimientos/formulario.html', { 
        'movimientos': movimientos # Asegúrate de que esta plantilla pueda manejar la variable 'movimientos'
    })

@login_required
@grupo_permitido('Jefe de Bodega')
def exportar_informe(request):
    return HttpResponse("Funcionalidad de exportación aún no implementada.")

@login_required
def listado_stock(request):
    stocks = Stock.objects.select_related('bodega', 'producto').order_by('bodega__nombre', 'producto__titulo')
    
    form = StockForm() # Initialize form for GET request

    if request.method == 'POST':
        form = StockForm(request.POST)
        
        # Print debug information before is_valid()
        print(f"\n--- DEBUG: POST Request to listado_stock ---")
        print(f"DEBUG: StockForm initialized (POST). Is valid? {form.is_valid()}") 
        if not form.is_valid():
            print(f"DEBUG: StockForm errors: {form.errors.as_data()}") # Print errors for debugging
            # If not valid, re-render with errors
            return render(request, 'inventario/stock/listado.html', {
                'stocks': stocks,
                'form': form 
            })

        # If the form is valid, proceed with saving
        bodega = form.cleaned_data['bodega']
        producto = form.cleaned_data['producto']
        cantidad_a_sumar = form.cleaned_data['cantidad'] # This is the amount to ADD

        print(f"DEBUG: Bodega: {bodega.nombre}, Producto: {producto.titulo}, Cantidad a sumar: {cantidad_a_sumar}") 

        try:
            with transaction.atomic(): # Ensure atomic update of stock
                # Use actualizar_stock directly, as it handles get_or_create and summing
                Stock.actualizar_stock(bodega, producto, cantidad_a_sumar)

            print("DEBUG: Stock actualizado exitosamente (sumando).") 
            # messages.success(request, f"Stock de {producto.titulo} en {bodega.nombre} ajustado por {cantidad_id_sumar}.")
            return redirect('listado_stock')
        except ValidationError as e:
            print(f"DEBUG: ValidationError en Stock.actualizar_stock(): {e.message}") 
            form.add_error(None, e.message)
        except Exception as e:
            print(f"DEBUG: Error inesperado al actualizar stock: {e}")
            form.add_error(None, f"Error inesperado al actualizar stock: {e}")
    
    # Render the template for GET requests or if POST failed validation and re-rendered
    return render(request, 'inventario/stock/listado.html', {
        'stocks': stocks,
        'form': form 
    })

@login_required 
def get_productos_bodega_htmx(request):
    bodega_id = request.GET.get('bodega_id')
    productos = Producto.objects.none()
    if bodega_id:
        productos = Producto.objects.filter(stocks__bodega_id=bodega_id, stocks__cantidad__gt=0).distinct().order_by('titulo')
    
    return render(request, 'inventario/movimientos/productos_options.html', {'productos': productos, 'bodega_id': bodega_id})
