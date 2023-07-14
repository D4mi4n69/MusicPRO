from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('registro/', views.registro, name='registro'),
    path('lista_productos', views.lista_productos, name='lista_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('modificar/<id>', views.modificar_producto, name='modificar_producto'),
    path('eliminar/<id>', views.eliminar_producto, name='eliminar_producto'),
    path('carrito', views.carrito, name='carrito'),
    path('agregar/<id>', views.agregar_producto, name='agregar'),
    path('restar/<id>', views.restar_producto, name='restar'),
    path('limpiar/', views.limpiar_carrito, name='limpiar'),
    path('producto_detalle/<int:id>/', views.producto_detalles, name='producto_detalles'),
    path('registro_producto/', views.registro_producto, name='registro_producto'),  #Vendedor 
    path('confirmar_producto/<id>', views.confirmar_producto, name='confirmar_producto'), #Vendedor
    path('registro_despacho/', views.registro_despacho, name='registro_despacho'), #Bodeguero
    path('confirmar_despacho/<id>', views.confirmar_despacho, name='confirmar_despacho'),  #Bodeguero
    path('registro_entrega/', views.registro_entrega, name='registro_entrega'), #Contador
    path('confirmar_entrega/<id>', views.confirmar_entrega, name='confirmar_entrega'),  #Contador
    path('resultado_compra/', views.resultado_compra, name='resultado_compra'),
    path('seguimiento_compra/', views.seguimiento_compra, name='seguimiento_compra'),
    path('perfil/', views.perfil, name='perfil'),
    path('informe_ventas/', views.informe_ventas, name='informe_ventas'),
    path('generar_pdf/', views.generar_pdf, name='generar_pdf'),
]