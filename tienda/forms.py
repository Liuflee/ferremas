from django import forms
from .models import DatosCompra, Producto
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 'rows': 3, 'style': 'max-width: 500px;'}),
            'categoria': forms.Select(attrs={
                'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'}),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm', 'style': 'max-width: 300px;'}),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-sm', 'style': 'max-width: 500px;'}),
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