from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from app.db import get_session

router = APIRouter()

class TagCreate(BaseModel):
    name: str
    category: str
    color_hex: str = "#6366f1"
    created_at: Optional[date] = None
    global_tag: bool = True

class TagUpdate(BaseModel):
    category: Optional[str] = None
    color_hex: Optional[str] = None
    global_tag: Optional[bool] = None

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.post("/", status_code=201)
async def create_tag(data: TagCreate):
    with get_session() as session:
        result = session.run(
            """
            CREATE (t:Tag {
                name: $name,
                category: $category,
                color_hex: $color_hex,
                created_at: date($created_at),
                global: $global_tag
            })
            RETURN elementId(t) AS id, t
            """,
            name=data.name,
            category=data.category,
            color_hex=data.color_hex,
            created_at=str(data.created_at) if data.created_at else str(date.today()),
            global_tag=data.global_tag,
        )
        record = result.single()
        return {"id": record["id"], **node_to_dict(record["t"])}

@router.get("/")
async def list_tags(
    category: Optional[str] = None,
    global_tag: Optional[bool] = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
):
    filters = []
    params: dict = {"skip": skip, "limit": limit}
    if category:
        filters.append("t.category = $category")
        params["category"] = category
    if global_tag is not None:
        filters.append("t.global = $global_tag")
        params["global_tag"] = global_tag
    where = "WHERE " + " AND ".join(filters) if filters else ""
    with get_session() as session:
        result = session.run(
            f"MATCH (t:Tag) {where} RETURN elementId(t) AS id, t SKIP $skip LIMIT $limit",
            **params
        )
        return [{"id": r["id"], **node_to_dict(r["t"])} for r in result]

@router.get("/{tag_id}")
async def get_tag(tag_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (t:Tag) WHERE elementId(t) = $id RETURN elementId(t) AS id, t",
            id=tag_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Tag not found")
        return {"id": record["id"], **node_to_dict(record["t"])}

@router.patch("/{tag_id}")
async def update_tag(tag_id: str, data: TagUpdate):
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clauses = ", ".join([f"t.{k} = ${k}" for k in updates])
    with get_session() as session:
        result = session.run(
            f"MATCH (t:Tag) WHERE elementId(t) = $id SET {set_clauses} RETURN elementId(t) AS id, t",
            id=tag_id, **updates
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Tag not found")
        return {"id": record["id"], **node_to_dict(record["t"])}

@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: str):
    with get_session() as session:
        result = session.run(
            "MATCH (t:Tag) WHERE elementId(t) = $id DETACH DELETE t RETURN count(t) AS deleted",
            id=tag_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Tag not found")
