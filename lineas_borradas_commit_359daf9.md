# Líneas borradas del commit 359daf9

## app/controllers/empleados.py
```python
@empleados_blueprint.route("/api/especialidades", methods=["GET"])
@jwt_required
def api_listar_especialidades():
    empleados = Empleados()
    resultado = empleados.listar_especialidades()
    return jsonify(resultado)
```

## app/controllers/productos.py
```python
modelo = Productos()
```

## app/controllers/proveedores.py
```python
modelo = Proveedores()
productos_modelo = Productos()
```

## app/models/clientes.py
```python
<<<<<<< HEAD
=======
>>>>>>> 2f82cfda297eab91d337a033612ea877fe5729f0
```

## app/models/empleados.py
```python
<<<<<<< HEAD
=======
>>>>>>> 2f82cfda297eab91d337a033612ea877fe5729f0
```

## app/models/productos.py
```python
# Bloques de conexión y cursor reemplazados por _consultar y _ejecutar.
# Se eliminaron las versiones manuales de listar/crear/actualizar/eliminar para clases, marcas y modelos.
```

## app/models/proveedores.py
```python
# Bloques de conexión y cursor reemplazados por _consultar y _ejecutar.
# Se eliminaron las versiones manuales de listar/crear/actualizar/eliminar para proveedores y productos asociados.
```

## app/models/usuarios.py
```python
<<<<<<< HEAD
```
