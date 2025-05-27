from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from tienda.models import Pedido, TransferenciaPago, OrdenDespacho
from tienda.decorators import es_contador


@login_required
@user_passes_test(es_contador)
def resumen_compras(request):
    # Filtrar solo pedidos confirmados y finalizados
    pedidos = Pedido.objects.filter(estado__in=['aprobado', 'enviado', 'entregado', 'finalizado'])

    # Totales generales
    total_ingresos = pedidos.aggregate(total=Sum('items__precio_unitario'))['total']

    # Si quieres permitir filtrar por fechas
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')

    if fecha_inicio and fecha_fin:
        pedidos = pedidos.filter(fecha_creacion__range=[fecha_inicio, fecha_fin])

    context = {
        'pedidos': pedidos,
        'total_ingresos': total_ingresos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'contadorapp/resumen_compras.html', context)


@login_required
@user_passes_test(es_contador)
def vista_contador(request):
    pedidos_finalizados = Pedido.objects.filter(estado='finalizado')

    total_ventas = pedidos_finalizados.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('items__cantidad') * F('items__precio_unitario'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0

#cantidad de pedidos finalizados
    pagos_confirmados = Pedido.objects.filter(estado='finalizado').count()

    contexto = {
        'pedidos': pedidos_finalizados,
        'total_ventas': total_ventas,
        'pagos_confirmados': pagos_confirmados,
    }
    return render(request, 'contadorapp/resumen_contador.html', contexto)



@login_required
@user_passes_test(es_contador)
def ordenes_enviadas(request):
    # Mostrar solo órdenes que ya fueron enviadas
    ordenes = OrdenDespacho.objects.filter(estado='enviado')
    return render(request, 'contadorapp/ordenes_enviadas.html', {'ordenes': ordenes})


@login_required
@user_passes_test(es_contador)
def marcar_entregado(request, orden_id):
    orden = get_object_or_404(OrdenDespacho, id=orden_id, estado='enviado')
    orden.estado = 'entregado'
    orden.save()

    # También marcar el pedido como finalizado
    pedido = orden.pedido
    pedido.estado = 'finalizado'
    pedido.save()

    return redirect('ordenes_enviadas')