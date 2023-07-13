from django import forms
from .models import Perfil, Producto, Entrega
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria', 'imagen', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre del Producto'
        self.fields['precio'].label = 'Precio'
        self.fields['stock'].label = 'Stock'
        self.fields['categoria'].label = 'Categoría'
        self.fields['imagen'].label = 'Imagen'
        self.fields['imagen'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['descripcion'].label = 'Descripción'

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if first_name and len(first_name.strip()) < 3 or len(first_name.strip()) > 15:
            self.add_error("first_name", "El primer nombre debe tener entre 3 y 15 caracteres sin espacios en blanco.")

        if last_name and len(last_name.strip()) < 3 or len(last_name.strip()) > 15:
            self.add_error("last_name", "El apellido debe tener entre 3 y 15 caracteres sin espacios en blanco.")

class EntregaForm(forms.ModelForm):
    confirmacion = forms.BooleanField(required=False, widget=forms.CheckboxInput)

    class Meta:
        model = Entrega
        fields = ['name', 'confirmacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Nombre del Producto'


class formularioModificacionPerfil(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['imagen']
