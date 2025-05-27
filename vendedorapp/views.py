from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from tienda.decorators import es_vendedor
from tienda.models import *

# Create your views here.
@login_required
@user_passes_test(es_vendedor)  # o un test más específico para "vendedor"
def productos_bodega(request):
    # Esta vista muestra los productos disponibles en la bodega
    productos = Producto.objects.all()
    return render(request, 'vendedorapp/productos_bodega.html', {'productos': productos})

@login_required
@user_passes_test(es_vendedor)
def pedidos_por_aprobar(request):
    # Esta vista muestra los pedidos pendientes de aprobación
    pedidos = Pedido.objects.filter(estado='pendiente')  # O el estado que uses
    return render(request, 'vendedorapp/pedidos_por_aprobar.html', {'pedidos': pedidos})

@login_required
@user_passes_test(es_vendedor)
def aprobar_pedido(request, pedido_id):
    # Esta vista aprueba un pedido y lo marca como aprobado
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'aprobado'
    pedido.save()
    # Aquí podrías notificar al bodeguero si usas señales o emails
    return redirect('pedidos_por_aprobar')

@login_required
@user_passes_test(es_vendedor)
def rechazar_pedido(request, pedido_id):
    # Esta vista rechaza un pedido y lo marca como rechazado
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'rechazado'
    pedido.save()
    return redirect('pedidos_por_aprobar')


@login_required
@user_passes_test(es_vendedor)
def ordenes_de_despacho(request):
    # Esta vista muestra las órdenes de despacho generadas
    ordenes = OrdenDespacho.objects.all()
    return render(request, 'vendedorapp/despacho.html', {'ordenes': ordenes})

'''Marcar ordenes listas para despacho.'''
@login_required
@user_passes_test(es_vendedor)
def aprobar_orden(request, orden_id):
    # Esta vista marca una orden de despacho como lista para entregar
    orden = get_object_or_404(OrdenDespacho, id=orden_id)
    orden.estado = 'listo'
    orden.save()
    return redirect('ordenes_de_despacho')

@login_required
@user_passes_test(es_vendedor)
def marcar_enviado(request, orden_id):
    # Esta vista marca una orden como entregada y su pedido como finalizado
    orden = get_object_or_404(OrdenDespacho, id=orden_id)

    if orden.estado != 'listo':
        # Solo se pueden marcar como entregadas las órdenes listas
        return redirect('ordenes_de_despacho')

    orden.estado = 'enviado'
    orden.save()

    # Cambiar el estado del pedido relacionado a 'finalizado'
    pedido = orden.pedido
    pedido.estado = 'enviado'
    pedido.save()

    return redirect('ordenes_de_despacho')
