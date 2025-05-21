from .models import Producto

def carrito_context(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(pk=producto_id)
            precio_actual = producto.precios.first()  # precio más reciente

            if not precio_actual:
                # Si no hay precio histórico, ignoramos el producto
                continue

            subtotal = precio_actual.valor * cantidad
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'precio_actual': precio_actual.valor,  # útil para mostrar el precio por unidad
            })
            total += subtotal
        except Producto.DoesNotExist:
            # En caso de que el producto ya no exista, lo ignoramos
            continue

    return {
        'carrito_items': items,
        'carrito_total': total
    }
