from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db import get_driver, close_driver
from app.routers import suppliers, products, warehouses, orders, carriers, tags, relationships, graph, csv_loader

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()
    yield
    close_driver()

app = FastAPI(
    title="Supply Chain Neo4j API",
    description="Backend for supply chain graph management on Neo4j",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(carriers.router, prefix="/carriers", tags=["Carriers"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
app.include_router(graph.router, prefix="/graph", tags=["Graph"])
app.include_router(csv_loader.router, prefix="/csv", tags=["CSV"])

@app.get("/health")
async def health():
    return {"status": "ok"}
