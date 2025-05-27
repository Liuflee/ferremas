from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import *
from .forms import DatosCompraForm, OfertaForm, ProductoForm, RegistroForm  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm 
import uuid
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

def redirect_back_or_home(request):
    next_url = request.META.get('HTTP_REFERER', 'home')
    if not next_url or 'carrito' in next_url:
        return redirect('home')
    return redirect(next_url)



def obtener_precio_actual(producto):
    ultimo_precio = producto.precio_actual 
    return ultimo_precio if ultimo_precio else 0

def home(request):
    productos = Producto.objects.filter(activo=True)[:6]

    ahora = timezone.now()
    productos_en_oferta = Producto.objects.filter(
        activo=True,
        ofertas__fecha_inicio__lte=ahora,
        ofertas__fecha_fin__gte=ahora
    ).distinct()[:6]

    context = {
        'productos': productos,
        'productos_en_oferta': productos_en_oferta,
    }
    return render(request, 'tienda/home.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_crear(request):
    next_url = request.GET.get('next', 'home')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        next_url = request.POST.get('next', 'home')
        if form.is_valid():
            producto = form.save()
            precio_valor = form.cleaned_data['precio']
            PrecioHistorico.objects.create(
                producto=producto,
                fecha=timezone.now(),
                valor=precio_valor
            )
            return redirect(next_url)
    else:
        form = ProductoForm()

    return render(request, 'tienda/producto_form.html', {'form': form, 'next': next_url})


@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    next_url = request.GET.get('next', 'home')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        next_url = request.POST.get('next', 'home')
        if form.is_valid():
            producto = form.save() 
            precio_valor = form.cleaned_data['precio']
            ultimo_precio = producto.precios.first()  

            if not ultimo_precio or ultimo_precio.valor != precio_valor:
                PrecioHistorico.objects.create(
                    producto=producto,
                    fecha=timezone.now(),
                    valor=precio_valor
                )

            return redirect(next_url)
    else:

        ultimo_precio = producto.precios.first()
        initial_data = {}
        if ultimo_precio:
            initial_data['precio'] = ultimo_precio.valor
        form = ProductoForm(instance=producto, initial=initial_data)

    return render(request, 'tienda/producto_form.html', {'form': form, 'next': next_url})


@login_required
@user_passes_test(lambda u: u.is_staff)
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    next_url = request.GET.get('next', 'home') 

    if request.method == 'POST':
        producto.activo = False
        producto.save()
        return redirect(next_url) 

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
        form = RegistroForm(initial={'first_name': '', 'last_name': '', 'email': '', 'username': ''}) 

    return render(request, 'tienda/registro.html', {'form': form})



class CustomLoginView(LoginView):
    template_name = 'tienda/login.html'
    authentication_form = CustomAuthenticationForm

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas. Inténtelo de nuevo.')
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return reverse('panel_productos')  # Redirige a la vista del administrador
        elif user.groups.filter(name='Vendedor').exists():
            return reverse('productos_bodega')  # Vista principal del vendedor
        elif user.groups.filter(name='Bodeguero').exists():
            return reverse('pedidos_para_despacho')  # Vista del bodeguero
        elif user.groups.filter(name='Contador').exists():
            return reverse('vista_contador')  # Vista del contador
        else:
            return reverse('home')  # Usuario normal
    
def logout_view(request):
    logout(request)
    return redirect('home')

def catalogo(request):
    productos = Producto.objects.filter(activo=True)

    categoria_filter = request.GET.getlist('categoria')
    if categoria_filter:
        productos = productos.filter(categoria__in=categoria_filter)

    # Filtro por productos con oferta activa
    oferta_activa = request.GET.get('oferta_activa')
    if oferta_activa == 'true':
        ahora = timezone.now()
        productos = productos.filter(
            ofertas__fecha_inicio__lte=ahora,
            ofertas__fecha_fin__gte=ahora
        ).distinct()


    search_query = request.GET.get('search')
    if search_query:
        productos = productos.filter(nombre__icontains=search_query) | productos.filter(descripcion__icontains=search_query)

    order_by = request.GET.get('order_by', 'nombre') 

    if order_by in ['precio_actual', '-precio_actual']:
        productos = list(productos)  # convertir a lista para ordenar en Python
        productos.sort(key=lambda p: p.precio_actual or 0, reverse=order_by.startswith('-'))
    else:
        productos = productos.order_by(order_by)

    categorias = Producto.CATEGORIAS

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_filter': categoria_filter,
        'order_by': order_by,
    })


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    
    cantidad = int(request.POST.get('cantidad', 1))
    if cantidad < 1:
        cantidad = 1

    carrito[str(producto_id)] = carrito.get(str(producto_id), 0) + cantidad
    request.session['carrito'] = carrito
    return redirect_back_or_home(request)

def limpiar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect_back_or_home(request)

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)

    if producto_id in carrito:
        del carrito[producto_id]
        request.session['carrito'] = carrito

    return redirect('carrito')

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
        precio_actual = obtener_precio_actual(producto)
        subtotal = precio_actual * cantidad
        carrito_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
            'precio_actual': precio_actual, 
        })
        carrito_total += subtotal

    datos_compra = None
    if 'datos_compra_id' in request.session:
        datos_compra = get_object_or_404(DatosCompra, pk=request.session['datos_compra_id'])

    carrito_total_items = sum(item['cantidad'] for item in carrito_items)

    return render(request, 'tienda/carrito.html', {
        'carrito_items': carrito_items,
        'carrito_total': carrito_total,
        'datos_compra': datos_compra,
        'form': form,
        'carrito_total_items': carrito_total_items,
    })

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

            carrito_total = 0
            for producto_id, cantidad in carrito.items():
                producto = get_object_or_404(Producto, pk=producto_id)
                precio_actual = obtener_precio_actual(producto)
                carrito_total += precio_actual * cantidad

            # crear transacción con Transbank
            buy_order = str(uuid.uuid4())[:26]  
            session_id = str(uuid.uuid4())
            amount = carrito_total
            return_url = request.build_absolute_uri(reverse('webpay_respuesta'))

            tx = Transaction(WebpayOptions(
                commerce_code='597055555532',  # código de comercio de integración
                api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',  # valor por defecto de integración 
                integration_type=IntegrationType.TEST
            ))

            response = tx.create(buy_order=buy_order, session_id=session_id, amount=amount, return_url=return_url)

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
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "No se pudo procesar el pedido: el carrito está vacío.")
            return redirect('carrito')

        datos_compra_id = request.session.get('datos_compra_id')
        datos_compra = get_object_or_404(DatosCompra, pk=datos_compra_id, usuario=request.user)

        pedido = Pedido.objects.create(
            usuario=request.user,
            estado='pendiente',
            datos_compra=datos_compra
        )


        for producto_id, cantidad in carrito.items():
            producto = get_object_or_404(Producto, pk=producto_id)
            precio_unitario = producto.precio_actual
            if precio_unitario is None:
                messages.error(request, f"El producto '{producto.nombre}' no tiene un precio válido.")
                return redirect('carrito')

            # verificar stock 
            if producto.stock < cantidad:
                messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
                return redirect('carrito')

            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
            )


            producto.save()

        messages.success(request, "¡Pago realizado y pedido registrado exitosamente!")
        return redirect('pago_exitoso')

    elif response['status'] in ['FAILED', 'REJECTED', 'ERROR', 'TIMEOUT']:
        messages.error(request, f"El pago no fue exitoso: {response['status']}")
        return redirect('pago_error')

    
def pago_exitoso(request):
    if 'webpay_order' in request.session and 'webpay_token' in request.session:
        order = request.session['webpay_order']
        token = request.session['webpay_token']


        tx = Transaction(WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
            integration_type=IntegrationType.TEST
        ))

        response = tx.commit(token) 

        datos_compra = get_object_or_404(DatosCompra, usuario=request.user, id=request.session.get('datos_compra_id'))


        context = {
            'order': order,
            'amount': response['amount'],
            'status': response['status'],
            'buy_order': response['buy_order'],
            'session_id': response['session_id'],
            'datos_compra': datos_compra,  
        }

        del request.session['webpay_order']  
        del request.session['webpay_token'] 
        del request.session['carrito']
        del request.session['datos_compra_id']

        return render(request, 'tienda/pago_exitoso.html', context)

    else:
        return redirect('carrito')


def pago_error(request):
    if 'webpay_order' in request.session and 'webpay_token' in request.session:
        order = request.session['webpay_order']
        token = request.session['webpay_token']

        tx = Transaction(WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
            integration_type=IntegrationType.TEST
        ))

        response = tx.commit(token)

        context = {
            'order': order,
            'amount': response['amount'],
            'status': response['status'],
            'buy_order': response['buy_order'],
            'session_id': response['session_id'],
        }

        del request.session['webpay_order']  
        del request.session['webpay_token']  

        return render(request, 'tienda/pago_error.html', context)
    
    else:
        return redirect('carrito')
    
def error_404(request):
    return render(request, 'tienda/error_404.html', status=404)

@login_required
def estado_pedidos_usuario(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_creacion').select_related('orden_despacho')
    return render(request, 'tienda/estado_pedidos.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.select_related('orden_despacho', 'datos_compra'), id=pedido_id, usuario=request.user)
    items = pedido.items.select_related('producto')

    for item in items:
        item.total = item.cantidad * item.precio_unitario

    return render(request, 'tienda/detalle_pedido.html', {'pedido': pedido, 'items': items})
