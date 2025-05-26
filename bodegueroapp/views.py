from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from tienda.models import *
from django.contrib import messages


''' Ver órdenes de pedidos asignadas

Lista de pedidos pendientes por preparar.

Detalles de cada orden (productos, cantidades, urgencia).'''

@login_required
@user_passes_test(lambda u: u.is_staff)
def pedidos_para_despacho(request):
    # Esta vista muestra los pedidos que están listos para ser preparados para despacho
    # Filtrar pedidos que están en estado 'aprobado' y 'en preparacion' y tienen datos de compra
    pedidos = Pedido.objects.filter(estado__in=['aprobado', 'en_preparacion'], datos_compra__isnull=False)
    return render(request, 'bodegueroapp/pedidos_para_despacho.html', {'pedidos': pedidos})

'''Aceptar y preparar pedidos

Confirmar que puede prepararse con el stock disponible.

Preparar físicamente el pedido.'''

def verificar_stock(pedido):
    for item in pedido.items.all():
        producto = item.producto
        if producto.stock < item.cantidad:
            return False, f'No hay suficiente stock para el producto {producto.nombre}.'
    return True, 'Stock suficiente para preparar el pedido.'

'''Preparar pedido para despacho
Esta vista prepara un pedido para despacho, cambiando su estado a "en_preparacion" si tiene stock suficiente.'''''
@login_required
@user_passes_test(lambda u: u.is_staff)
def preparar_pedido(request, pedido_id):
    #Esta vista prepara un pedido para despacho
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if pedido.estado != 'aprobado':
        messages.error(request, 'El pedido no está en estado aprobado para preparar.')
        return redirect('pedidos_para_despacho')
    # Verificar stock antes de preparar
    stock_suficiente, mensaje = verificar_stock(pedido)
    if not stock_suficiente:
        messages.error(request, mensaje)
        return redirect('pedidos_para_despacho')
    pedido.estado = 'en_preparacion' 
    pedido.save()
    
    messages.success(request, f'Pedido #{pedido.id} preparado correctamente.')
    return redirect('pedidos_para_despacho')

'''Generar orden de despacho, crea una orden de depacho para un pedido con estado "en_preparacion".
La orden de despacho se asocia al pedido y cambia su estado a "enviado".'''
@login_required
@user_passes_test(lambda u: u.is_staff)
def generar_orden_despacho(request, pedido_id):
    # Esta vista genera una orden de despacho para un pedido aprobado
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Solo permitir generar si el pedido está aprobado y aún no tiene orden
    if pedido.estado == 'en_preparacion' and not hasattr(pedido, 'orden_despacho'):
        OrdenDespacho.objects.create(pedido=pedido)
        pedido.estado = 'enviado'  # Cambiar estado del pedido a enviado
        messages.success(request, f'Orden de despacho generada para el pedido #{pedido.id}.')
        pedido.save()
    
    return redirect('pedidos_para_despacho')

