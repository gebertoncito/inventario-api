from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


def crear_producto(client: TestClient, stock: int = 10) -> int:
    respuesta = client.post(
        "/productos",
        json={"nombre": "Arroz", "precio": "25.50", "stock": stock},
    )

    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def test_entrada_suma_stock_y_responde_con_movimiento(client: TestClient) -> None:
    producto_id = crear_producto(client)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "entrada", "cantidad": 5},
    )

    assert respuesta.status_code == 201
    movimiento = respuesta.json()
    assert movimiento["producto_id"] == producto_id
    assert movimiento["tipo"] == "entrada"
    assert movimiento["cantidad"] == 5
    assert movimiento["nota"] is None
    fecha = datetime.fromisoformat(movimiento["fecha"])
    assert fecha.utcoffset() == timedelta(0)
    assert client.get(f"/productos/{producto_id}").json()["stock"] == 15


def test_salida_resta_stock(client: TestClient) -> None:
    producto_id = crear_producto(client)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "salida", "cantidad": 4},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["tipo"] == "salida"
    assert client.get(f"/productos/{producto_id}").json()["stock"] == 6


def test_salida_mayor_que_stock_devuelve_409_y_no_cambia_stock(
    client: TestClient,
) -> None:
    producto_id = crear_producto(client)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "salida", "cantidad": 11},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Stock insuficiente"}
    assert client.get(f"/productos/{producto_id}").json()["stock"] == 10


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_no_positiva_devuelve_422(
    client: TestClient,
    cantidad: int,
) -> None:
    producto_id = crear_producto(client)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "entrada", "cantidad": cantidad},
    )

    assert respuesta.status_code == 422


def test_tipo_invalido_devuelve_422(client: TestClient) -> None:
    producto_id = crear_producto(client)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "ajuste", "cantidad": 1},
    )

    assert respuesta.status_code == 422


def test_movimiento_de_producto_inexistente_devuelve_404(
    client: TestClient,
) -> None:
    respuesta = client.post(
        "/productos/999/movimientos",
        json={"tipo": "entrada", "cantidad": 1},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_movimiento_de_producto_eliminado_devuelve_404(
    client: TestClient,
) -> None:
    producto_id = crear_producto(client)
    assert client.delete(f"/productos/{producto_id}").status_code == 204

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "entrada", "cantidad": 1},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_historial_ordenado_por_fecha_e_id_descendentes(
    client: TestClient,
) -> None:
    producto_id = crear_producto(client)
    movimientos = []
    for tipo, cantidad in (("entrada", 1), ("salida", 1), ("entrada", 2)):
        respuesta = client.post(
            f"/productos/{producto_id}/movimientos",
            json={"tipo": tipo, "cantidad": cantidad},
        )
        assert respuesta.status_code == 201
        movimientos.append(respuesta.json())

    respuesta = client.get(f"/productos/{producto_id}/movimientos")

    assert respuesta.status_code == 200
    esperados = sorted(
        movimientos,
        key=lambda movimiento: (movimiento["fecha"], movimiento["id"]),
        reverse=True,
    )
    assert respuesta.json() == esperados


def test_historial_de_producto_inexistente_devuelve_404(
    client: TestClient,
) -> None:
    respuesta = client.get("/productos/999/movimientos")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_nota_se_recorta_y_nota_vacia_se_guarda_como_nula(
    client: TestClient,
) -> None:
    producto_id = crear_producto(client)

    respuesta_con_nota = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "entrada", "cantidad": 1, "nota": "  reposición  "},
    )
    respuesta_nota_vacia = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "entrada", "cantidad": 1, "nota": "   "},
    )

    assert respuesta_con_nota.status_code == 201
    assert respuesta_con_nota.json()["nota"] == "reposición"
    assert respuesta_nota_vacia.status_code == 201
    assert respuesta_nota_vacia.json()["nota"] is None


def test_salida_insuficiente_no_registra_movimiento(client: TestClient) -> None:
    producto_id = crear_producto(client, stock=2)

    respuesta = client.post(
        f"/productos/{producto_id}/movimientos",
        json={"tipo": "salida", "cantidad": 3},
    )

    assert respuesta.status_code == 409
    assert client.get(f"/productos/{producto_id}/movimientos").json() == []
