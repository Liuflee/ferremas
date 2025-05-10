from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import DatosCompra, Producto
from .forms import DatosCompraForm, ProductoForm, RegistroForm  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm 
import uuid
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions


def home(request):
    productos = Producto.objects.all()[:6]  # vista previa de productos
    return render(request, 'tienda/home.html', {'productos': productos})

def redirect_back_or_home(request):
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_crear(request):
    next_url = request.GET.get('next', 'home')  # Leer 'next' del GET

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        next_url = request.POST.get('next', 'home')  # Leer 'next' del POST
        if form.is_valid():
            form.save()
            return redirect(next_url)  # Redirigir a la URL que venga en 'next'
    else:
        form = ProductoForm()
    
    # Pasar 'next' al contexto para el formulario
    return render(request, 'tienda/producto_form.html', {'form': form, 'next': next_url})


@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    next_url = request.GET.get('next', 'home')  # Leer 'next' del GET

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        next_url = request.POST.get('next', 'home')  # Leer 'next' del POST
        if form.is_valid():
            form.save()
            return redirect(next_url)  # Redirigir a la URL que venga en 'next'
    else:
        form = ProductoForm(instance=producto)
    
    # Pasar 'next' al contexto para el formulario
    return render(request, 'tienda/producto_form.html', {'form': form, 'next': next_url})


@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    next_url = request.GET.get('next', 'home')  # Leer 'next' del GET

    if request.method == 'POST':
        producto.delete()
        return redirect(next_url)  # Redirigir a la URL que venga en 'next'

    # Pasar 'next' al contexto para el formulario
    return render(request, 'tienda/producto_confirmar_eliminar.html', {'producto': producto, 'next': next_url})


                  
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
    # Obtener todos los productos
    productos = Producto.objects.all()

    # Filtro por categoría
    categoria_filter = request.GET.get('categoria')
    if categoria_filter:
        productos = productos.filter(categoria=categoria_filter)

    # Filtro por búsqueda de nombre o descripción
    search_query = request.GET.get('search')
    if search_query:
        productos = productos.filter(nombre__icontains=search_query) | productos.filter(descripcion__icontains=search_query)

    # Ordenar productos
    order_by = request.GET.get('order_by', 'nombre')  # 'nombre' es el valor predeterminado
    productos = productos.order_by(order_by)

    # Obtener todas las categorías para el filtro
    categorias = Producto.CATEGORIAS

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_filter': categoria_filter,
        'order_by': order_by,
    })

def agregar_al_carrito(request, producto_id):
    # lógica para agregar al carrito, simplificada
    producto = Producto.objects.get(pk=producto_id)
    carrito = request.session.get('carrito', {})
    carrito[producto_id] = carrito.get(producto_id, 0) + 1
    request.session['carrito'] = carrito
    return redirect_back_or_home(request)

def limpiar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect_back_or_home(request)

def carrito(request):
    carrito = request.session.get('carrito', {})
    carrito_items = []
    carrito_total = 0
    form = DatosCompraForm()
    if request.method == 'POST':
        form = DatosCompraForm(request.POST)
        if form.is_valid():
            datos_compra = form.save(commit=False)
            datos_compra.usuario = request.user
            datos_compra.save()
            request.session['datos_compra_id'] = datos_compra.id
            return redirect('iniciar_pago')

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=producto_id)
        subtotal = producto.precio * cantidad
        carrito_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        carrito_total += subtotal

    datos_compra = None
    if 'datos_compra_id' in request.session:
        datos_compra = get_object_or_404(DatosCompra, pk=request.session['datos_compra_id'])

    return render(request, 'tienda/carrito.html', {
        'carrito_items': carrito_items,
        'carrito_total': carrito_total,
        'datos_compra': datos_compra,
        'form': form
    })


@login_required
def iniciar_pago(request):
    if request.method == 'POST':
        form = DatosCompraForm(request.POST)
        carrito = request.session.get('carrito', {})

        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('carrito')

        if form.is_valid():
            datos_compra = form.save(commit=False)
            datos_compra.usuario = request.user
            datos_compra.save()
            request.session['datos_compra_id'] = datos_compra.id

            # Total del carrito
            carrito_total = 0
            for producto_id, cantidad in carrito.items():
                producto = get_object_or_404(Producto, pk=producto_id)
                carrito_total += producto.precio * cantidad

            # Crear transacción con Transbank
            buy_order = str(uuid.uuid4())[:26]  # ID único, max 26 caracteres
            session_id = str(uuid.uuid4())
            amount = carrito_total
            return_url = request.build_absolute_uri(reverse('webpay_respuesta'))

            tx = Transaction(WebpayOptions(
                commerce_code='597055555532',  # código de comercio de integración
                api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',  # usa el valor por defecto de integración o el tuyo si tienes producción
                integration_type=IntegrationType.TEST
            ))

            response = tx.create(buy_order=buy_order, session_id=session_id, amount=amount, return_url=return_url)

            # Guardar la orden en sesión (podrías también hacer un modelo de Orden)
            request.session['webpay_token'] = response['token']
            request.session['webpay_order'] = buy_order

            return redirect(response['url'] + '?token_ws=' + response['token'])
        else:
            messages.error(request, "Revisa los datos ingresados.")
    return redirect('carrito')

@login_required
def webpay_respuesta(request):
    token = request.GET.get("token_ws")

    if not token:
        messages.error(request, "Transacción no válida.")
        return redirect('carrito')

    tx = Transaction(WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    ))

    response = tx.commit(token)
    
    if response['status'] == 'AUTHORIZED':
        # Puedes guardar una orden con estado pagado aquí
        messages.success(request, "¡Pago realizado con éxito!")

        # Vaciar carrito
        if 'carrito' in request.session:
            del request.session['carrito']

        return redirect('pago_exitoso')  # Redirigir a una página de éxito
    elif response['status'] == 'FAILED':
        messages.error(request, "El pago ha fallado.")
        return redirect('pago_error')
    elif response['status'] == 'REJECTED':
        messages.error(request, "El pago fue rechazado.")
        return redirect('pago_error')
    elif response['status'] == 'ERROR':
        messages.error(request, "Error en el pago.")
        return redirect('pago_error')
    elif response['status'] == 'TIMEOUT':
        messages.error(request, "El pago ha expirado.")
        return redirect('pago_error')
    else:
        messages.error(request, "El pago no fue exitoso.")
        return redirect('carrito')
    
def pago_exitoso(request):
    if 'webpay_order' in request.session and 'webpay_token' in request.session:
        order = request.session['webpay_order']
        token = request.session['webpay_token']

        # Aquí puedes obtener los detalles de la transacción
        tx = Transaction(WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
            integration_type=IntegrationType.TEST
        ))

        response = tx.commit(token)  # Obtener detalles completos de la transacción

        # Obtener los datos de compra del usuario
        datos_compra = get_object_or_404(DatosCompra, usuario=request.user, id=request.session.get('datos_compra_id'))

        # Agregar los datos de compra al contexto
        context = {
            'order': order,
            'amount': response['amount'],
            'status': response['status'],
            'buy_order': response['buy_order'],
            'session_id': response['session_id'],
            'datos_compra': datos_compra,  # Datos del comprador
        }

        del request.session['webpay_order']  # Limpiar la sesión después de usarla
        del request.session['webpay_token']  # Limpiar el token también

        return render(request, 'tienda/pago_exitoso.html', context)

    else:
        return redirect('carrito')


def pago_error(request):
    if 'webpay_order' in request.session and 'webpay_token' in request.session:
        order = request.session['webpay_order']
        token = request.session['webpay_token']

        # Aquí puedes hacer lo mismo, obtener más detalles sobre la transacción
        tx = Transaction(WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
            integration_type=IntegrationType.TEST
        ))

        response = tx.commit(token)

        # Pasar la información a la plantilla
        context = {
            'order': order,
            'amount': response['amount'],
            'status': response['status'],
            'buy_order': response['buy_order'],
            'session_id': response['session_id'],
        }

        del request.session['webpay_order']  # Limpiar la sesión después de usarla
        del request.session['webpay_token']  # Limpiar el token también

        return render(request, 'tienda/pago_error.html', context)
    
    else:
        return redirect('carrito')
    
def error_404(request):
    return render(request, 'tienda/error_404.html', status=404)

