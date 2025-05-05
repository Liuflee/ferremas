from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Producto
from .forms import ProductoForm, RegistroForm  # Ensure RegistroForm is defined in your forms.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm  # Ensure this is the correct path to your form

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
                  
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'tienda/producto_detalle.html', {'producto': producto})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm(initial={'first_name': '', 'last_name': '', 'email': '', 'username': ''})  # Valores iniciales vacíos para evitar 'None'

    return render(request, 'tienda/registro.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'tienda/login.html'
    authentication_form = CustomAuthenticationForm

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas. Inténtelo de nuevo.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('home')  
    
def logout_view(request):
    logout(request)
    return redirect('home')