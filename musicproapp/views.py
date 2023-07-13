from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .models import Producto, Categoria, Entrega, Boleta, Compras
from .forms import CustomUserCreationForm, ProductoForm, EntregaForm, formularioModificacionPerfil
from django.contrib.auth.decorators import login_required, user_passes_test
from musicproapp.compra import Carrito, Compra
from django.core.paginator import Paginator
from django.contrib import messages

from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction


import random


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

    #Esto es para sacar el total a pagar de los productos
    for key,i in carrito.carrito.items():
        suma=int(i["total"])+suma

 
    context = {
        'carrito': carrito,
        'request': request,
        'total':suma,
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

        limpiar_comprapreliminar(request)
        for key,i in carrito.carrito.items():
            agregar_comprapreliminar(request=request, id=i["producto_id"])

        compra = Compra(request) #Quitarlo después ------------------------------------
        print("lista de compra preliminar: "+str(compra.compra)) #Quitarlo después ------------------------------------

        response= (Transaction()).create(buy_order, session_id, amount, return_url)
        context["response"]=response
        return render(request, 'carrito.html', context)
    
    except:

        return render(request, 'carrito.html', context)

    
def registro(request):
    datos = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
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

    if 'carrito' in url_anterior:
        return redirect('carrito')
    else:
        return redirect('index')


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

def agregar_comprapreliminar(request,id):
    carrito_compra= Compra(request)
    producto = Producto.objects.get(codigo_producto=id)
    carrito_compra.agregar(producto=producto)

def limpiar_comprapreliminar(request):
    carrito_compra= Compra(request)
    carrito_compra.limpiar()  


@login_required
@user_passes_test(lambda u: u.is_superuser)
def registro_entrega(request):
    producto = Producto.objects.all().order_by('codigo_producto')
    context = {
        'producto' : producto
    }
    return render(request, 'contador/registro-entrega.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def confirmar_producto(request, id):
    entrega = get_object_or_404(Entrega, codigo_entrega=id)
    if request.method == 'POST':
        formulario = EntregaForm(data=request.POST, instance=entrega, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('confirmar_producto', id=id)
    else:
        formulario = EntregaForm(instance=entrega)

    context = {
        'form': formulario,
        'entrega': entrega,
    }
    return render(request, 'contador/confirmar-producto.html', context)


    


def webpay_plus_create(request):
    context={}
    print("Webpay Plus Transaction.create")
    buy_order = str(random.randrange(1000000, 99999999))
    session_id = str(random.randrange(1000000, 99999999))
    amount = random.randrange(10000, 1000000)
    return_url = request.build_absolute_uri('/') +'resultado_compra//'

    create_request = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": amount,
        "return_url": return_url
    }

    response = (Transaction()).create(buy_order, session_id, amount, return_url)
    print("Este es el response: "+ str(response))
    context["response"]=response

    return render(request, 'create.html', context)   


def resultado_compra(request):
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
        for key, i in compra.compra.items():
            suma = int(i["total"]) + suma
        boleta.objects.create(codigo_boleta=numero_boleta, cantidad_productos=len(compra.compra.items()), total=suma, estado=False)  # Establecer estado en False

        for key, i in compra.compra.items():
            compras.objects.create(nombre_producto=i["nombre"], boleta=Boleta.objects.get(codigo_boleta=numero_boleta), cantidad=i["cantidad"], total=i["total"])

        context["mensaje"] = "Has realizado tu compra exitosamente, tu número de boleta es: " + str(numero_boleta)

    return render(request, 'resultado_pago.html', context)




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



