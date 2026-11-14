# Registro de cambios

## [Unreleased]

### Added

- Operación `PUT` para reemplazar un producto.
- Operación `PATCH` para actualizar campos parciales de un producto.
- Operación `DELETE` para realizar el borrado lógico de un producto.

## 0.1.0 - 2026-11-13

- Estructura inicial de Inventario API con FastAPI, SQLAlchemy y Pydantic.
- Endpoints para consultar y crear productos, más el chequeo `/health`.
- Pruebas automatizadas con SQLite en memoria.
