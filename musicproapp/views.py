from io import BytesIO
import os
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .models import Producto, Categoria, Boleta, Compras, Perfil, User
from .forms import CustomUserCreationForm, ProductoForm, formularioModificacionPerfil, BoletaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from musicproapp.compra import Carrito, Compra
from django.core.paginator import Paginator
from django.contrib import messages
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction
import matplotlib.pyplot as plt
import random
import requests
from datetime import date
from django.db.models import Sum
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def index(request):
    categorias = Categoria.objects.all() 
    categoria_buscada = request.GET.get('categoria')  

    if categoria_buscada:  
        productos = Producto.objects.filter(categoria__nombre=categoria_buscada).order_by('categoria')
    else:
        productos = Producto.objects.all().order_by('categoria')

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_filtrada': categoria_buscada
    }

        #Lo siguiente es la api para la conversion de moneda
    convertor = request.GET.get('moneda')
    if convertor:
        context["moneda"]= convertor
        url = 'https://v6.exchangerate-api.com/v6/4a502b3c64d89bf561e72b72/pair/CLP/'+str(convertor)
        response = requests.get(url)
        conversion = response.json()
        context["conversion"]=conversion

    return render(request, 'index.html', context)



def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    context = {'producto': producto}
    return render(request, 'producto_detalles.html', context)


def nosotros(request):
    context = {}
    return render(request, 'nosotros.html', context)



def carrito(request):
    carrito = Carrito(request)
    producto=Producto.objects.all()
    print(carrito.carrito)  # Agregar este print para verificar los datos del carrito
    suma=0
    descuento=0

    #Esto es para sacar el total a pagar de los productos
    for key,i in carrito.carrito.items():
        suma=int(i["total"])+suma

    if len(carrito.carrito.items()) > 4:
        if request.user.is_authenticated:
            suma= suma*0.9
            descuento=1


 
    context = {
        'carrito': carrito,
        'request': request,
        'total':suma,
        'descuento':descuento
    }


    #Con esto se comprueba si hay stock suficiente para cubrir la compra
    for key,i in carrito.carrito.items():
        producto=Producto.objects.get(codigo_producto=i["producto_id"])
        if i["cantidad"]>producto.stock:
            context["error"]='No tenemos suficiente stock del producto: "'+producto.nombre+'". Lamentamos el inconveniente.'
            break

    #Lo siguiente es la api de transbank
    try:
        orden=len(Boleta.objects.all())+1 
        buy_order=str(orden)
        session_id= request.session.session_key
        amount=suma
        return_url= request.build_absolute_uri('/') + 'resultado_compra/'

        create_request = {
            "buy_order": buy_order,
            "session_id": session_id,
            "amount" : amount,
            "return_url": return_url
            }
        
        response= (Transaction()).create(buy_order, session_id, amount, return_url)
        context["response"]=response

        limpiar_comprapreliminar(request)
        for key,i in carrito.carrito.items():
            agregar_comprapreliminar(request=request, id=i["producto_id"], cantidad=i["cantidad"])

        compra = Compra(request) #Quitarlo después ------------------------------------
        print("lista de compra preliminar: "+str(compra.compra)) #Quitarlo después ------------------------------------

        return render(request, 'carrito.html', context)

    except:
        return render(request, 'carrito.html', context)
    




    
def registro(request):
    datos = {
        'form': CustomUserCreationForm()
    }
    perfil=Perfil
    user=User

    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            nombre_usuario=formulario.instance.username
            usuario=user.objects.get(username=nombre_usuario)
            perfil.objects.create(user=usuario)
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            return redirect(to="index")
        else:
            datos['form'] = formulario
    
    return render (request, 'registration/registro.html', datos)

    
#Crud de productos
@login_required
@user_passes_test(lambda u: u.is_superuser)
def lista_productos(request):

    producto = Producto.objects.all().order_by('codigo_producto')
    
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(producto, 5)
        producto = paginator.page(page)
    except:
        raise Http404

    context = {
        'entity' : producto,
        'paginator': paginator
    }
    return render(request, 'admin/lista-productos.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_producto(request):
    context = {
        'form': ProductoForm
    }
    if request.method=='POST':
        productos_form = ProductoForm(data=request.POST, files=request.FILES)
        if productos_form.is_valid():
            productos_form.save()
            messages.success(request, "Producto agregado exitosamente.")
            return redirect(to="lista_productos")
        else:
            context['form'] = productos_form
    
    return render(request, 'admin/crear-producto.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def modificar_producto(request, id):
    productos = get_object_or_404(Producto, codigo_producto=id)
    context = {
        'form': ProductoForm(instance = productos)
    }
    if request.method=='POST':
        formulario = ProductoForm(data=request.POST, instance=productos, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto modificado exitosamente.")
            return redirect(to="lista_productos")
        context["form"] = formulario
              
    return render(request, 'admin/modificar-producto.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, codigo_producto=id)
    messages.success(request, "Producto eliminado exitosamente.")
    producto.delete()
    return redirect(to="lista_productos") 


def producto_detalles(request, id):
    context = {}
    producto = Producto.objects.get(codigo_producto=id)
    if(producto):
        context["producto"]=producto
        return render(request, 'producto_detalles.html', context)
    else:
        context["error"]="No se ha podido encontrar el producto que buscas, intentalo nuevamente más tarde"
        return render(request, 'producto_detalles.html', context)

#------------------------------- Funciones para el carrito --------------------------------------------------------
def agregar_producto(request,id):
    carrito_compra= Carrito(request)
    producto = Producto.objects.get(codigo_producto=id)
    carrito_compra.agregar(producto=producto)
    url_anterior = request.META.get('HTTP_REFERER')
    return redirect(to='carrito')

    # if 'carrito' in url_anterior:      ------------ Decidí comentarlo de momento porque no sé que querian hacer aca XD ----------------
    #     return redirect('carrito')
    # else:
    #     return redirect('index')


# def eliminar_producto(request, id):
#     carrito_compra= Carrito(request)
#     producto = Producto.objects.get(codigo_producto=id)
#     carrito_compra.eliminar(producto=producto)
#     return redirect(to="carrito")

def restar_producto(request, id):
    carrito_compra= Carrito(request)
    producto = Producto.objects.get(codigo_producto=id)
    carrito_compra.restar(producto=producto)
    return redirect(to="carrito")

def limpiar_carrito(request):
    carrito_compra= Carrito(request)
    carrito_compra.limpiar()
    return redirect(to="carrito")    

#------------------------------- Funciones preliminares para la compra --------------------------------------------------------

def agregar_comprapreliminar(request,id,cantidad):
    carrito_compra= Compra(request)
    producto = Producto.objects.get(codigo_producto=id)
    carrito_compra.agregar(producto=producto, cantidad=cantidad)

def limpiar_comprapreliminar(request):
    carrito_compra= Compra(request)
    carrito_compra.limpiar()  

 #------------------------------------------------------------------- Vendedor -----------------------------------------------------------
@login_required
def registro_producto(request):
    producto = Boleta.objects.all().order_by('codigo_boleta').filter(estado="Pagado")

    context = {
        'producto' : producto
    }
    return render(request, 'vendedor/registro-entrega.html', context)

@login_required
def confirmar_producto(request, id):
    productos = get_object_or_404(Boleta, codigo_boleta=id)
    context = {
        'form': BoletaForm(instance = productos)
    }
    if request.method=='POST':
        formulario = BoletaForm(data=request.POST, instance=productos, files=request.FILES)
        if formulario.is_valid():
            if request.POST["value"] == "Rechazar Pedido":
                formulario.instance.estado="Rechazado"
                formulario.save()
                messages.success(request, "Pedido rechazado exitosamente.")
                return redirect(to="registro_producto")
            else:
                formulario.instance.estado="Aceptado"
                formulario.save()
                messages.success(request, "Pedido confirmado exitosamente.")
                return redirect(to="registro_producto")
        context["form"] = formulario
        
              
    return render(request, 'vendedor/confirmar-producto.html', context)


 #------------------------------------------------------------------- Bodeguero -----------------------------------------------------------

@login_required
def registro_despacho(request):
    producto = Boleta.objects.all().order_by('codigo_boleta').filter(estado="Aceptado")

    context = {
        'producto' : producto
    }
    return render(request, 'bodeguero/registro-despacho.html', context)

@login_required
def confirmar_despacho(request, id):
    productos = get_object_or_404(Boleta, codigo_boleta=id)
    context = {
        'form': BoletaForm(instance = productos)
    }
    if request.method=='POST':
        formulario = BoletaForm(data=request.POST, instance=productos, files=request.FILES)
        if formulario.is_valid():
            formulario.instance.estado="Despachado"
            formulario.save()
            messages.success(request, "Pedido despachado exitosamente.")
            return redirect(to="registro_despacho")
        context["form"] = formulario
        
              
    return render(request, 'bodeguero/confirmar-despacho.html', context)

    
 #------------------------------------------------------------------- Contador -----------------------------------------------------------

@login_required
def registro_entrega(request):
    producto = Boleta.objects.all().order_by('codigo_boleta').filter(estado="Despachado")

    context = {
        'producto' : producto
    }
    return render(request, 'contador/registro-entrega.html', context)

@login_required
def confirmar_entrega(request, id):
    productos = get_object_or_404(Boleta, codigo_boleta=id)
    context = {
        'form': BoletaForm(instance = productos)
    }
    if request.method=='POST':
        formulario = BoletaForm(data=request.POST, instance=productos, files=request.FILES)
        if formulario.is_valid():
            formulario.instance.estado="Entregado"
            formulario.save()
            messages.success(request, "Pedido marcado como entregado exitosamente.")
            return redirect(to="registro_entrega")
        context["form"] = formulario
        
              
    return render(request, 'contador/confirmar-entrega.html', context)




def resultado_compra(request):
    try:
        compra = Compra(request)
        boleta = Boleta
        compras = Compras
        context = {}
        token = request.GET.get("token_ws")
        print("commit for token_ws: {}".format(token))

        response = (Transaction()).commit(token=token)

        # En el caso de que el pago se haya efectuado correctamente:
        if response['status'] == "AUTHORIZED":
            suma = 0
            numero_boleta = len(boleta.objects.all()) + 1
            fecha_actual= date.today()
            for key, i in compra.compra.items():
                suma = int(i["total"]) + suma
            boleta.objects.create(codigo_boleta=numero_boleta, cantidad_productos=len(compra.compra.items()), total=suma, estado="Pagado", fecha=fecha_actual)  
            # Tipos de estado:
            # Pagado -> Cuando recien se efecuta la compra
            # Aceptado / Rechazado 
            # Enviado
            # Entregado

            for key, i in compra.compra.items():
                compras.objects.create(nombre_producto=i["nombre"], boleta=Boleta.objects.get(codigo_boleta=numero_boleta), cantidad=i["cantidad"], total=i["total"])
                producto=Producto.objects.get(codigo_producto=i["producto_id"])
                producto.stock=producto.stock-int(i["cantidad"]) #Con esto ya se estaría descontando la cantidad comprada del stock
                producto.save()

            context["mensaje"] = "Has realizado tu compra exitosamente, tu número de boleta es: " + str(numero_boleta)
            limpiar_carrito(request) #Esto es para que se limpie el carrito una vez realizada la compra

            return render(request, 'resultado_pago.html', context)
        
        else:
            context["mensaje"]="Al parecer ha ocurrido un error al realizad tu compra, intentalo nuevamente más tarde."
            context["error"]=1
            return render(request, 'resultado_pago.html', context)
    except:
        return redirect(to='index')




def seguimiento_compra(request):
    codigo_boleta = request.GET.get('codigo_boleta')
    if codigo_boleta:
        try:
            boleta = Boleta.objects.get(codigo_boleta=codigo_boleta)
            compras = Compras.objects.filter(boleta=boleta)

            context = {
                'boleta': boleta,
                'compras': compras,
            }
            return render(request, 'seguimiento_compra.html', context)

        except Boleta.DoesNotExist:
            error = 'La boleta especificada no existe.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': error})
            else:
                return render(request, 'seguimiento_compra.html', {'error': error})
    else:
        return render(request, 'seguimiento_compra.html')



@login_required
def perfil(request):
    if request.method == 'POST':
        profile_update_form = formularioModificacionPerfil(request.POST, request.FILES, instance=request.user.perfil)
        if profile_update_form.is_valid():
            profile_update_form.save()
            messages.success(request, "La imagen de perfil se ha modificado con éxito.")
            return redirect('perfil')
    else:
        profile_update_form = formularioModificacionPerfil(instance=request.user.perfil)

    context = {
        'p_form': profile_update_form,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'titulo': 'Perfil de Usuario',
    }

    return render(request, 'perfil.html', context)



def generar_pdf(request):
    template_path = 'admin/informe_ventas.html'
    context = {}  

    # Cargar la plantilla HTML
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_ventas.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response



def informe_ventas(request):
# Obtener los productos vendidos y la cantidad total de ventas por producto
    ventas_por_producto = Compras.objects.values('nombre_producto').annotate(total_ventas=Sum('cantidad')).order_by('-total_ventas')[:5]
    productos = [venta['nombre_producto'] for venta in ventas_por_producto]
    total_ventas = [venta['total_ventas'] for venta in ventas_por_producto]

    cantidad_total_ventas = sum(total_ventas)

    # Obtener la cantidad de productos
    cantidad_productos = Producto.objects.count()

    # Obtener la cantidad de usuarios registrados
    cantidad_usuarios = User.objects.count()

    # Obtener los ingresos ganados (suma del campo 'total' de Compras)
    ingresos_ganados = Compras.objects.aggregate(total_ingresos=Sum('total'))['total_ingresos'] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_ventas.pdf"'

    buffer = BytesIO()

    # Crear el documento PDF
    p = canvas.Canvas(buffer)

    # Agregar contenido al PDF
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, "Informe de Ventas")
    p.drawString(100, 750, "Productos más vendidos:")

    y_position = 720
    for producto, ventas in zip(productos, total_ventas):
        p.drawString(120, y_position, f"- {producto}: {ventas} unidades")
        y_position -= 20

    p.drawString(100, y_position, f"Cantidad total de productos vendidos: {cantidad_total_ventas}")
    p.drawString(100, y_position - 20, f"Ingresos ganados: ${ingresos_ganados:,.0f}")

    # Finalizar el documento PDF
    p.showPage()
    p.save()

    # Obtener el valor del buffer y añadirlo a la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    # Configurar los colores y etiquetas para el gráfico circular
    colores = ['blue', 'green', 'orange', 'red', 'purple']
    etiquetas = productos

    # Crear el gráfico circular
    plt.pie(total_ventas, labels=etiquetas, colors=colores, autopct='%1.1f%%')
    plt.title('Informe de Ventas')

    # Guardar el gráfico en un archivo
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'informe_ventas.png'))

    # Obtener la URL del gráfico generado
    url_informe_ventas = os.path.join(settings.MEDIA_URL, 'informe_ventas.png')

    # Agregar los valores al contexto
    context = {
        'url_informe_ventas': url_informe_ventas,
        'cantidad_total_ventas': cantidad_total_ventas,
        'cantidad_productos': cantidad_productos,
        'cantidad_usuarios': cantidad_usuarios,
        'ingresos_ganados': ingresos_ganados
    }

    return render(request, 'admin/informe_ventas.html', context)


