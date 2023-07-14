from django.contrib import admin
from .models import Categoria, tipoProducto, Producto, Boleta, Compras, Perfil, Bodeguero, Vendedor, Contador

# Register your models here.
admin.site.register(Categoria)
admin.site.register(tipoProducto)
admin.site.register(Producto)
admin.site.register(Boleta)
admin.site.register(Compras)
admin.site.register(Perfil)
admin.site.register(Bodeguero)
admin.site.register(Vendedor)
admin.site.register(Contador)