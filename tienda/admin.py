from django.contrib import admin

# Register your models here.
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)
    ordering = ('-precio',) 