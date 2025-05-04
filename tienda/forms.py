from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs=
                {'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'descripcion': forms.Textarea(attrs=
                {'class': 'form-control form-control-sm', 'rows': 3, 'style': 'max-width: 500px;'}),
            'categoria': forms.TextInput(attrs=
                {'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'precio': forms.NumberInput(attrs=
                {'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'}),
            'stock': forms.NumberInput(attrs=
                {'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'}),
            'imagen': forms.ClearableFileInput(attrs=
                {'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
        }
