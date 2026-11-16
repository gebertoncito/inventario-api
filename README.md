# Inventario API

API REST para gestionar los productos de una pulpería o tienda. Está construida
con FastAPI, SQLAlchemy 2.0 y Pydantic 2. SQLite es la base de datos
predeterminada para desarrollo y pruebas; PostgreSQL está disponible mediante
Docker.

## Requisitos

- Python 3.12 o superior
- Docker con Docker Compose, si se desea usar PostgreSQL

## Preparar el entorno

Desde la carpeta `inventario-api`, crea y activa el entorno virtual:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

En Windows, si PowerShell no permite activar el entorno, usa:

```powershell
.\.venv\Scripts\activate.bat
```

Copia `.env.example` a `.env` y ajusta `DATABASE_URL` si hace falta. La
aplicación lee la variable de entorno `DATABASE_URL`; SQLite se usa por defecto.

## Configuración

`CORS_ORIGINS` define los orígenes permitidos para las solicitudes del navegador,
separados por comas. Si no se configura, se permite `http://localhost:5173`.

## Usar PostgreSQL

Inicia la base de datos:

```powershell
docker compose up -d db
```

Configura en `.env` la URL:

```text
DATABASE_URL=postgresql+psycopg://inventario:inventario@localhost:5432/inventario
```

Las credenciales del archivo Compose son para desarrollo local; cámbialas antes
de usar la configuración en un entorno productivo.

## Ejecutar la API

```powershell
python -m uvicorn app.main:app --reload
```

La API estará disponible en <http://127.0.0.1:8000>, la documentación interactiva
en <http://127.0.0.1:8000/docs> y el chequeo de estado en
<http://127.0.0.1:8000/health>.

## Endpoints disponibles

- `POST /productos`: crea un producto.
- `GET /productos`: lista los productos activos.
- `GET /productos/{id}`: obtiene un producto activo.
- `PUT /productos/{id}`: reemplaza nombre y precio de un producto activo; no acepta stock.
- `PATCH /productos/{id}`: actualiza nombre o precio; no acepta stock.
- `DELETE /productos/{id}`: realiza el borrado lógico de un producto activo.
- `POST /productos/{id}/movimientos`: registra una entrada o salida de stock.
- `GET /productos/{id}/movimientos`: consulta el historial de movimientos.
- `GET /health`: informa el estado de la API.

Al crear un producto, `POST /productos` acepta un stock inicial; si es mayor que
cero, se registra como un movimiento de entrada. El stock se modifica mediante
`POST /productos/{id}/movimientos`, no mediante PUT ni PATCH.

El nombre es obligatorio y no puede estar vacío; el precio debe ser mayor que
cero y admitir hasta 10 dígitos con 2 decimales; el stock debe ser un entero no
negativo. Las solicitudes inválidas responden con HTTP 422. Las operaciones
de modificación requieren que el producto esté activo; de lo contrario,
responden con HTTP 404.

## Pruebas y lint

```powershell
python -m pytest
python -m ruff check .
```

Las pruebas usan una base de datos SQLite en memoria independiente por caso.

## Archivos principales

- `app/main.py`: configura FastAPI, crea las tablas al iniciar y publica
  `/health`.
- `app/database.py`: configura la conexión, sesiones y dependencia de base de
  datos.
- `app/models.py`: define el modelo SQLAlchemy `Producto`.
- `app/schemas.py`: define los esquemas Pydantic y sus validaciones.
- `app/routes.py`: implementa los endpoints bajo `/productos`.
- `tests/conftest.py`: configura la base de datos temporal y el cliente de
  pruebas.
- `tests/test_productos.py`: comprueba creación, validaciones, listado y 404.
