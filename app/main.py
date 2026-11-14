from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.database import Base, engine
from app.models import Producto  # noqa: F401
from app.routes import router as productos_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Inventario API",
    description="API REST para gestionar el inventario de una pulpería o tienda.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(productos_router)


@app.get("/health", tags=["salud"])
def health() -> dict[str, str]:
    return {"status": "ok"}
