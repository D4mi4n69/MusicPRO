from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class tipoProducto(models.Model):
    id_tipo_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Tipo de producto")

    def __str__(self):
        return self.nombre
    
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre de subcategoría")
    tipo_producto = models.ForeignKey(tipoProducto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    precio = models.IntegerField()
    stock = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    descripcion = models.TextField(max_length=1000, verbose_name="Descripción del Producto")

    def __str__(self):
        return self.nombre
    
class Entrega(models.Model):
    codigo_entrega = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    confirmacion = models.BooleanField(null=False, blank=False)

    def __str__(self):
        return self.codigo_entrega
    

class Boleta(models.Model):
    estado = models.CharField(max_length=50, verbose_name="Estado del producto")
    codigo_boleta = models.AutoField(primary_key=True)
    cantidad_productos=models.IntegerField()
    total = models.IntegerField()
    fecha = models.DateField()

    def __int__(self):
        return self.codigo_boleta
    

class Compras(models.Model):
    nombre_producto = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    boleta = models.ForeignKey(Boleta, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.IntegerField()

    def __str__(self):
        return self.nombre_producto

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagen = models.ImageField(default='default.jpg', upload_to='productos')

    def __str__(self):
        return f'Perfil de {self.user.username}'

    # Metodo para modificar la función save() para ajustar un máximo en el tamaño de las imágenes si alguna o ambas de sus dimensiones son muy grandes
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.imagen.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.imagen.path)

class Bodeguero(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
class Vendedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
class Contador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username