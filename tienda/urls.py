from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página principal
    path('producto/nuevo/', views.producto_crear, name='producto_crear'),
    path('producto/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('producto/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),  # Detalle del producto
    path('registro/', views.registro, name='registro'),  # Registro de usuario
    path('login/', views.CustomLoginView.as_view(), name='login'),  # Vista de inicio de sesión personalizada
    path('logout/', views.logout_view, name='logout'),  # Vista de cierre de sesión
    path('catalogo/', views.catalogo, name='catalogo'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/respuesta/', views.respuesta_pago, name='respuesta_pago'),



]
