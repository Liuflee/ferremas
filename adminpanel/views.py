from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from tienda.models import Producto

def dashboard(request):
    productos = Producto.objects.all()
    return render(request, 'adminpanel/dashboard.html', {'productos': productos})