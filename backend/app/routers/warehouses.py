from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from app.db import get_session

router = APIRouter()

class WarehouseCreate(BaseModel):
    code: str
    city: str
    capacity: int
    active: bool = True
    coordinates: List[float] = []  # [lat, lng]
    opened_at: Optional[date] = None

class WarehouseUpdate(BaseModel):
    city: Optional[str] = None
    capacity: Optional[int] = None
    active: Optional[bool] = None
    coordinates: Optional[List[float]] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.post("/", status_code=201)
async def create_warehouse(data: WarehouseCreate):
    with get_session() as session:
        result = session.run(
            """
            CREATE (w:Warehouse {
                code: $code,
                city: $city,
                capacity: $capacity,
                active: $active,
                coordinates: $coordinates,
                opened_at: date($opened_at)
            })
            RETURN elementId(w) AS id, w
            """,
            code=data.code,
            city=data.city,
            capacity=data.capacity,
            active=data.active,
            coordinates=data.coordinates,
            opened_at=str(data.opened_at) if data.opened_at else str(date.today()),
        )
        record = result.single()
        if not record:
            raise HTTPException(500, "Failed to create warehouse")
        return {"id": record["id"], **node_to_dict(record["w"])}

@router.get("/")
async def list_warehouses(
    city: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if city:
        filters.append("toLower(w.city) CONTAINS toLower($city)")
        params["city"] = city
    if active is not None:
        filters.append("w.active = $active")
        params["active"] = active
    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (w:Warehouse) {where} RETURN elementId(w) AS id, w SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["w"])} for r in result]

@router.get("/{warehouse_id}")
async def get_warehouse(warehouse_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (w:Warehouse) WHERE elementId(w) = $id RETURN elementId(w) AS id, w",
            id=warehouse_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Warehouse not found")
        return {"id": record["id"], **node_to_dict(record["w"])}

@router.patch("/{warehouse_id}")
async def update_warehouse(warehouse_id: str, data: WarehouseUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clauses = ", ".join([f"w.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (w:Warehouse) WHERE elementId(w) = $id SET {set_clauses} RETURN elementId(w) AS id, w",
            id=warehouse_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Warehouse not found")
        return {"id": record["id"], **node_to_dict(record["w"])}

@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(warehouse_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (w:Warehouse) WHERE elementId(w) = $id DETACH DELETE w RETURN count(w) AS deleted",
            id=warehouse_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Warehouse not found")

@router.delete("/", status_code=204)
async def delete_multiple_warehouses(ids: List[str]):
    with get_session() as session:
        session.run("MATCH (w:Warehouse) WHERE elementId(w) IN $ids DETACH DELETE w", ids=ids)

@router.get("/{warehouse_id}/inventory")
async def get_inventory(warehouse_id: str):
    with get_session() as session:
        result = session.run(
            """
            MATCH (p:Product)-[r:STORED_IN]->(w:Warehouse)
            WHERE elementId(w) = $id
            RETURN elementId(p) AS product_id, p.name AS name, p.sku AS sku,
                   r.quantity AS quantity, r.reserved_qty AS reserved_qty,
                   r.last_updated AS last_updated
            """,
            id=warehouse_id
        )
        return [dict(r) for r in result]
