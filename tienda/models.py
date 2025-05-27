from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Producto(models.Model):
    CATEGORIAS = [
        ('herramientas', 'Herramientas'),
        ('herramientas_electricas', 'Herramientas Eléctricas'),
        ('herramientas_manuales', 'Herramientas Manuales'),
        ('materiales', 'Materiales'),
        ('accesorios', 'Accesorios'),
        ('pinturas', 'Pinturas'),
        ('electricidad', 'Electricidad'),
        ('inalambricas', 'Inalámbricas'),
        ('medicion', 'Medición'),
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100, choices=CATEGORIAS)  
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='static/productos/')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    @property
    def oferta_vigente(self):
        ahora = timezone.now()
        return self.ofertas.filter(fecha_inicio__lte=ahora, fecha_fin__gte=ahora).first()

    @property
    def precio_actual(self):
        oferta = self.oferta_vigente
        if oferta:
            return round((oferta.precio_oferta), 0)
        precio = self.precios.first()
        return precio.valor if precio else None

    @property
    def precio_original(self):
        precio = self.precios.first()
        return round((precio.valor),0) if precio else None

class Oferta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ofertas')
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    def esta_activa(self):
        ahora = timezone.now()
        return self.fecha_inicio <= ahora <= self.fecha_fin

    def __str__(self):
        return f"Oferta para {self.producto.nombre} - ${self.precio_oferta}"
    
class PrecioHistorico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios')
    fecha = models.DateTimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.producto.nombre} - {self.valor} ({self.fecha.date()})"


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('en_preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('finalizado', 'Finalizado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    datos_compra = models.OneToOneField('DatosCompra', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado}"
    
    def total(self):
        return sum(item.cantidad * item.precio_unitario for item in self.items.all())



class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de compra

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class DatosCompra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    codigo_postal = models.CharField(max_length=10)
    envio = models.BooleanField(default=True)  # True: envío, False: retiro
    fecha = models.DateTimeField(auto_now_add=True)

class OrdenDespacho(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='orden_despacho')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    motivo_rechazo = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo para entregar'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ], default='pendiente')

    def __str__(self):
        return f"Orden Despacho #{self.id} - Pedido #{self.pedido.id}"
    
    def total(self):
        return sum(item.cantidad * item.precio_unitario for item in self.pedido.items.all())