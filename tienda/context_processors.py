from .models import Producto


def carrito_context(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(pk=producto_id)
            precio_unitario = producto.precio_actual

            if precio_unitario is None:
                # Si no hay precio válido, ignoramos el producto
                continue

            subtotal = precio_unitario * cantidad
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'precio_actual': precio_unitario,  # Mostrar el precio ya con oferta si aplica
                'precio_original': producto.precio_original,  # Útil si quieres mostrar descuento
            })
            total += subtotal
        except Producto.DoesNotExist:
            continue

    return {
        'carrito_items': items,
        'carrito_total': total
    }