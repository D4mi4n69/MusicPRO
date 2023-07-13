class Carrito():
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito

    def agregar(self, producto):
        encontrado=0
        for key, value in self.carrito.items():
            if value["producto_id"] == producto.codigo_producto:
                value["cantidad"] = int(value["cantidad"])+1
                value["total"] = value["cantidad"] * producto.precio
                encontrado=1
                break
        if encontrado==0:
            self.carrito[producto.codigo_producto] = {
                "producto_id": producto.codigo_producto,
                "nombre": producto.nombre,
                "categoria": producto.categoria.nombre,
                "precio": str (producto.precio),
                "cantidad": 1,
                "total": producto.precio
            }
        self.guardar_carrito()



    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, producto):
        for key, value in self.carrito.items():
            if value["producto_id"] == producto.codigo_producto:
                del self.carrito[key]
                self.guardar_carrito()
                break
    
    def restar(self, producto):
        for key, value in self.carrito.items():
            if value["producto_id"] == producto.codigo_producto:
                value["cantidad"] = int(value["cantidad"]) - 1
                value["total"] = int(value["total"]) - producto.precio
                if int(value["cantidad"]) == 0:
                    self.eliminar(producto)
                break
        self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True





#compra pre liminar hasta esperar la autorizacion de webpay

class Compra():
    def __init__(self, request):
        self.request = request
        self.session = request.session
        compra = self.session.get("compra")
        if not compra:
            compra = self.session["compra"] = {}
        self.compra = compra

    def agregar(self, producto, cantidad):
        self.compra[producto.codigo_producto] = {
            "producto_id": producto.codigo_producto,
            "nombre": producto.nombre,
            "categoria": producto.categoria.nombre,
            "precio": str (producto.precio),
            "cantidad": cantidad,
            "total": producto.precio*cantidad
            }
        self.guardar_compra()



    def guardar_compra(self):
        self.session["compra"] = self.compra
        self.session.modified = True
    

    def limpiar(self):
        self.session["compra"] = {}
        self.session.modified = True