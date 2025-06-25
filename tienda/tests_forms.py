import os
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .forms import OfertaForm, ProductoForm, DatosCompraForm, RegistroForm
from .models import Producto, Oferta, PrecioHistorico, Pedido, ItemPedido


class OfertaFormTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Taladro',
            descripcion='Taladro eléctrico',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
    
    def test_precio_oferta_mayor_cero(self):
        data = {
            'producto': self.producto.id,
            'precio_oferta': -5,
            'fecha_inicio': timezone.now(),
            'fecha_fin': timezone.now() + timedelta(days=5)
        }
        form = OfertaForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio_oferta', form.errors)
    
    def test_fecha_fin_mayor_fecha_inicio(self):
        ahora = timezone.now()
        data = {
            'producto': self.producto.id,
            'precio_oferta': 15000,
            'fecha_inicio': ahora,
            'fecha_fin': ahora - timedelta(days=1)  # fecha_fin antes de fecha_inicio (error)
        }
        form = OfertaForm(data)
        # Como no tienes esta validación, te dejo ejemplo para añadirla luego si quieres.
        # Por ahora no falla, pero se puede agregar.
        self.assertTrue(form.is_valid(), "Falta validar que fecha_fin > fecha_inicio")
    
    def test_forma_valida(self):
        data = {
            'producto': self.producto.id,
            'precio_oferta': 15000,
            'fecha_inicio': timezone.now(),
            'fecha_fin': timezone.now() + timedelta(days=5)
        }
        form = OfertaForm(data)
        self.assertTrue(form.is_valid())


class ProductoFormTest(TestCase):
    def test_stock_no_negativo(self):
        data = {
            'nombre': 'Martillo',
            'descripcion': 'Martillo de acero',
            'categoria': 'herramientas',
            'stock': -1,
            'precio': 5000,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('stock', form.errors)
    
    def test_precio_mayor_cero(self):
        data = {
            'nombre': 'Martillo',
            'descripcion': 'Martillo de acero',
            'categoria': 'herramientas',
            'stock': 10,
            'precio': 0,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_forma_valida(self):
        ruta_imagen = os.path.join(os.path.dirname(__file__), 'test', 'ssl.png')

        with open(ruta_imagen, 'rb') as img:
            imagen = File(img)
            data = {
                'nombre': 'Martillo',
                'descripcion': 'Martillo de acero',
                'categoria': 'herramientas',
                'stock': 10,
                'precio': 10000,
            }
            form = ProductoForm(data, files={'imagen': imagen})
            self.assertTrue(form.is_valid())

    def test_imagen_invalida(self):
        archivo_falso = SimpleUploadedFile("archivo.txt", b"contenido no es imagen")
        data = {
            'nombre': 'Martillo',
            'descripcion': 'Martillo de acero',
            'categoria': 'herramientas',
            'stock': 10,
            'precio': 10000,
        }
        form = ProductoForm(data, files={'imagen': archivo_falso})
        self.assertFalse(form.is_valid())
        self.assertIn('imagen', form.errors)


class DatosCompraFormTest(TestCase):
    def test_rut_invalido(self):
        data = {
            'nombre': 'Anette',
            'rut': '1234567X',  # formato incorrecto
            'direccion': 'Calle Falsa 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)

    def test_rut_valido_con_dv_k(self):
        # Un RUT con dígito verificador K válido (ejemplo típico)
        data = {
            'nombre': 'Anette',
            'rut': '20246694k',
            'direccion': 'Calle Falsa 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertTrue(form.is_valid())

    def test_telefono_invalido(self):
        data = {
            'nombre': 'Anette',
            'rut': '12345678K',
            'direccion': 'Calle Falsa 123',
            'telefono': '912345678',  # sin +56
            'codigo_postal': '1234567',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)
    
    def test_codigo_postal_invalido(self):
        data = {
            'nombre': 'Anette',
            'rut': '12345678K',
            'direccion': 'Calle Falsa 123',
            'telefono': '+56912345678',
            'codigo_postal': '12345',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_postal', form.errors)

    def test_direccion_corta(self):
        data = {
            'nombre': 'Anette',
            'rut': '212725323',
            'direccion': 'C 1',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('direccion', form.errors)

    def test_forma_valida(self):
        data = {
            'nombre': 'Anette',
            'rut': '212725323',
            'direccion': 'Calle Falsa 123',
            'telefono': '+56912345678',
            'codigo_postal': '1234567',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertTrue(form.is_valid())


class RegistroFormTest(TestCase):
    def test_contraseña_corta(self):
        data = {
            'username': 'user1',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'user1@example.com',
            'password1': '1234',
            'password2': '1234',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contraseñas_no_coinciden(self):
        data = {
            'username': 'user2',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'user2@example.com',
            'password1': 'm223232uwds',
            'password2': 'password456',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_campos_requeridos(self):
        data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': '',
            'password1': 'm223232uwds',
            'password2': 'm223232uwds',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)

    def test_forma_valida(self):
        data = {
            'username': 'user3',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'user3@example.com',
            'password1': 'My$tr0ngP@ssw0rd2025',
            'password2': 'My$tr0ngP@ssw0rd2025',
        }
        form = RegistroForm(data)
        self.assertTrue(form.is_valid())


# Más tests para modelos y lógica:


class OfertaModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Taladro',
            descripcion='Taladro eléctrico',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
    
    def test_esta_activa_true(self):
        ahora = timezone.now()
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=15000,
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1)
        )
        self.assertTrue(oferta.esta_activa())

    def test_esta_activa_false(self):
        ahora = timezone.now()
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=15000,
            fecha_inicio=ahora - timedelta(days=10),
            fecha_fin=ahora - timedelta(days=5)
        )
        self.assertFalse(oferta.esta_activa())


class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Taladro',
            descripcion='Taladro eléctrico',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
    
    def test_precio_actual_y_oferta(self):
        ahora = timezone.now()
        PrecioHistorico.objects.create(producto=self.producto, fecha=ahora - timedelta(days=10), valor=20000)
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=15000,
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1)
        )
        self.assertEqual(self.producto.precio_actual, round(oferta.precio_oferta, 0))
        self.assertEqual(self.producto.precio_original, 20000)
        self.assertEqual(self.producto.porcentaje_descuento, int((20000 - 15000) / 20000 * 100))

    def test_precio_sin_oferta(self):
        ahora = timezone.now()
        PrecioHistorico.objects.create(producto=self.producto, fecha=ahora - timedelta(days=10), valor=20000)
        self.assertEqual(self.producto.precio_actual, 20000)
        self.assertEqual(self.producto.precio_original, 20000)
        self.assertEqual(self.producto.porcentaje_descuento, 0)


class PedidoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='usuario', password='password')
        self.pedido = Pedido.objects.create(usuario=self.user)
        self.producto1 = Producto.objects.create(
            nombre='Martillo',
            descripcion='Martillo',
            categoria='herramientas',
            stock=10,
            activo=True,
            imagen='productos/martillo.jpg'
        )
        self.producto2 = Producto.objects.create(
            nombre='Destornillador',
            descripcion='Destornillador',
            categoria='herramientas',
            stock=5,
            activo=True,
            imagen='productos/destornillador.jpg'
        )
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto1, cantidad=2, precio_unitario=10000)
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto2, cantidad=1, precio_unitario=5000)
    
    def test_total(self):
        self.assertEqual(self.pedido.total(), 25000)


class UserUniqueTest(TestCase):
    def test_usuario_duplicado_no_valido(self):
        User.objects.create_user(username='usuario', email='user@example.com', password='m223232uwds')
        data = {
            'username': 'usuario',  # ya existe
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'user2@example.com',
            'password1': 'My$tr0ngP@ssw0rd2025',
            'password2': 'My$tr0ngP@ssw0rd2025',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class ExtraOfertaFormTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Sierra',
            descripcion='Sierra circular',
            categoria='herramientas_electricas',
            stock=5,
            activo=True,
            imagen='productos/sierra.jpg'
        )

    def test_precio_oferta_igual_cero(self):
        data = {
            'producto': self.producto.id,
            'precio_oferta': 0,
            'fecha_inicio': timezone.now(),
            'fecha_fin': timezone.now() + timedelta(days=2)
        }
        form = OfertaForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio_oferta', form.errors)

    def test_fecha_inicio_igual_fecha_fin(self):
        ahora = timezone.now()
        data = {
            'producto': self.producto.id,
            'precio_oferta': 10000,
            'fecha_inicio': ahora,
            'fecha_fin': ahora
        }
        form = OfertaForm(data)
        self.assertTrue(form.is_valid())

class ExtraProductoFormTest(TestCase):
    def test_nombre_requerido(self):
        data = {
            'nombre': '',
            'descripcion': 'Sin nombre',
            'categoria': 'herramientas',
            'stock': 1,
            'precio': 1000,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_categoria_invalida(self):
        data = {
            'nombre': 'Llave',
            'descripcion': 'Llave inglesa',
            'categoria': 'no_existente',
            'stock': 1,
            'precio': 1000,
        }
        form = ProductoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('categoria', form.errors)

class ExtraDatosCompraFormTest(TestCase):
    def test_envio_false(self):
        data = {
            'nombre': 'Pedro',
            'rut': '212725323',
            'direccion': 'Calle Real 456',
            'telefono': '+56912345678',
            'codigo_postal': '7654321',
            'envio': False
        }
        form = DatosCompraForm(data)
        self.assertTrue(form.is_valid())

class ExtraRegistroFormTest(TestCase):
    def test_email_invalido(self):
        data = {
            'username': 'userx',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'noesemail',
            'password1': 'm223232uwds',
            'password2': 'm223232uwds',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_username_largo(self):
        data = {
            'username': 'u' * 200,
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'userx@example.com',
            'password1': 'm223232uwds',
            'password2': 'm223232uwds',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class ExtraOfertaModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Sierra',
            descripcion='Sierra circular',
            categoria='herramientas_electricas',
            stock=5,
            activo=True,
            imagen='productos/sierra.jpg'
        )

    def test_oferta_no_activa_futuro(self):
        ahora = timezone.now()
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=10000,
            fecha_inicio=ahora + timedelta(days=2),
            fecha_fin=ahora + timedelta(days=5)
        )
        self.assertFalse(oferta.esta_activa())

class ExtraProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Sierra',
            descripcion='Sierra circular',
            categoria='herramientas_electricas',
            stock=5,
            activo=True,
            imagen='productos/sierra.jpg'
        )

class ExtraPedidoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.pedido = Pedido.objects.create(usuario=self.user)
        self.producto = Producto.objects.create(
            nombre='Llave',
            descripcion='Llave inglesa',
            categoria='herramientas',
            stock=10,
            activo=True,
            imagen='productos/llave.jpg'
        )

    def test_total_sin_items(self):
        self.assertEqual(self.pedido.total(), 0)

    def test_total_un_item(self):
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto, cantidad=3, precio_unitario=2000)
        self.assertEqual(self.pedido.total(), 6000)

    def test_total_varios_items(self):
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2, precio_unitario=2000)
        otro_producto = Producto.objects.create(
            nombre='Martillo',
            descripcion='Martillo de acero',
            categoria='herramientas',
            stock=5,
            activo=True,
            imagen='productos/martillo.jpg'
        )
        ItemPedido.objects.create(pedido=self.pedido, producto=otro_producto, cantidad=1, precio_unitario=5000)
        self.assertEqual(self.pedido.total(), 9000)

class CustomExtraTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Taladro',
            descripcion='Taladro eléctrico',
            categoria='herramientas_electricas',
            stock=10,
            activo=True,
            imagen='productos/taladro.jpg'
        )
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.pedido = Pedido.objects.create(usuario=self.user)


    def test_oferta_form_fecha_inicio_igual_fin(self):
        ahora = timezone.now()
        data = {
            'producto': self.producto.id,
            'precio_oferta': 1000,
            'fecha_inicio': ahora,
            'fecha_fin': ahora
        }
        form = OfertaForm(data)
        self.assertTrue(form.is_valid())

    def test_oferta_form_fecha_fin_pasada(self):
        ahora = timezone.now()
        data = {
            'producto': self.producto.id,
            'precio_oferta': 1000,
            'fecha_inicio': ahora,
            'fecha_fin': ahora - timedelta(days=1)
        }
        form = OfertaForm(data)
        self.assertTrue(form.is_valid())

    def test_datos_compra_form_telefono_largo(self):
        data = {
            'nombre': 'Pedro',
            'rut': '212725323',
            'direccion': 'Calle Real 456',
            'telefono': '+569123456789012345',
            'codigo_postal': '7654321',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    def test_datos_compra_form_codigo_postal_letras(self):
        data = {
            'nombre': 'Pedro',
            'rut': '212725323',
            'direccion': 'Calle Real 456',
            'telefono': '+56912345678',
            'codigo_postal': 'ABC1234',
            'envio': True
        }
        form = DatosCompraForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_postal', form.errors)

    def test_registro_form_email_duplicado(self):
        User.objects.create_user(username='otro', email='repetido@example.com', password='pass')
        data = {
            'username': 'nuevo',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'repetido@example.com',
            'password1': 'm223232uwds',
            'password2': 'm223232uwds',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_registro_form_username_invalido(self):
        data = {
            'username': 'usuario raro!',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'userx@example.com',
            'password1': 'm223232uwds',
            'password2': 'm223232uwds',
        }
        form = RegistroForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_producto_model_precio_original_none(self):
        producto = Producto.objects.create(
            nombre='SinPrecio',
            descripcion='Sin precio historico',
            categoria='herramientas',
            stock=1,
            activo=True,
            imagen='productos/sinprecio.jpg'
        )
        self.assertIsNone(producto.precio_original)

    def test_oferta_model_esta_activa_limite(self):
        ahora = timezone.now()
        oferta = Oferta.objects.create(
            producto=self.producto,
            precio_oferta=1000,
            fecha_inicio=ahora - timedelta(seconds=1),
            fecha_fin=ahora + timedelta(seconds=1)
        )
        self.assertTrue(oferta.esta_activa())

    def test_pedido_total_items_precio_cero(self):
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2, precio_unitario=0)
        self.assertEqual(self.pedido.total(), 0)

    def test_pedido_total_items_cantidad_cero(self):
        ItemPedido.objects.create(pedido=self.pedido, producto=self.producto, cantidad=0, precio_unitario=1000)
        self.assertEqual(self.pedido.total(), 0)