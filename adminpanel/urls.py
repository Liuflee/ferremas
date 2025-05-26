from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.panel_productos, name='panel_productos'),
    path('ofertas/', views.panel_ofertas, name='panel_ofertas'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('ofertas/editar/<int:oferta_id>/', views.editar_oferta, name='editar_oferta'),
    path('ofertas/eliminar/<int:oferta_id>/', views.eliminar_oferta, name='eliminar_oferta'),
]