
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from tienda.models import Pedido, TransferenciaPago
from tienda.decorators import es_contador


@login_required
@user_passes_test(es_contador)
def vista_contador(request):
    pedidos_finalizados = Pedido.objects.filter(estado='finalizado')
    total_ventas = pedidos_finalizados.aggregate(total=Sum('items__precio_unitario'))['total'] or 0
    pagos_confirmados = TransferenciaPago.objects.filter(confirmado=True).count()
    
    contexto = {
        'pedidos': pedidos_finalizados,
        'total_ventas': total_ventas,
        'pagos_confirmados': pagos_confirmados,
    }
    return render(request, 'contadorapp/resumen_contador.html', contexto)
