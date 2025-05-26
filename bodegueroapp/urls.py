from django.urls import path
from . import views

urlpatterns = [
    # Bodega URLs
    path('pedidos_despacho/', views.pedidos_para_despacho, name='pedidos_para_despacho'),
    path('pedidos_despacho/<int:pedido_id>/', views.generar_orden_despacho, name='generar_orden_despacho'),
    path('preparar_pedido/<int:pedido_id>/', views.preparar_pedido, name='preparar_pedido'),
    path('verificar_stock/<int:pedido_id>/', views.verificar_stock, name='verificar_stock'),


]