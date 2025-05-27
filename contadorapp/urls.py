from django.urls import path
from . import views

urlpatterns = [
    path('contabilidad/', views.vista_contador, name='vista_contador'),
]