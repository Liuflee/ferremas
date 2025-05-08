from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Producto
from .forms import ProductoForm, RegistroForm  
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm 
import uuid
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions


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

def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/catalogo.html', {'productos': productos})


def agregar_al_carrito(request, producto_id):
    # lógica para agregar al carrito, simplificada
    producto = Producto.objects.get(pk=producto_id)
    carrito = request.session.get('carrito', {})
    carrito[producto_id] = carrito.get(producto_id, 0) + 1
    request.session['carrito'] = carrito
    return redirect('catalogo')

def carrito(request):
    carrito = request.session.get('carrito', {})
    carrito_items = []
    carrito_total = 0

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=producto_id)
        subtotal = producto.precio * cantidad
        carrito_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        carrito_total += subtotal

    return render(request, 'tienda/carrito.html', {
        'carrito_items': carrito_items,
        'carrito_total': carrito_total
    })

configuration = WebpayOptions(
    commerce_code='597055555532',  # código de comercio de pruebas
    api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',  # clave de API de pruebas
    integration_type=IntegrationType.TEST
)

transaction = Transaction(configuration)

def iniciar_pago(request):
    carrito = request.session.get('carrito', {})
    total = sum(get_object_or_404(Producto, pk=producto_id).precio * cantidad for producto_id, cantidad in carrito.items())
    
    # Generar un buy_order único y truncado a 26 caracteres
    buy_order = str(uuid.uuid4())[:26]
    session_id = str(request.session.session_key or 'sesion123')
    return_url = request.build_absolute_uri(reverse('respuesta_pago'))

    response = transaction.create(
        buy_order=buy_order,
        session_id=session_id,
        amount=total,
        return_url=return_url
    )

    request.session['carrito'] = {}  # Limpiar el carrito después de generar la orden
    return redirect(response['url'] + '?token_ws=' + response['token'])

def respuesta_pago(request):
    token = request.GET.get('token_ws')

    if not token:
        return render(request, 'tienda/pago_error.html', {'mensaje': 'Token no recibido.'})

    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        return render(request, 'tienda/pago_exitoso.html', {'response': response})
    else:
        return render(request, 'tienda/pago_error.html', {'mensaje': 'Transacción no autorizada'})