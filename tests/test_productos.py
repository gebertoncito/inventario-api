from fastapi.testclient import TestClient


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


def test_health(client: TestClient) -> None:
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
