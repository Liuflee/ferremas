from django.urls import path
from . import views
from bodegueroapp.views import ordenes_despacho

urlpatterns = [
    path('ordenes/', ordenes_despacho, name='ordenes_despacho'),   
]