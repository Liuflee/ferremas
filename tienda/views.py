from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Producto
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required

def home(request):
    productos = Producto.objects.all()  # Obtiene todos los productos
    return render(request, 'tienda/home.html', {'productos': productos})

def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductoForm()
    return render(request, 'tienda/producto_form.html', {'form': form})

def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/producto_form.html', {'form': form})

def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('home')
    return render(request, 'tienda/producto_confirmar_eliminar.html', {'producto': producto})