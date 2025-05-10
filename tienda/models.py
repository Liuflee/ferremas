from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):

    CATEGORIAS = [
        ('herramientas', 'Herramientas'),
        ('materiales', 'Materiales'),
        ('accesorios', 'Accesorios'),
        ('pinturas', 'Pinturas'),
        ('electricidad', 'Electricidad'),
        # agrega más categorías si quieres
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100, choices=CATEGORIAS)  
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='static/productos/')

    def __str__(self):
        return self.nombre
    
class DatosCompra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    codigo_postal = models.CharField(max_length=10)
    envio = models.BooleanField(default=True)  # True: envío, False: retiro
    fecha = models.DateTimeField(auto_now_add=True)