from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Producto
from app.schemas import ProductoCreate, ProductoOut


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
