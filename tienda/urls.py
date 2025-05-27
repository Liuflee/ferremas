from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('producto/nuevo/', views.producto_crear, name='producto_crear'),
    path('producto/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('producto/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'), 
    path('registro/', views.registro, name='registro'),  
    path('login/', views.CustomLoginView.as_view(), name='login'), 
    path('logout/', views.logout_view, name='logout'), 
    path('catalogo/', views.catalogo, name='catalogo'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('limpiar-carrito/', views.limpiar_carrito, name='limpiar_carrito'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/error/', views.pago_error, name='pago_error'),
    path('error_404/', views.error_404, name='error_404'),
    path('pagar/', views.iniciar_pago, name='iniciar_pago'),
    path('webpay/respuesta/', views.webpay_respuesta, name='webpay_respuesta'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('mis_pedidos/', views.estado_pedidos_usuario, name='estado_pedidos'),
    path('mis_pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),


]
