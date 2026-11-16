from fastapi.testclient import TestClient


def test_preflight_permite_origen_del_frontend(client: TestClient) -> None:
    respuesta = client.options(
        "/productos",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_preflight_no_permite_origen_no_autorizado(client: TestClient) -> None:
    respuesta = client.options(
        "/productos",
        headers={
            "Origin": "http://malicioso.test",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in respuesta.headers
