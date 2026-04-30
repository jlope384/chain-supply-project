from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.db import get_session

router = APIRouter()

class OrderCreate(BaseModel):
    order_id: str
    status: str = "PENDING"
    total: float
    placed_at: Optional[str] = None
    fulfilled: bool = False
    notes: Optional[str] = ""

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total: Optional[float] = None
    fulfilled: Optional[bool] = None
    notes: Optional[str] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

VALID_STATUSES = {"PENDING", "SHIPPED", "DELIVERED", "RETURNED"}

@router.post("/", status_code=201)
async def create_order(data: OrderCreate):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Must be one of {VALID_STATUSES}")
    with get_session() as session:
        result = session.run(
            """
            CREATE (o:Order {
                order_id: $order_id,
                status: $status,
                total: $total,
                placed_at: datetime($placed_at),
                fulfilled: $fulfilled,
                notes: $notes
            })
            RETURN elementId(o) AS id, o
            """,
            order_id=data.order_id,
            status=data.status,
            total=data.total,
            placed_at=data.placed_at or datetime.utcnow().isoformat(),
            fulfilled=data.fulfilled,
            notes=data.notes or "",
        )
        record = result.single()
        if not record:
            raise HTTPException(500, "Failed to create order")
        return {"id": record["id"], **node_to_dict(record["o"])}

@router.get("/")
async def list_orders(
    status: Optional[str] = None,
    fulfilled: Optional[bool] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if status:
        filters.append("o.status = $status")
        params["status"] = status
    if fulfilled is not None:
        filters.append("o.fulfilled = $fulfilled")
        params["fulfilled"] = fulfilled
    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (o:Order) {where} RETURN elementId(o) AS id, o SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["o"])} for r in result]

@router.get("/stats")
async def order_stats():
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order)
            RETURN 
                count(o) AS total,
                sum(o.total) AS revenue,
                avg(o.total) AS avg_order,
                count(CASE WHEN o.status = 'PENDING' THEN 1 END) AS pending,
                count(CASE WHEN o.status = 'SHIPPED' THEN 1 END) AS shipped,
                count(CASE WHEN o.status = 'DELIVERED' THEN 1 END) AS delivered,
                count(CASE WHEN o.status = 'RETURNED' THEN 1 END) AS returned
        """)
        r = result.single()
        return dict(r)

@router.get("/{order_id}")
async def get_order(order_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (o:Order) WHERE elementId(o) = $id RETURN elementId(o) AS id, o",
            id=order_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Order not found")
        return {"id": record["id"], **node_to_dict(record["o"])}

@router.patch("/{order_id}")
async def update_order(order_id: str, data: OrderUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status")
    set_clauses = ", ".join([f"o.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (o:Order) WHERE elementId(o) = $id SET {set_clauses} RETURN elementId(o) AS id, o",
            id=order_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Order not found")
        return {"id": record["id"], **node_to_dict(record["o"])}

@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (o:Order) WHERE elementId(o) = $id DETACH DELETE o RETURN count(o) AS deleted",
            id=order_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Order not found")

@router.delete("/", status_code=204)
async def delete_multiple_orders(ids: List[str]):
    with get_session() as session:
        session.run("MATCH (o:Order) WHERE elementId(o) IN $ids DETACH DELETE o", ids=ids)
