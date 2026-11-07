"""Pruebas de integración de la clase Equipo contra MySQL real."""
import random

import pytest

from app.models.equipo import Equipo
from seed_helpers import crear_producto_temporal, eliminar_producto_temporal


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"


def _id_equipo_aleatorio() -> str:
    """Genera un IMEI de 15 dígitos único para cada test."""
    return str(random.randint(10**14, 10**15 - 1))


def _producto_valido() -> str:
    """Crea un producto temporal y devuelve su ID."""
    return crear_producto_temporal(
        nombre="Producto Equipo Integracion", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
    )


# ==================== CONSULTAR ====================

class TestConsultarEquipo:

    def test_equipo_inexistente(self):
        assert Equipo(ID_equipo="999999999999999").Consultar_equipo_por_id() is None

    def test_sin_id_equipo(self):
        assert Equipo().Consultar_equipo_por_id() is None

    def test_equipo_existente(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            resultado = Equipo(
                ID_equipo=id_equipo,
                ID_producto=id_producto,
                Color="Negro",
                Capacidad="128GB",
                Clave="1234",
                Patron="1-2-3-4",
            ).registrar_equipo()
            assert resultado == f"Equipo {id_equipo} registrado exitosamente."

            consultado = Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id()

            assert consultado is not None
            assert consultado["ID_equipo"] == id_equipo
            assert consultado["ID_producto"] == id_producto
            assert consultado["Color"] == "Negro"
            assert consultado["Capacidad"] == "128GB"
            assert consultado["Clave"] == 1234
            assert consultado["Patron"] == "1-2-3-4"
            assert consultado["Nombre_producto"] == "Producto Equipo Integracion"
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)


# ==================== REGISTRAR ====================

class TestRegistrarEquipo:

    def test_datos_validos_sin_opcionales(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()

            resultado = Equipo(
                ID_equipo=id_equipo,
                ID_producto=id_producto,
            ).registrar_equipo()

            assert resultado == f"Equipo {id_equipo} registrado exitosamente."

            consultado = Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id()
            assert consultado["Color"] is None
            assert consultado["Capacidad"] is None
            assert consultado["Clave"] is None
            assert consultado["Patron"] is None
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_datos_validos_con_todos_los_campos(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()

            resultado = Equipo(
                ID_equipo=id_equipo,
                ID_producto=id_producto,
                Color="Blanco",
                Capacidad="256GB",
                Clave="9876",
                Patron="9-8-7-6-5-4",
            ).registrar_equipo()

            assert resultado == f"Equipo {id_equipo} registrado exitosamente."

            consultado = Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id()
            assert consultado["Color"] == "Blanco"
            assert consultado["Capacidad"] == "256GB"
            assert consultado["Clave"] == 9876
            assert consultado["Patron"] == "9-8-7-6-5-4"
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_equipo_duplicado(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(ID_equipo=id_equipo, ID_producto=id_producto).registrar_equipo()

            resultado = Equipo(
                ID_equipo=id_equipo, ID_producto=id_producto
            ).registrar_equipo()

            assert resultado == f"El equipo '{id_equipo}' ya existe."
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_sin_id_equipo(self):
        resultado = Equipo(ID_producto="1").registrar_equipo()
        assert resultado == "El ID del equipo es obligatorio."

    def test_sin_id_producto(self):
        resultado = Equipo(ID_equipo=_id_equipo_aleatorio()).registrar_equipo()
        assert resultado == "El ID del producto es obligatorio."

    def test_id_equipo_demasiado_largo(self):
        resultado = Equipo(
            ID_equipo="1" * 17, ID_producto="1"
        ).registrar_equipo()
        assert resultado == "El ID del equipo no puede tener más de 15 caracteres."

    def test_color_demasiado_largo(self):
        id_producto = None
        try:
            id_producto = _producto_valido()
            resultado = Equipo(
                ID_equipo=_id_equipo_aleatorio(),
                ID_producto=id_producto,
                Color="C" * 31,
            ).registrar_equipo()
            assert resultado == "El color no puede tener más de 30 caracteres."
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_capacidad_demasiado_larga(self):
        id_producto = None
        try:
            id_producto = _producto_valido()
            resultado = Equipo(
                ID_equipo=_id_equipo_aleatorio(),
                ID_producto=id_producto,
                Capacidad="C" * 7,
            ).registrar_equipo()
            assert resultado == "La capacidad no puede tener más de 6 caracteres."
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_clave_no_numerica(self):
        id_producto = None
        try:
            id_producto = _producto_valido()
            resultado = Equipo(
                ID_equipo=_id_equipo_aleatorio(),
                ID_producto=id_producto,
                Clave="abc",
            ).registrar_equipo()
            assert resultado == "La clave debe ser un número entero válido."
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_patron_demasiado_largo(self):
        id_producto = None
        try:
            id_producto = _producto_valido()
            resultado = Equipo(
                ID_equipo=_id_equipo_aleatorio(),
                ID_producto=id_producto,
                Patron="1-2-3-4-5-6-7-8-9-0",
            ).registrar_equipo()
            assert resultado == "El patrón no puede tener más de 17 caracteres."
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


# ==================== ACTUALIZAR ====================

class TestActualizarEquipo:

    def test_actualiza_solo_color(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(
                ID_equipo=id_equipo, ID_producto=id_producto, Color="Negro", Capacidad="128GB"
            ).registrar_equipo()

            resultado = Equipo(
                ID_equipo=id_equipo, Color="Rojo"
            ).actualizar_equipo()

            assert resultado == f"Equipo {id_equipo} actualizado correctamente."

            consultado = Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id()
            assert consultado["Color"] == "Rojo"
            assert consultado["Capacidad"] == "128GB"  # no se tocó
            assert consultado["ID_producto"] == id_producto  # no se tocó
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_actualiza_todos_los_campos(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(
                ID_equipo=id_equipo, ID_producto=id_producto, Color="Negro"
            ).registrar_equipo()

            resultado = Equipo(
                ID_equipo=id_equipo,
                Color="Azul",
                Capacidad="512GB",
                Clave="1111",
                Patron="1-1-1-1",
            ).actualizar_equipo()

            assert resultado == f"Equipo {id_equipo} actualizado correctamente."

            consultado = Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id()
            assert consultado["Color"] == "Azul"
            assert consultado["Capacidad"] == "512GB"
            assert consultado["Clave"] == 1111
            assert consultado["Patron"] == "1-1-1-1"
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_equipo_inexistente(self):
        resultado = Equipo(
            ID_equipo="999999999999999", Color="Rojo"
        ).actualizar_equipo()
        assert resultado == "No se encontró el equipo 999999999999999."

    def test_sin_id_equipo(self):
        resultado = Equipo(Color="Rojo").actualizar_equipo()
        assert resultado == "El ID del equipo es obligatorio."

    def test_sin_datos_para_actualizar(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(ID_equipo=id_equipo, ID_producto=id_producto).registrar_equipo()

            resultado = Equipo(ID_equipo=id_equipo).actualizar_equipo()
            assert resultado == "No hay datos para actualizar."
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_color_demasiado_largo(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(ID_equipo=id_equipo, ID_producto=id_producto).registrar_equipo()

            resultado = Equipo(
                ID_equipo=id_equipo, Color="C" * 31
            ).actualizar_equipo()
            assert resultado == "El color no puede tener más de 30 caracteres."
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_clave_no_numerica(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(ID_equipo=id_equipo, ID_producto=id_producto).registrar_equipo()

            resultado = Equipo(
                ID_equipo=id_equipo, Clave="abc"
            ).actualizar_equipo()
            assert resultado == "La clave debe ser un número entero válido."
        finally:
            if id_producto:
                Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)


# ==================== ELIMINAR ====================

class TestEliminarEquipo:

    def test_elimina_equipo_sin_relaciones(self):
        id_producto = None
        id_equipo = _id_equipo_aleatorio()
        try:
            id_producto = _producto_valido()
            Equipo(ID_equipo=id_equipo, ID_producto=id_producto).registrar_equipo()

            resultado = Equipo(ID_equipo=id_equipo).eliminar_equipo()

            assert resultado == f"Equipo {id_equipo} eliminado correctamente."
            assert Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id() is None
        finally:
            if id_producto:
                if Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id():
                    Equipo(ID_equipo=id_equipo).eliminar_equipo()
                eliminar_producto_temporal(id_producto)

    def test_equipo_inexistente(self):
        resultado = Equipo(ID_equipo="999999999999999").eliminar_equipo()
        assert resultado == "No se encontró el equipo 999999999999999."

    def test_sin_id_equipo(self):
        resultado = Equipo().eliminar_equipo()
        assert resultado == "El ID del equipo es obligatorio."