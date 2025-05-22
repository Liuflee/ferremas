from django.urls import path
from . import views

urlpatterns = [
    path('bodega/', views.productos_bodega, name='productos_bodega'),
    path('pedidos/', views.pedidos_por_aprobar, name='pedidos_por_aprobar'),
    path('pedidos/aprobar/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),
    path('pedidos/rechazar/<int:pedido_id>/', views.rechazar_pedido, name='rechazar_pedido'),
    path('despacho/', views.pedidos_para_despacho, name='despacho'),
    path('orden_despacho/generar/<int:pedido_id>/', views.generar_orden_despacho, name='generar_orden_despacho'),
]