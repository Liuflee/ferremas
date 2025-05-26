from django.shortcuts import render, redirect, get_object_or_404
from tienda.models import Producto, PrecioHistorico, Oferta
from tienda.forms import ProductoForm, OfertaForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_staff)
def panel_productos(request):
    productos = Producto.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            PrecioHistorico.objects.create(
                producto=producto,
                valor=form.cleaned_data['precio'],
                fecha=timezone.now()
            )
            messages.success(request, "Producto creado exitosamente.")
            return redirect('panel_productos')
    else:
        form = ProductoForm()

    return render(request, 'adminpanel/panel_productos.html', {
        'productos': productos,
        'form': form,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save() 
            precio_valor = form.cleaned_data['precio']
            ultimo_precio = producto.precios.first()  

            if not ultimo_precio or ultimo_precio.valor != precio_valor:
                PrecioHistorico.objects.create(
                    producto=producto,
                    fecha=timezone.now(),
                    valor=precio_valor
                )

            return redirect('panel_productos')
    else:

        ultimo_precio = producto.precios.first()
        initial_data = {}
        if ultimo_precio:
            initial_data['precio'] = ultimo_precio.valor
        form = ProductoForm(instance=producto, initial=initial_data)

    return render(request, 'adminpanel/editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('panel_productos')

@login_required
@user_passes_test(lambda u: u.is_staff)
def panel_ofertas(request):
    ofertas = Oferta.objects.all().order_by('-fecha_inicio')

    if request.method == 'POST':
        form = OfertaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Oferta creada correctamente.")
            return redirect('panel_ofertas')
    else:
        form = OfertaForm()

    return render(request, 'adminpanel/panel_ofertas.html', {
        'ofertas': ofertas,
        'form': form
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_oferta(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    if request.method == 'POST':
        form = OfertaForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, "Oferta editada correctamente.")
            return redirect('panel_ofertas')
    else:
        form = OfertaForm(instance=oferta)

    return render(request, 'adminpanel/editar_oferta.html', {'form': form, 'oferta': oferta})

@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_oferta(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    oferta.delete()
    messages.success(request, "Oferta eliminada correctamente.")
    return redirect('panel_ofertas')
