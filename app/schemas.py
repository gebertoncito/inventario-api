from decimal import Decimal
from typing import Annotated

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
    nombre: NombreProducto | None = None
    precio: PrecioProducto | None = None
    stock: Annotated[int, Field(ge=0)] | None = None

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


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
    stock: int
    activo: bool
