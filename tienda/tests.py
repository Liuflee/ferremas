import os
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Producto, Oferta, PrecioHistorico, Pedido, ItemPedido, DatosCompra
from .forms import ProductoForm, DatosCompraForm, RegistroForm


class LoginTest(TestCase):
    """Pruebas de inicio de sesión"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_exitoso(self):
        """Verificar que un usuario con credenciales válidas pueda ingresar"""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_fallido_password_incorrecta(self):
        """Validar que el sistema rechace credenciales incorrectas"""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)
        # Verificar que no está autenticado
        self.client.get(reverse('home'))
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)
    
    def test_login_fallido_usuario_inexistente(self):
        """Validar rechazo de usuario que no existe"""
        response = self.client.post(reverse('login'), {
            'username': 'noexiste@example.com',
            'password': 'anypass'
        })
        self.assertEqual(response.status_code, 302)


class ProductoCRUDTest(TestCase):
    """Pruebas de operaciones CRUD de productos"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        # Imagen de prueba
        self.imagen = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
    
    def test_agregar_producto_nuevo(self):
        """Comprobar que un administrador puede crear un nuevo producto"""
        data = {
            'nombre': 'Taladro Eléctrico',
            'descripcion': 'Taladro de alta potencia',
            'categoria': 'herramientas_electricas',
            'stock': 15,
            'precio': 45000,
        }
        
        with open(os.path.join(os.path.dirname(__file__), 'test', 'ssl.png'), 'rb') as img:
            response = self.client.post(
                reverse('producto_crear'),
                data={'imagen': img, **data}
            )
        
        # Verificar que se creó el producto
        self.assertEqual(Producto.objects.filter(nombre='Taladro Eléctrico').count(), 1)
        producto = Producto.objects.get(nombre='Taladro Eléctrico')
        self.assertEqual(producto.stock, 15)
        self.assertEqual(producto.categoria, 'herramientas_electricas')
        
        # Verificar que se creó el precio histórico
        self.assertTrue(PrecioHistorico.objects.filter(producto=producto).exists())
    
    def test_modificar_producto_existente(self):
        """Validar que los cambios a un producto se actualicen correctamente"""
        producto = Producto.objects.create(
            nombre='Martillo',
            descripcion='Martillo básico',
            categoria='herramientas',
            stock=10,
            activo=True,
            imagen='productos/martillo.jpg'
        )
        PrecioHistorico.objects.create(
            producto=producto,
            fecha=timezone.now(),
            valor=5000
        )
        
        # Modificar el producto
        data = {
            'nombre': 'Martillo Profesional',
            'descripcion': 'Martillo de acero reforzado',
            'categoria': 'herramientas',
            'stock': 20,
            'precio': 8000,
        }
        
        response = self.client.post(
            reverse('producto_editar', kwargs={'pk': producto.pk}),
            data=data
        )
        
        # Verificar cambios
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, 'Martillo Profesional')
        self.assertEqual(producto.stock, 20)
        self.assertEqual(producto.descripcion, 'Martillo de acero reforzado')
        
        # Verificar que se actualizó el precio
        self.assertEqual(producto.precio_actual, 8000)
    
    def test_eliminar_producto(self):
        """Verificar que un producto pueda ser eliminado (marcado como inactivo)"""
        producto = Producto.objects.create(
            nombre='Destornillador',
            descripcion='Destornillador plano',
            categoria='herramientas',
            stock=5,
            activo=True,
            imagen='productos/destornillador.jpg'
        )
        
        response = self.client.post(
            reverse('producto_eliminar', kwargs={'pk': producto.pk})
        )
        
        # Verificar que el producto fue marcado como inactivo
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        
        # Verificar que no aparece en el catálogo
        response = self.client.get(reverse('catalogo'))
        self.assertNotContains(response, 'Destornillador')


class BusquedaProductoTest(TestCase):
    """Pruebas de búsqueda y filtrado de productos"""
    
    def setUp(self):
        self.client = Client()
        
        # Crear productos de prueba
        self.producto1 = Producto.objects.create(
            nombre='Taladro Inalámbrico',
            descripcion='Taladro de batería recargable',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
        
        self.producto2 = Producto.objects.create(
            nombre='Martillo de Acero',
            descripcion='Martillo resistente para construcción',
            categoria='herramientas',
            stock=15,
            activo=True,
            imagen='productos/martillo.jpg'
        )
        
        self.producto3 = Producto.objects.create(
            nombre='Taladro de Columna',
            descripcion='Taladro estacionario de alta precisión',
            categoria='herramientas_electricas',
            stock=5,
            activo=True,
            imagen='productos/taladro_columna.jpg'
        )
    
    def test_buscar_producto_por_nombre(self):
        """Validar búsqueda por nombre"""
        response = self.client.get(reverse('catalogo'), {'search': 'Taladro'})
        
        self.assertContains(response, 'Taladro Inalámbrico')
        self.assertContains(response, 'Taladro de Columna')
        self.assertNotContains(response, 'Martillo de Acero')
    
    def test_buscar_producto_por_categoria(self):
        """Validar filtrado por categoría"""
        response = self.client.get(
            reverse('catalogo'),
            {'categoria': ['herramientas_electricas']}
        )
        
        self.assertContains(response, 'Taladro Inalámbrico')
        self.assertContains(response, 'Taladro de Columna')
        self.assertNotContains(response, 'Martillo de Acero')
    
    def test_buscar_sin_resultados(self):
        """Validar búsqueda sin resultados"""
        response = self.client.get(reverse('catalogo'), {'search': 'Excavadora'})
        
        self.assertNotContains(response, 'Taladro')
        self.assertNotContains(response, 'Martillo')


class CarritoCompraTest(TestCase):
    """Pruebas del carrito de compras"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='comprador',
            email='comprador@example.com',
            password='comprador123'
        )
        self.client.login(username='comprador', password='comprador123')
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre='Sierra Circular',
            descripcion='Sierra eléctrica de alta potencia',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/sierra.jpg'
        )
        PrecioHistorico.objects.create(
            producto=self.producto1,
            fecha=timezone.now(),
            valor=35000
        )
        
        self.producto2 = Producto.objects.create(
            nombre='Nivel Láser',
            descripcion='Nivel láser de precisión',
            categoria='medicion',
            stock=8,
            activo=True,
            imagen='productos/nivel.jpg'
        )
        PrecioHistorico.objects.create(
            producto=self.producto2,
            fecha=timezone.now(),
            valor=25000
        )
    
    def test_agregar_productos_al_carrito(self):
        """Comprobar que se pueden agregar múltiples productos al carrito"""
        # Agregar primer producto
        response = self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto1.pk}),
            {'cantidad': 2}
        )
        
        # Agregar segundo producto
        response = self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto2.pk}),
            {'cantidad': 1}
        )
        
        # Verificar carrito
        session = self.client.session
        carrito = session.get('carrito', {})
        
        self.assertEqual(carrito[str(self.producto1.pk)], 2)
        self.assertEqual(carrito[str(self.producto2.pk)], 1)
    
    def test_eliminar_producto_del_carrito(self):
        """Verificar que se puede eliminar un producto del carrito"""
        # Agregar producto
        self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto1.pk}),
            {'cantidad': 1}
        )
        
        # Eliminar producto
        response = self.client.get(
            reverse('eliminar_del_carrito', kwargs={'producto_id': self.producto1.pk})
        )
        
        # Verificar que se eliminó
        session = self.client.session
        carrito = session.get('carrito', {})
        self.assertNotIn(str(self.producto1.pk), carrito)
    
    def test_limpiar_carrito(self):
        """Verificar que se puede limpiar todo el carrito"""
        # Agregar productos
        self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto1.pk}),
            {'cantidad': 1}
        )
        self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto2.pk}),
            {'cantidad': 1}
        )
        
        # Limpiar carrito
        response = self.client.get(reverse('limpiar_carrito'))
        
        # Verificar que está vacío
        session = self.client.session
        self.assertNotIn('carrito', session)


class ProcesoCompraTest(TestCase):
    """Pruebas del proceso completo de compra"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='cliente123'
        )
        self.client.login(username='cliente', password='cliente123')
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre='Lijadora Orbital',
            descripcion='Lijadora eléctrica profesional',
            categoria='herramientas_electricas',
            stock=20,
            activo=True,
            imagen='productos/lijadora.jpg'
        )
        PrecioHistorico.objects.create(
            producto=self.producto,
            fecha=timezone.now(),
            valor=28000
        )
        
        # Agregar al carrito
        self.client.post(
            reverse('agregar_al_carrito', kwargs={'producto_id': self.producto.pk}),
            {'cantidad': 2}
        )
    
    def test_proceso_compra_completo(self):
        """Simular el proceso completo de compra"""
        # Datos de compra válidos
        datos_compra = {
            'nombre': 'Juan Pérez',
            'rut': '20246694k',
            'direccion': 'Avenida Principal 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        }
        
        # Intentar procesar la compra (hasta antes del pago)
        response = self.client.post(
            reverse('iniciar_pago'),
            data=datos_compra
        )
        
        # Verificar que se guardaron los datos de compra
        self.assertTrue(DatosCompra.objects.filter(rut='20246694K').exists())
        datos = DatosCompra.objects.get(rut='20246694K')
        self.assertEqual(datos.nombre, 'Juan Pérez')
        self.assertEqual(datos.telefono, '+56912345678')


class HistorialComprasTest(TestCase):
    """Pruebas de visualización de historial de compras"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='usuario_historial',
            email='historial@example.com',
            password='historial123'
        )
        self.client.login(username='usuario_historial', password='historial123')
        
        # Crear productos y pedidos
        self.producto = Producto.objects.create(
            nombre='Cinta Métrica',
            descripcion='Cinta métrica de 5 metros',
            categoria='medicion',
            stock=50,
            activo=True,
            imagen='productos/cinta.jpg'
        )
        PrecioHistorico.objects.create(
            producto=self.producto,
            fecha=timezone.now(),
            valor=3500
        )
        
        # Crear datos de compra
        self.datos_compra = DatosCompra.objects.create(
            usuario=self.user,
            nombre='María González',
            rut='12345678K',
            direccion='Calle 123',
            telefono='+56987654321',
            codigo_postal='7654321',
            envio=True
        )
        
        # Crear pedido
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            estado='aprobado',
            datos_compra=self.datos_compra
        )
        
        ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2,
            precio_unitario=3500
        )
    
    def test_visualizar_historial_compras(self):
        """Verificar que el usuario puede ver sus compras"""
        response = self.client.get(reverse('estado_pedidos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pedido')
        self.assertContains(response, self.pedido.id)
    
    def test_ver_detalle_pedido(self):
        """Verificar que se pueden ver los detalles de un pedido"""
        response = self.client.get(
            reverse('detalle_pedido', kwargs={'pedido_id': self.pedido.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cinta Métrica')
        self.assertContains(response, '3500')
        self.assertContains(response, 'María González')


class ValidacionCamposTest(TestCase):
    """Pruebas de validación de campos obligatorios"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
    
    def test_validacion_campos_producto(self):
        """Asegurar validación en formulario de producto"""
        form = ProductoForm(data={
            'nombre': '',  # Campo obligatorio vacío
            'descripcion': 'Descripción válida',
            'categoria': 'herramientas',
            'stock': 10,
            'precio': 5000,
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    
    def test_validacion_precio_negativo(self):
        """Validar que el precio no puede ser negativo"""
        form = ProductoForm(data={
            'nombre': 'Producto Test',
            'descripcion': 'Descripción',
            'categoria': 'herramientas',
            'stock': 10,
            'precio': -100,  # Precio inválido
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
    
    def test_validacion_datos_compra_campos_obligatorios(self):
        """Validar campos obligatorios en datos de compra"""
        form = DatosCompraForm(data={
            'nombre': '',  # Vacío
            'rut': '12345678K',
            'direccion': 'Calle 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    
    def test_validacion_rut_invalido(self):
        """Validar formato de RUT"""
        form = DatosCompraForm(data={
            'nombre': 'Pedro López',
            'rut': '123',  # RUT inválido
            'direccion': 'Calle 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)
    
    def test_validacion_registro_usuario(self):
        """Validar campos en registro de usuario"""
        form = RegistroForm(data={
            'username': 'nuevouser',
            'first_name': '',  # Campo vacío
            'last_name': 'Apellido',
            'email': 'usuario@example.com',
            'password1': 'password123',
            'password2': 'password123',
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
    
    def test_validacion_passwords_no_coinciden(self):
        """Validar que las contraseñas coincidan"""
        form = RegistroForm(data={
            'username': 'nuevouser',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'usuario@example.com',
            'password1': 'password123',
            'password2': 'diferente123',  # No coincide
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class OfertasTest(TestCase):
    """Pruebas adicionales para ofertas"""
    
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Taladro Test',
            descripcion='Taladro para pruebas',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
        PrecioHistorico.objects.create(
            producto=self.producto,
            fecha=timezone.now(),
            valor=50000
        )
    
    def test_producto_con_oferta_vigente(self):
        """Verificar que se aplica correctamente una oferta vigente"""
        ahora = timezone.now()
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=35000,
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=5)
        )
        
        # El precio actual debe ser el de la oferta
        self.assertEqual(self.producto.precio_actual, 35000)
        self.assertEqual(self.producto.precio_original, 50000)
        self.assertEqual(self.producto.porcentaje_descuento, 30)
    
    def test_producto_sin_oferta(self):
        """Verificar precio cuando no hay oferta"""
        self.assertEqual(self.producto.precio_actual, 50000)
        self.assertEqual(self.producto.porcentaje_descuento, 0)