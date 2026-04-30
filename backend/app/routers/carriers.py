from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from app.db import get_session

router = APIRouter()

class CarrierCreate(BaseModel):
    name: str
    modes: List[str] = []  # AIR, SEA, GROUND
    active: bool = True
    rating: float = 0.0
    regions: List[str] = []
    onboarded_at: Optional[date] = None

class CarrierUpdate(BaseModel):
    name: Optional[str] = None
    modes: Optional[List[str]] = None
    active: Optional[bool] = None
    rating: Optional[float] = None
    regions: Optional[List[str]] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.post("/", status_code=201)
async def create_carrier(data: CarrierCreate):
    with get_session() as session:
        result = session.run(
            """
            CREATE (c:Carrier {
                name: $name,
                modes: $modes,
                active: $active,
                rating: $rating,
                regions: $regions,
                onboarded_at: date($onboarded_at)
            })
            RETURN elementId(c) AS id, c
            """,
            name=data.name,
            modes=data.modes,
            active=data.active,
            rating=data.rating,
            regions=data.regions,
            onboarded_at=str(data.onboarded_at) if data.onboarded_at else str(date.today()),
        )
        record = result.single()
        return {"id": record["id"], **node_to_dict(record["c"])}

@router.get("/")
async def list_carriers(
    active: Optional[bool] = None,
    mode: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if active is not None:
        filters.append("c.active = $active")
        params["active"] = active
    if mode:
        filters.append("$mode IN c.modes")
        params["mode"] = mode
    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (c:Carrier) {where} RETURN elementId(c) AS id, c SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["c"])} for r in result]

@router.get("/{carrier_id}")
async def get_carrier(carrier_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (c:Carrier) WHERE elementId(c) = $id RETURN elementId(c) AS id, c",
            id=carrier_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Carrier not found")
        return {"id": record["id"], **node_to_dict(record["c"])}

@router.patch("/{carrier_id}")
async def update_carrier(carrier_id: str, data: CarrierUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clauses = ", ".join([f"c.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (c:Carrier) WHERE elementId(c) = $id SET {set_clauses} RETURN elementId(c) AS id, c",
            id=carrier_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Carrier not found")
        return {"id": record["id"], **node_to_dict(record["c"])}

@router.delete("/{carrier_id}", status_code=204)
async def delete_carrier(carrier_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (c:Carrier) WHERE elementId(c) = $id DETACH DELETE c RETURN count(c) AS deleted",
            id=carrier_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Carrier not found")

@router.delete("/", status_code=204)
async def delete_multiple_carriers(ids: List[str]):
    with get_session() as session:
        session.run("MATCH (c:Carrier) WHERE elementId(c) IN $ids DETACH DELETE c", ids=ids)
