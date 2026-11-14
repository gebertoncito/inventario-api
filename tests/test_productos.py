from app import main as main_module
from app.models import Producto
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_crear_producto_valido(client: TestClient) -> None:
    respuesta = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": 1,
        "nombre": "Arroz",
        "precio": "25.50",
        "stock": 10,
        "activo": True,
    }


def test_rechazar_precio_negativo(client: TestClient) -> None:
    respuesta = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "-1.00", "stock": 10},
    )

    assert respuesta.status_code == 422


def test_rechazar_precio_con_mas_de_diez_digitos(client: TestClient) -> None:
    respuesta = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "100000000.00", "stock": 10},
    )

    assert respuesta.status_code == 422


def test_rechazar_nombre_vacio(client: TestClient) -> None:
    respuesta = client.post(
        "/productos",
        json={"nombre": "   ", "precio": "25.50", "stock": 10},
    )

    assert respuesta.status_code == 422


def test_rechazar_stock_negativo(client: TestClient) -> None:
    respuesta = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": -1},
    )

    assert respuesta.status_code == 422


def test_listar_productos_creados(client: TestClient) -> None:
    client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )
    client.post(
        "/productos",
        json={"nombre": "Frijoles", "precio": "30.00", "stock": 5},
    )

    respuesta = client.get("/productos")

    assert respuesta.status_code == 200
    assert [producto["nombre"] for producto in respuesta.json()] == [
        "Arroz",
        "Frijoles",
    ]


def test_producto_inexistente_devuelve_404(client: TestClient) -> None:
    respuesta = client.get("/productos/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_put_actualiza_producto_completo(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    respuesta = client.put(
        f"/productos/{creado.json()['id']}",
        json={"nombre": "Frijoles", "precio": "30.00", "stock": 5},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creado.json()["id"],
        "nombre": "Frijoles",
        "precio": "30.00",
        "stock": 5,
        "activo": True,
    }


def test_put_producto_inexistente_devuelve_404(client: TestClient) -> None:
    respuesta = client.put(
        "/productos/999",
        json={"nombre": "Frijoles", "precio": "30.00", "stock": 5},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_put_rechaza_precio_negativo(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    respuesta = client.put(
        f"/productos/{creado.json()['id']}",
        json={"nombre": "Frijoles", "precio": "-1.00", "stock": 5},
    )

    assert respuesta.status_code == 422


def test_patch_actualiza_solo_stock(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    respuesta = client.patch(
        f"/productos/{creado.json()['id']}",
        json={"stock": 5},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creado.json()["id"],
        "nombre": "Arroz",
        "precio": "25.50",
        "stock": 5,
        "activo": True,
    }


def test_patch_cuerpo_vacio_no_cambia_producto(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    respuesta = client.patch(f"/productos/{creado.json()['id']}", json={})

    assert respuesta.status_code == 200
    assert respuesta.json() == creado.json()


def test_patch_rechaza_nombre_vacio(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )

    respuesta = client.patch(
        f"/productos/{creado.json()['id']}",
        json={"nombre": "   "},
    )

    assert respuesta.status_code == 422


def test_delete_oculta_producto_y_conserva_registro_inactivo(
    client: TestClient,
) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )
    producto_id = creado.json()["id"]

    respuesta = client.delete(f"/productos/{producto_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert client.get("/productos").json() == []
    assert client.get(f"/productos/{producto_id}").status_code == 404

    with Session(main_module.engine) as db:
        producto = db.scalar(select(Producto).where(Producto.id == producto_id))

    assert producto is not None
    assert producto.activo is False


def test_delete_producto_ya_eliminado_devuelve_404(client: TestClient) -> None:
    creado = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": 10},
    )
    producto_id = creado.json()["id"]

    primera_respuesta = client.delete(f"/productos/{producto_id}")
    segunda_respuesta = client.delete(f"/productos/{producto_id}")

    assert primera_respuesta.status_code == 204
    assert segunda_respuesta.status_code == 404
    assert segunda_respuesta.json() == {"detail": "Producto no encontrado"}


def test_health(client: TestClient) -> None:
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
