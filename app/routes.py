from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MovimientoInventario, Producto
from app.schemas import (
    MovimientoCreate,
    MovimientoOut,
    ProductoCreate,
    ProductoOut,
    ProductoUpdate,
)


router = APIRouter(prefix="/productos", tags=["productos"])


@router.post(
    "",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
) -> Producto:
    nuevo_producto = Producto(**producto.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


@router.get("", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)) -> list[Producto]:
    consulta = select(Producto).where(Producto.activo.is_(True)).order_by(Producto.id)
    return list(db.scalars(consulta).all())


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
) -> Producto:
    return _obtener_producto_activo(producto_id, db)


@router.put("/{producto_id}", response_model=ProductoOut)
def reemplazar_producto(
    producto_id: int,
    producto_actualizado: ProductoCreate,
    db: Session = Depends(get_db),
) -> Producto:
    producto_existente = _obtener_producto_activo(producto_id, db)
    for campo, valor in producto_actualizado.model_dump().items():
        setattr(producto_existente, campo, valor)
    db.commit()
    db.refresh(producto_existente)
    return producto_existente


@router.patch("/{producto_id}", response_model=ProductoOut)
def actualizar_producto_parcial(
    producto_id: int,
    producto_actualizado: ProductoUpdate,
    db: Session = Depends(get_db),
) -> Producto:
    producto_existente = _obtener_producto_activo(producto_id, db)
    for campo, valor in producto_actualizado.model_dump(exclude_unset=True).items():
        setattr(producto_existente, campo, valor)
    db.commit()
    db.refresh(producto_existente)
    return producto_existente


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
) -> None:
    producto_existente = _obtener_producto_activo(producto_id, db)
    producto_existente.activo = False
    db.commit()


@router.post(
    "/{producto_id}/movimientos",
    response_model=MovimientoOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimiento(
    producto_id: int,
    movimiento: MovimientoCreate,
    db: Session = Depends(get_db),
) -> MovimientoInventario:
    try:
        condiciones = [
            Producto.id == producto_id,
            Producto.activo.is_(True),
        ]
        if movimiento.tipo == "salida":
            condiciones.append(Producto.stock >= movimiento.cantidad)
            nuevo_stock = Producto.stock - movimiento.cantidad
        else:
            nuevo_stock = Producto.stock + movimiento.cantidad

        resultado = db.execute(
            update(Producto).where(*condiciones).values(stock=nuevo_stock)
        )
        if resultado.rowcount == 0:
            if movimiento.tipo == "salida":
                producto_activo = db.scalar(
                    select(Producto.id).where(
                        Producto.id == producto_id,
                        Producto.activo.is_(True),
                    )
                )
                if producto_activo is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Stock insuficiente",
                    )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        nuevo_movimiento = MovimientoInventario(
            producto_id=producto_id,
            **movimiento.model_dump(),
        )
        db.add(nuevo_movimiento)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(nuevo_movimiento)
    return nuevo_movimiento


@router.get(
    "/{producto_id}/movimientos",
    response_model=list[MovimientoOut],
)
def listar_movimientos(
    producto_id: int,
    db: Session = Depends(get_db),
) -> list[MovimientoInventario]:
    _obtener_producto_activo(producto_id, db)
    consulta = (
        select(MovimientoInventario)
        .where(MovimientoInventario.producto_id == producto_id)
        .order_by(
            MovimientoInventario.fecha.desc(),
            MovimientoInventario.id.desc(),
        )
    )
    return list(db.scalars(consulta).all())


def _obtener_producto_activo(producto_id: int, db: Session) -> Producto:
    consulta = select(Producto).where(
        Producto.id == producto_id,
        Producto.activo.is_(True),
    )
    producto = db.scalar(consulta)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto
