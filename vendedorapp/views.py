from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from tienda.models import *

# Create your views here.
@login_required
@user_passes_test(lambda u: u.is_staff)  # o un test más específico para "vendedor"
def productos_bodega(request):
    productos = Producto.objects.all()
    return render(request, 'vendedorapp/productos_bodega.html', {'productos': productos})

@login_required
@user_passes_test(lambda u: u.is_staff)
def pedidos_por_aprobar(request):
    pedidos = Pedido.objects.filter(estado='pendiente')  # O el estado que uses
    return render(request, 'vendedorapp/pedidos_por_aprobar.html', {'pedidos': pedidos})

@login_required
@user_passes_test(lambda u: u.is_staff)
def aprobar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'aprobado'
    pedido.save()
    # Aquí podrías notificar al bodeguero si usas señales o emails
    return redirect('pedidos_por_aprobar')

@login_required
@user_passes_test(lambda u: u.is_staff)
def rechazar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'rechazado'
    pedido.save()
    return redirect('pedidos_por_aprobar')

#Enviar a bodega
@login_required
@user_passes_test(lambda u: u.is_staff)
def pedidos_para_despacho(request):
    pedidos = Pedido.objects.filter(estado='aprobado')  # Listos para preparar
    return render(request, 'vendedorapp/despacho.html', {'pedidos': pedidos})

@login_required
@user_passes_test(lambda u: u.is_staff)
def generar_orden_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Solo permitir generar si el pedido está aprobado y aún no tiene orden
    if pedido.estado == 'aprobado' and not hasattr(pedido, 'orden_despacho'):
        orden = OrdenDespacho.objects.create(pedido=pedido)
        pedido.estado = 'en_preparacion'  # Nuevo estado, agrégalo a tus choices
        pedido.save()
    
    return redirect('pedidos_para_despacho')
