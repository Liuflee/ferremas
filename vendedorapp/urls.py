from django.urls import path
from . import views

urlpatterns = [
    path('bodega/', views.productos_bodega, name='productos_bodega'),
    path('pedidos/', views.pedidos_por_aprobar, name='pedidos_por_aprobar'),
    path('pedidos/aprobar/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),
    path('pedidos/rechazar/<int:pedido_id>/', views.rechazar_pedido, name='rechazar_pedido'),
    path('ordenes_despacho/', views.ordenes_de_despacho, name='ordenes_de_despacho'),
    path('despacho/', views.ordenes_de_despacho, name='despacho'),
    path('ordenes_despacho/aprobar/<int:orden_id>/', views.aprobar_orden, name='aprobar_orden'),
]