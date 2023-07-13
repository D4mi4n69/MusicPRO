from django.contrib import admin
from .models import Categoria, tipoProducto, Producto, Entrega, Boleta, Compras

# Register your models here.
admin.site.register(Categoria)
admin.site.register(tipoProducto)
admin.site.register(Producto)
admin.site.register(Entrega)
admin.site.register(Boleta)
admin.site.register(Compras)
