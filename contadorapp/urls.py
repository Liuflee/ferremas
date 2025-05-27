from django.urls import path
from . import views

urlpatterns = [
    path('contabilidad/', views.vista_contador, name='vista_contador'),
    path('ordenes_enviadas/', views.ordenes_enviadas, name='ordenes_enviadas'),
    path('ordenes_enviadas/<int:orden_id>/entregado/', views.marcar_entregado, name='marcar_entregado'),
]