# Registro de cambios

## [Unreleased]

## 0.2.0 - 2026-11-16

### Added

- Operación `PUT` para reemplazar un producto.
- Operación `PATCH` para actualizar campos parciales de un producto.
- Operación `DELETE` para realizar el borrado lógico de un producto.
- Registro de entradas y salidas de stock con historial por producto.
- Validación de stock y actualización atómica al registrar movimientos.

### Changed

- PUT y PATCH ya no aceptan stock; el stock se modifica solo con movimientos.
- POST /productos con stock inicial registra un movimiento de entrada.

## 0.1.0 - 2026-11-13

- Estructura inicial de Inventario API con FastAPI, SQLAlchemy y Pydantic.
- Endpoints para consultar y crear productos, más el chequeo `/health`.
- Pruebas automatizadas con SQLite en memoria.
