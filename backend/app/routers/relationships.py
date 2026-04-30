from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.db import get_session

router = APIRouter()

def rel_to_dict(rel):
    d = dict(rel)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

# ──────────────────────────────────────────────
# SUPPLIES  (Supplier)-[:SUPPLIES]->(Product)
# ──────────────────────────────────────────────
class SuppliesCreate(BaseModel):
    supplier_id: str
    product_id: str
    since: str
    contract_price: float
    exclusive: bool = False
    min_order_qty: int = 1

@router.post("/supplies", status_code=201)
async def create_supplies(data: SuppliesCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (s:Supplier) WHERE elementId(s) = $sid
            MATCH (p:Product) WHERE elementId(p) = $pid
            CREATE (s)-[r:SUPPLIES {
                since: date($since),
                contract_price: $contract_price,
                exclusive: $exclusive,
                min_order_qty: $min_order_qty
            }]->(p)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, sid=data.supplier_id, pid=data.product_id, since=data.since,
             contract_price=data.contract_price, exclusive=data.exclusive,
             min_order_qty=data.min_order_qty)
        r = result.single()
        if not r:
            raise HTTPException(404, "Supplier or Product not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# STORED_IN  (Product)-[:STORED_IN]->(Warehouse)
# ──────────────────────────────────────────────
class StoredInCreate(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: int
    last_updated: str
    bin_codes: List[str] = []
    reserved_qty: int = 0

@router.post("/stored_in", status_code=201)
async def create_stored_in(data: StoredInCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (p:Product) WHERE elementId(p) = $pid
            MATCH (w:Warehouse) WHERE elementId(w) = $wid
            CREATE (p)-[r:STORED_IN {
                quantity: $quantity,
                last_updated: date($last_updated),
                bin_codes: $bin_codes,
                reserved_qty: $reserved_qty
            }]->(w)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, pid=data.product_id, wid=data.warehouse_id, quantity=data.quantity,
             last_updated=data.last_updated, bin_codes=data.bin_codes,
             reserved_qty=data.reserved_qty)
        r = result.single()
        if not r:
            raise HTTPException(404, "Product or Warehouse not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# SHIPS_VIA  (Warehouse)-[:SHIPS_VIA]->(Carrier)
# ──────────────────────────────────────────────
class ShipsViaCreate(BaseModel):
    warehouse_id: str
    carrier_id: str
    contracted_since: str
    priority: int = 1
    max_weight_kg: float = 1000.0

@router.post("/ships_via", status_code=201)
async def create_ships_via(data: ShipsViaCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (w:Warehouse) WHERE elementId(w) = $wid
            MATCH (c:Carrier) WHERE elementId(c) = $cid
            CREATE (w)-[r:SHIPS_VIA {
                contracted_since: date($contracted_since),
                priority: $priority,
                max_weight_kg: $max_weight_kg
            }]->(c)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, wid=data.warehouse_id, cid=data.carrier_id,
             contracted_since=data.contracted_since, priority=data.priority,
             max_weight_kg=data.max_weight_kg)
        r = result.single()
        if not r:
            raise HTTPException(404, "Warehouse or Carrier not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# TRANSFERS_TO  (Warehouse)-[:TRANSFERS_TO]->(Warehouse)
# ──────────────────────────────────────────────
class TransfersToCreate(BaseModel):
    from_warehouse_id: str
    to_warehouse_id: str
    transfer_id: str
    scheduled_at: str
    completed: bool = False

@router.post("/transfers_to", status_code=201)
async def create_transfers_to(data: TransfersToCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (w1:Warehouse) WHERE elementId(w1) = $w1id
            MATCH (w2:Warehouse) WHERE elementId(w2) = $w2id
            CREATE (w1)-[r:TRANSFERS_TO {
                transfer_id: $transfer_id,
                scheduled_at: datetime($scheduled_at),
                completed: $completed
            }]->(w2)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, w1id=data.from_warehouse_id, w2id=data.to_warehouse_id,
             transfer_id=data.transfer_id, scheduled_at=data.scheduled_at,
             completed=data.completed)
        r = result.single()
        if not r:
            raise HTTPException(404, "One or both warehouses not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# CONTAINS  (Order)-[:CONTAINS]->(Product)
# ──────────────────────────────────────────────
class ContainsCreate(BaseModel):
    order_id: str
    product_id: str
    quantity: int
    unit_price: float
    discount: float = 0.0
    note: Optional[str] = ""

@router.post("/contains", status_code=201)
async def create_contains(data: ContainsCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order) WHERE elementId(o) = $oid
            MATCH (p:Product) WHERE elementId(p) = $pid
            CREATE (o)-[r:CONTAINS {
                quantity: $quantity,
                unit_price: $unit_price,
                discount: $discount,
                note: $note
            }]->(p)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, oid=data.order_id, pid=data.product_id, quantity=data.quantity,
             unit_price=data.unit_price, discount=data.discount, note=data.note or "")
        r = result.single()
        if not r:
            raise HTTPException(404, "Order or Product not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# SHIPPED_BY  (Order)-[:SHIPPED_BY]->(Carrier)
# ──────────────────────────────────────────────
class ShippedByCreate(BaseModel):
    order_id: str
    carrier_id: str
    tracking_id: str
    cost: float
    dispatched_at: str
    estimated_delivery: str

@router.post("/shipped_by", status_code=201)
async def create_shipped_by(data: ShippedByCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order) WHERE elementId(o) = $oid
            MATCH (c:Carrier) WHERE elementId(c) = $cid
            CREATE (o)-[r:SHIPPED_BY {
                tracking_id: $tracking_id,
                cost: $cost,
                dispatched_at: datetime($dispatched_at),
                estimated_delivery: date($estimated_delivery)
            }]->(c)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, oid=data.order_id, cid=data.carrier_id, tracking_id=data.tracking_id,
             cost=data.cost, dispatched_at=data.dispatched_at,
             estimated_delivery=data.estimated_delivery)
        r = result.single()
        if not r:
            raise HTTPException(404, "Order or Carrier not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# RETURNS_TO  (Order)-[:RETURNS_TO]->(Supplier)
# ──────────────────────────────────────────────
class ReturnsToCreate(BaseModel):
    order_id: str
    supplier_id: str
    reason: str
    returned_at: str
    refund_amount: float

@router.post("/returns_to", status_code=201)
async def create_returns_to(data: ReturnsToCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order) WHERE elementId(o) = $oid
            MATCH (s:Supplier) WHERE elementId(s) = $sid
            CREATE (o)-[r:RETURNS_TO {
                reason: $reason,
                returned_at: datetime($returned_at),
                refund_amount: $refund_amount
            }]->(s)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, oid=data.order_id, sid=data.supplier_id, reason=data.reason,
             returned_at=data.returned_at, refund_amount=data.refund_amount)
        r = result.single()
        if not r:
            raise HTTPException(404, "Order or Supplier not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# PARTNERS_WITH  (Carrier)-[:PARTNERS_WITH]->(Supplier)
# ──────────────────────────────────────────────
class PartnersWithCreate(BaseModel):
    carrier_id: str
    supplier_id: str
    since: str
    discount_rate: float
    preferred: bool = False

@router.post("/partners_with", status_code=201)
async def create_partners_with(data: PartnersWithCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (c:Carrier) WHERE elementId(c) = $cid
            MATCH (s:Supplier) WHERE elementId(s) = $sid
            CREATE (c)-[r:PARTNERS_WITH {
                since: date($since),
                discount_rate: $discount_rate,
                preferred: $preferred
            }]->(s)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, cid=data.carrier_id, sid=data.supplier_id, since=data.since,
             discount_rate=data.discount_rate, preferred=data.preferred)
        r = result.single()
        if not r:
            raise HTTPException(404, "Carrier or Supplier not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# TAGGED_AS  (Tag)-[:TAGGED_AS]->(Product)
# ──────────────────────────────────────────────
class TaggedAsCreate(BaseModel):
    tag_id: str
    product_id: str
    tagged_at: str
    auto_assigned: bool = False
    weight: float = 1.0

@router.post("/tagged_as", status_code=201)
async def create_tagged_as(data: TaggedAsCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (t:Tag) WHERE elementId(t) = $tid
            MATCH (p:Product) WHERE elementId(p) = $pid
            CREATE (t)-[r:TAGGED_AS {
                tagged_at: datetime($tagged_at),
                auto_assigned: $auto_assigned,
                weight: $weight
            }]->(p)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, tid=data.tag_id, pid=data.product_id, tagged_at=data.tagged_at,
             auto_assigned=data.auto_assigned, weight=data.weight)
        r = result.single()
        if not r:
            raise HTTPException(404, "Tag or Product not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# FULFILLS  (Warehouse)-[:FULFILLS]->(Order)
# ──────────────────────────────────────────────
class FulfillsCreate(BaseModel):
    warehouse_id: str
    order_id: str
    fulfilled_at: str
    items_count: int
    partial: bool = False

@router.post("/fulfills", status_code=201)
async def create_fulfills(data: FulfillsCreate):
    with get_session() as session:
        result = session.run("""
            MATCH (w:Warehouse) WHERE elementId(w) = $wid
            MATCH (o:Order) WHERE elementId(o) = $oid
            CREATE (w)-[r:FULFILLS {
                fulfilled_at: datetime($fulfilled_at),
                items_count: $items_count,
                partial: $partial
            }]->(o)
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
        """, wid=data.warehouse_id, oid=data.order_id,
             fulfilled_at=data.fulfilled_at, items_count=data.items_count,
             partial=data.partial)
        r = result.single()
        if not r:
            raise HTTPException(404, "Warehouse or Order not found")
        return {"id": r["id"], "type": r["type"], **rel_to_dict(r["props"])}

# ──────────────────────────────────────────────
# Generic relationship property management
# ──────────────────────────────────────────────
class RelPropUpdate(BaseModel):
    from_id: str
    to_id: str
    rel_type: str
    props: dict

@router.patch("/properties")
async def update_relationship_properties(data: RelPropUpdate):
    set_clauses = ", ".join([f"r.{k} = ${k}" for k in data.props])
    with get_session() as session:
        result = session.run(
            f"""
            MATCH (a)-[r:{data.rel_type}]->(b)
            WHERE elementId(a) = $from_id AND elementId(b) = $to_id
            SET {set_clauses}
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
            """,
            from_id=data.from_id, to_id=data.to_id, **data.props
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Relationship not found")
        return {"id": record["id"], "type": record["type"], **rel_to_dict(record["props"])}

class RelPropDelete(BaseModel):
    from_id: str
    to_id: str
    rel_type: str
    keys: List[str]

@router.delete("/properties")
async def delete_relationship_properties(data: RelPropDelete):
    remove_clauses = ", ".join([f"r.{k}" for k in data.keys])
    with get_session() as session:
        result = session.run(
            f"""
            MATCH (a)-[r:{data.rel_type}]->(b)
            WHERE elementId(a) = $from_id AND elementId(b) = $to_id
            REMOVE {remove_clauses}
            RETURN elementId(r) AS id, type(r) AS type, properties(r) AS props
            """,
            from_id=data.from_id, to_id=data.to_id
        )
        record = result.single()
        if not record:
            raise HTTPException(404, "Relationship not found")
        return {"id": record["id"], "type": record["type"], **rel_to_dict(record["props"])}

class RelDelete(BaseModel):
    from_id: str
    to_id: str
    rel_type: str

@router.delete("/single", status_code=204)
async def delete_single_relationship(data: RelDelete):
    with get_session() as session:
        result = session.run(
            f"""
            MATCH (a)-[r:{data.rel_type}]->(b)
            WHERE elementId(a) = $from_id AND elementId(b) = $to_id
            DELETE r RETURN count(r) AS deleted
            """,
            from_id=data.from_id, to_id=data.to_id
        )
        if result.single()["deleted"] == 0:
            raise HTTPException(404, "Relationship not found")

class MultiRelDelete(BaseModel):
    pairs: List[dict]  # [{from_id, to_id, rel_type}]

@router.delete("/multiple", status_code=204)
async def delete_multiple_relationships(data: MultiRelDelete):
    with get_session() as session:
        for pair in data.pairs:
            session.run(
                f"""
                MATCH (a)-[r:{pair['rel_type']}]->(b)
                WHERE elementId(a) = $from_id AND elementId(b) = $to_id
                DELETE r
                """,
                from_id=pair["from_id"], to_id=pair["to_id"]
            )
