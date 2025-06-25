from django import forms
from .models import DatosCompra, Oferta, Producto
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
import re

class OfertaForm(forms.ModelForm):
    def clean_precio_oferta(self):
        precio = self.cleaned_data['precio_oferta']
        if precio <= 0:
            raise forms.ValidationError("El precio de la oferta debe ser mayor a cero.")
        return precio
    
    class Meta:
        model = Oferta
        fields = ['producto', 'precio_oferta', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'precio_oferta': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
        }
        
class ProductoForm(forms.ModelForm):
    precio = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'})
    )

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock
    
    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a cero.")
        return precio
    
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'stock', 'imagen']  # NO incluir 'precio' aquí

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'style': 'max-width: 500px;'}),
            'categoria': forms.Select(attrs={'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
        }



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
        label="Correo electrónico"
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}),
        label="Contraseña"
    )

    error_messages = {
        'invalid_login': "Por favor, introduzca un correo electrónico y contraseña correctos.",
        'inactive': "Esta cuenta está inactiva.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes añadir más personalización aquí si es necesario

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Puedes agregar validaciones adicionales si es necesario
        return username
    


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. Nombre')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Apellido')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Debe contener al menos 8 caracteres.'
        self.fields['password2'].help_text = 'Ingrese la misma contraseña para verificación.'

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower() 
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden. Inténtelo de nuevo.")
        
        for field in ['first_name', 'last_name', 'email', 'username']:
            if not cleaned_data.get(field):
                self.add_error(field, forms.ValidationError(f"{field.capitalize()} es requerido."))

        return cleaned_data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    

class DatosCompraForm(forms.ModelForm):
    class Meta:
        model = DatosCompra
        fields = ['nombre', 'rut', 'direccion', 'telefono', 'codigo_postal', 'envio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'envio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        rut = rut.upper().replace('.', '').replace('-', '')
        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise forms.ValidationError('RUT inválido. Debe tener el formato correcto (Ej: 12345678K).')
        if not self.validar_rut(rut):
            raise forms.ValidationError('RUT inválido.')
        return rut

    def validar_rut(self, rut):
        cuerpo = rut[:-1]
        dv = rut[-1].upper()

        suma = 0
        multiplo = 2

        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo += 1
            if multiplo > 7:
                multiplo = 2

        resto = suma % 11
        dv_esperado = 'K' if resto == 1 else '0' if resto == 0 else str(11 - resto)

        return dv == dv_esperado

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if len(direccion.strip()) < 5:
            raise forms.ValidationError('La dirección debe tener al menos 5 caracteres.')
        return direccion

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\+?56\d{9}$', telefono):
            raise forms.ValidationError('Teléfono inválido. Debe tener formato chileno, ejemplo: +56912345678.')
        return telefono

    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        if not re.match(r'^\d{7}$', codigo_postal):
            raise forms.ValidationError('El código postal debe tener 7 dígitos.')
        return codigo_postal

class MotivoRechazoForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo del rechazo',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True
    )

class ObservacionesForm(forms.Form):
    observaciones = forms.CharField(
        label='Observaciones',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una contraseña'}),
        required=False
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme la contraseña'}),
        required=False
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if not self.instance or not self.instance.pk:
            if not password1:
                self.add_error('password1', "La contraseña es obligatoria para nuevos usuarios.")
            if password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden.")
        else:
            if password1 or password2:
                if password1 != password2:
                    self.add_error('password2', "Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()
            group = self.cleaned_data['group']
            user.groups.clear()
            user.groups.add(group)
        return user
