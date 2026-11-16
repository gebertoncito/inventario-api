from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


NombreProducto = Annotated[str, Field(min_length=1, max_length=120)]
PrecioProducto = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class ProductoBase(BaseModel):
    nombre: NombreProducto
    precio: PrecioProducto
    stock: Annotated[int, Field(ge=0)] = 0

    @field_validator("nombre")
    @classmethod
    def validar_nombre_no_vacio(cls, value: str) -> str:
        nombre = value.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")
        return nombre


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: NombreProducto | None = None
    precio: PrecioProducto | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre_no_vacio(cls, value: str | None) -> str | None:
        if value is None:
            return value
        nombre = value.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")
        return nombre

    @model_validator(mode="after")
    def validar_campos_no_nulos(self) -> "ProductoUpdate":
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError("El campo no puede ser nulo")
        return self


class ProductoReemplazo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: NombreProducto
    precio: PrecioProducto

    @field_validator("nombre")
    @classmethod
    def validar_nombre_no_vacio(cls, value: str) -> str:
        nombre = value.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")
        return nombre


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
    stock: int
    activo: bool


class MovimientoCreate(BaseModel):
    tipo: Literal["entrada", "salida"]
    cantidad: Annotated[int, Field(gt=0)]
    nota: Annotated[str | None, Field(max_length=200)] = None

    @field_validator("nota", mode="before")
    @classmethod
    def limpiar_nota(cls, value: str | None) -> str | None:
        if value is None:
            return None
        nota = value.strip()
        return nota or None


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    tipo: Literal["entrada", "salida"]
    cantidad: int
    fecha: datetime
    nota: str | None
