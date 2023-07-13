from django.urls import path
from rest_productos.views import productos

urlpatterns = [
    path('productos', productos, name="productos"),
]