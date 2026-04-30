from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from app.db import get_session

router = APIRouter()

class SupplierCreate(BaseModel):
    name: str
    country: str
    active: bool = True
    rating: float = 0.0
    certifications: List[str] = []
    founded_at: Optional[date] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    active: Optional[bool] = None
    rating: Optional[float] = None
    certifications: Optional[List[str]] = None
    founded_at: Optional[date] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.post("/", status_code=201)
async def create_supplier(data: SupplierCreate):
    with get_session() as session:
        result = session.run(
            """
            CREATE (s:Supplier {
                name: $name,
                country: $country,
                active: $active,
                rating: $rating,
                certifications: $certifications,
                founded_at: date($founded_at),
                created_at: datetime()
            })
            RETURN elementId(s) AS id, s
            """,
            name=data.name,
            country=data.country,
            active=data.active,
            rating=data.rating,
            certifications=data.certifications,
            founded_at=str(data.founded_at) if data.founded_at else str(date.today()),
        )
        record = result.single()
        if not record:
            raise HTTPException(500, "Failed to create supplier")
        return {"id": record["id"], **node_to_dict(record["s"])}

@router.get("/")
async def list_suppliers(
    country: Optional[str] = None,
    active: Optional[bool] = None,
    min_rating: Optional[float] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if country:
        filters.append("s.country = $country")
        params["country"] = country
    if active is not None:
        filters.append("s.active = $active")
        params["active"] = active
    if min_rating is not None:
        filters.append("s.rating >= $min_rating")
        params["min_rating"] = min_rating

    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (s:Supplier) {where} RETURN elementId(s) AS id, s SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["s"])} for r in result]

@router.get("/stats")
async def supplier_stats():
    with get_session() as session:
        result = session.run("""
            MATCH (s:Supplier)
            RETURN 
                count(s) AS total,
                avg(s.rating) AS avg_rating,
                count(CASE WHEN s.active THEN 1 END) AS active_count,
                collect(DISTINCT s.country) AS countries
        """)
        r = result.single()
        return {
            "total": r["total"],
            "avg_rating": round(r["avg_rating"] or 0, 2),
            "active_count": r["active_count"],
            "countries": r["countries"],
        }

@router.get("/{supplier_id}")
async def get_supplier(supplier_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (s:Supplier) WHERE elementId(s) = $id RETURN elementId(s) AS id, s",
            id=supplier_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Supplier not found")
        return {"id": record["id"], **node_to_dict(record["s"])}

@router.patch("/{supplier_id}")
async def update_supplier(supplier_id: str, data: SupplierUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clauses = ", ".join([f"s.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (s:Supplier) WHERE elementId(s) = $id SET {set_clauses} RETURN elementId(s) AS id, s",
            id=supplier_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Supplier not found")
        return {"id": record["id"], **node_to_dict(record["s"])}

@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(supplier_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (s:Supplier) WHERE elementId(s) = $id DETACH DELETE s RETURN count(s) AS deleted",
            id=supplier_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Supplier not found")

@router.delete("/", status_code=204)
async def delete_multiple_suppliers(ids: List[str]):
    with get_session() as session:
        session.run(
            "MATCH (s:Supplier) WHERE elementId(s) IN $ids DETACH DELETE s",
            ids=ids
        )

@router.post("/{supplier_id}/properties")
async def add_properties(supplier_id: str, props: dict):
    set_clauses = ", ".join([f"s.{k} = ${k}" for k in props])
    with get_session() as session:
        result = session.run(
            f"MATCH (s:Supplier) WHERE elementId(s) = $id SET {set_clauses} RETURN elementId(s) AS id, s",
            id=supplier_id, **props
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Not found")
        return {"id": record["id"], **node_to_dict(record["s"])}

@router.delete("/{supplier_id}/properties")
async def remove_properties(supplier_id: str, keys: List[str]):
    remove_clauses = ", ".join([f"s.{k}" for k in keys])
    with get_session() as session:
        result = session.run(
            f"MATCH (s:Supplier) WHERE elementId(s) = $id REMOVE {remove_clauses} RETURN elementId(s) AS id, s",
            id=supplier_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Not found")
        return {"id": record["id"], **node_to_dict(record["s"])}
