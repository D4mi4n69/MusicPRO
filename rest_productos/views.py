from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from musicproapp.models import Producto
from .serializers import ProductoSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status

@csrf_exempt
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def productos(request):
    if request.method == "GET":
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = ProductoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        producto = get_object_or_404(Producto, pk=data['codigo_producto'])
        serializer = ProductoSerializer(producto, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        data = JSONParser().parse(request)
        producto = get_object_or_404(Producto, pk=data['codigo_producto'])
        producto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
