from .models import Producto

def carrito_context(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(pk=producto_id)
            subtotal = producto.precio * cantidad
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
        except Producto.DoesNotExist:
            continue

    return {
        'carrito_items': items,
        'carrito_total': total
    }
