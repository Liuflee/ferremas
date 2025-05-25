from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from tienda.models import *
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_staff) 
def ordenes_despacho(request):
    ordenes = OrdenDespacho.objects.filter(pedido__estado='preparando').select_related('pedido')
    return render(request, 'bodegueroapp/ordenes.html', {'ordenes': ordenes})

@login_required
@user_passes_test(lambda u: u.is_staff)
def aprobar_orden(request, orden_id):
    orden = get_object_or_404(OrdenDespacho, id=orden_id)
    
    if orden.preparado:
        messages.warning(request, 'Esta orden ya fue aprobada anteriormente')
    else:
        orden.preparado = True
        orden.save()
        
        if hasattr(orden, 'pedido'):
            orden.pedido.estado = 'listo'  
            orden.pedido.save()
        
        messages.success(request, f'Orden #{orden.id} aprobada correctamente')
    
    return redirect('ordenes_despacho')