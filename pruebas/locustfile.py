from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Pausa aleatoria de 1 a 2 segundos entre vistas de páginas
    wait_time = between(1, 2)

    @task(1)
    def ver_catalogo(self):
        self.client.get("/catalogo")


    @task(1)
    def ver_empleados(self):
        self.client.get("/empleados")

    @task(1)
    def ver_clientes(self):
        self.client.get("/clientes")

    @task(1)
    def ver_productos(self):
        self.client.get("/productos")

    @task(1)
    def ver_taller(self):
        self.client.get("/taller")

    @task(1)
    def ver_proveedores(self):
        self.client.get("/proveedores")

    @task(1)
    def ver_inventario(self):
        self.client.get("/inventario")

    @task(1)
    def ver_compras(self):
        self.client.get("/ordenes_compra")

    @task(1)
    def cotizar_tradein(self):
        self.client.get("/trade-in")

    @task(1)
    def gestion_tradein(self):
        self.client.get("/empleados/tradein")

    @task(1)
    def ver_ventas(self):
        self.client.get("/admin/validar-pagos")

    @task(1)
    def ver_usuarios(self):
        self.client.get("/usuarios")

