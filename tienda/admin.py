from django.contrib import admin
from .models import *

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_actual', 'stock')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)
    ordering = ('nombre',)  # No se puede ordenar por precio directamente porque no es campo de Producto

    def precio_actual(self, obj):
        # Obtiene el último precio histórico según el ordering de PrecioHistorico (fecha descendente)
        ultimo_precio = obj.precios.first()
        return ultimo_precio.valor if ultimo_precio else '-'
    precio_actual.short_description = 'Precio'

@admin.register(PrecioHistorico)
class PrecioHistoricoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'valor', 'fecha')
    list_filter = ('producto',)
    ordering = ('-fecha',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('usuario__username',)

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('producto__nombre',)
    list_filter = ('pedido',)


@admin.register(DatosCompra)
class DatosCompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'rut', 'direccion', 'telefono', 'codigo_postal', 'envio', 'fecha')
    search_fields = ('usuario__username', 'nombre', 'rut')
    list_filter = ('envio', 'fecha')

admin.site.register(Oferta)

admin.site.register(OrdenDespacho)