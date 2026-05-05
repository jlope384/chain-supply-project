from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from app.db import get_session

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    weight: float = 0.0
    category: str
    in_stock: bool = True
    description: Optional[str] = ""

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    weight: Optional[float] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None
    description: Optional[str] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.post("/", status_code=201)
async def create_product(data: ProductCreate):
    with get_session() as session:
        result = session.run(
            """
            CREATE (p:Product {
                name: $name,
                sku: $sku,
                price: $price,
                weight: $weight,
                category: $category,
                in_stock: $in_stock,
                description: $description,
                created_at: datetime()
            })
            RETURN elementId(p) AS id, p
            """,
            name=data.name,
            sku=data.sku,
            price=data.price,
            weight=data.weight,
            category=data.category,
            in_stock=data.in_stock,
            description=data.description or "",
        )
        record = result.single()
        if not record:
            raise HTTPException(500, "Failed to create product")
        return {"id": record["id"], **node_to_dict(record["p"])}

@router.get("/")
async def list_products(
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if category:
        filters.append("toLower(p.category) CONTAINS toLower($category)")
        params["category"] = category
    if in_stock is not None:
        filters.append("p.in_stock = $in_stock")
        params["in_stock"] = in_stock
    if min_price is not None:
        filters.append("p.price >= $min_price")
        params["min_price"] = min_price
    if max_price is not None:
        filters.append("p.price <= $max_price")
        params["max_price"] = max_price

    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (p:Product) {where} RETURN elementId(p) AS id, p SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["p"])} for r in result]

@router.get("/stats")
async def product_stats():
    with get_session() as session:
        result = session.run("""
            MATCH (p:Product)
            RETURN
                count(p) AS total,
                avg(p.price) AS avg_price,
                min(p.price) AS min_price,
                max(p.price) AS max_price,
                count(CASE WHEN p.in_stock THEN 1 END) AS in_stock_count,
                collect(DISTINCT p.category) AS categories
        """)
        r = result.single()
        return {
            "total": r["total"],
            "avg_price": round(r["avg_price"] or 0, 2),
            "min_price": r["min_price"],
            "max_price": r["max_price"],
            "in_stock_count": r["in_stock_count"],
            "categories": r["categories"],
        }

@router.get("/{product_id}")
async def get_product(product_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (p:Product) WHERE elementId(p) = $id RETURN elementId(p) AS id, p",
            id=product_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Product not found")
        return {"id": record["id"], **node_to_dict(record["p"])}

@router.patch("/{product_id}")
async def update_product(product_id: str, data: ProductUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clauses = ", ".join([f"p.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (p:Product) WHERE elementId(p) = $id SET {set_clauses} RETURN elementId(p) AS id, p",
            id=product_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Product not found")
        return {"id": record["id"], **node_to_dict(record["p"])}

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (p:Product) WHERE elementId(p) = $id DETACH DELETE p RETURN count(p) AS deleted",
            id=product_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Product not found")

@router.delete("/", status_code=204)
async def delete_multiple_products(ids: List[str]):
    with get_session() as session:
        session.run(
            "MATCH (p:Product) WHERE elementId(p) IN $ids DETACH DELETE p",
            ids=ids
        )

@router.post("/{product_id}/properties")
async def add_properties(product_id: str, props: dict):
    set_clauses = ", ".join([f"p.{k} = ${k}" for k in props])
    with get_session() as session:
        result = session.run(
            f"MATCH (p:Product) WHERE elementId(p) = $id SET {set_clauses} RETURN elementId(p) AS id, p",
            id=product_id, **props
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Not found")
        return {"id": record["id"], **node_to_dict(record["p"])}

@router.delete("/{product_id}/properties")
async def remove_properties(product_id: str, keys: List[str]):
    remove_clauses = ", ".join([f"p.{k}" for k in keys])
    with get_session() as session:
        result = session.run(
            f"MATCH (p:Product) WHERE elementId(p) = $id REMOVE {remove_clauses} RETURN elementId(p) AS id, p",
            id=product_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Not found")
        return {"id": record["id"], **node_to_dict(record["p"])}
