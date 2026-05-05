import csv
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.db import get_session

router = APIRouter()

def parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]

def coerce(value: str):
    """Try int -> float -> bool -> str."""
    if value is None or value.strip() == "":
        return None
    v = value.strip()
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v

@router.post("/suppliers")
async def load_suppliers_csv(file: UploadFile = File(...)):
    """
    Upload a CSV with columns:
    name, country, active, rating, certifications (semicolon-separated), founded_at
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                certs = [c.strip() for c in row.get("certifications", "").split(";") if c.strip()]
                session.run("""
                    MERGE (s:Supplier {name: $name})
                    SET s.country = $country,
                        s.active = $active,
                        s.rating = $rating,
                        s.certifications = $certifications,
                        s.founded_at = date($founded_at),
                        s.created_at = datetime()
                """,
                    name=row["name"],
                    country=row.get("country", ""),
                    active=coerce(row.get("active", "true")),
                    rating=float(row.get("rating", 0) or 0),
                    certifications=certs,
                    founded_at=row.get("founded_at") or "2020-01-01",
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/products")
async def load_products_csv(file: UploadFile = File(...)):
    """
    Upload a CSV with columns:
    name, sku, price, weight, category, in_stock, description
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                session.run("""
                    MERGE (p:Product {sku: $sku})
                    SET p.name = $name,
                        p.price = $price,
                        p.weight = $weight,
                        p.category = $category,
                        p.in_stock = $in_stock,
                        p.description = $description,
                        p.created_at = datetime()
                """,
                    name=row["name"],
                    sku=row["sku"],
                    price=float(row.get("price", 0) or 0),
                    weight=float(row.get("weight", 0) or 0),
                    category=row.get("category", ""),
                    in_stock=coerce(row.get("in_stock", "true")),
                    description=row.get("description", ""),
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/warehouses")
async def load_warehouses_csv(file: UploadFile = File(...)):
    """
    Upload a CSV with columns:
    code, city, capacity, active, opened_at
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                session.run("""
                    MERGE (w:Warehouse {code: $code})
                    SET w.city = $city,
                        w.capacity = $capacity,
                        w.active = $active,
                        w.coordinates = [],
                        w.opened_at = date($opened_at)
                """,
                    code=row["code"],
                    city=row.get("city", ""),
                    capacity=int(row.get("capacity", 0) or 0),
                    active=coerce(row.get("active", "true")),
                    opened_at=row.get("opened_at") or "2020-01-01",
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/orders")
async def load_orders_csv(file: UploadFile = File(...)):
    """
    Upload a CSV with columns:
    order_id, status, total, placed_at, fulfilled, notes
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                session.run("""
                    MERGE (o:Order {order_id: $order_id})
                    SET o.status = $status,
                        o.total = $total,
                        o.placed_at = datetime($placed_at),
                        o.fulfilled = $fulfilled,
                        o.notes = $notes
                """,
                    order_id=row["order_id"],
                    status=row.get("status", "PENDING"),
                    total=float(row.get("total", 0) or 0),
                    placed_at=row.get("placed_at") or "2024-01-01T00:00:00",
                    fulfilled=coerce(row.get("fulfilled", "false")),
                    notes=row.get("notes", ""),
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/carriers")
async def load_carriers_csv(file: UploadFile = File(...)):
    """
    Upload a CSV with columns:
    name, modes (semicolon-separated), active, rating, regions (semicolon-separated), onboarded_at
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                modes = [m.strip() for m in row.get("modes", "").split(";") if m.strip()]
                regions = [r.strip() for r in row.get("regions", "").split(";") if r.strip()]
                session.run("""
                    MERGE (c:Carrier {name: $name})
                    SET c.modes = $modes,
                        c.active = $active,
                        c.rating = $rating,
                        c.regions = $regions,
                        c.onboarded_at = date($onboarded_at)
                """,
                    name=row["name"],
                    modes=modes,
                    active=coerce(row.get("active", "true")),
                    rating=float(row.get("rating", 0) or 0),
                    regions=regions,
                    onboarded_at=row.get("onboarded_at") or "2020-01-01",
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/relationships/supplies")
async def load_supplies_csv(file: UploadFile = File(...)):
    """
    CSV: supplier_name, product_sku, since, contract_price, exclusive, min_order_qty
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                session.run("""
                    MATCH (s:Supplier {name: $supplier_name})
                    MATCH (p:Product {sku: $product_sku})
                    MERGE (s)-[r:SUPPLIES]->(p)
                    SET r.since = date($since),
                        r.contract_price = $contract_price,
                        r.exclusive = $exclusive,
                        r.min_order_qty = $min_order_qty
                """,
                    supplier_name=row["supplier_name"],
                    product_sku=row["product_sku"],
                    since=row.get("since") or "2020-01-01",
                    contract_price=float(row.get("contract_price", 0) or 0),
                    exclusive=coerce(row.get("exclusive", "false")),
                    min_order_qty=int(row.get("min_order_qty", 1) or 1),
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}

@router.post("/relationships/stored_in")
async def load_stored_in_csv(file: UploadFile = File(...)):
    """
    CSV: product_sku, warehouse_code, quantity, reserved_qty, last_updated, bin_codes (semicolon-separated)
    """
    rows = parse_csv(await file.read())
    created = 0
    errors = []
    with get_session() as session:
        for i, row in enumerate(rows):
            try:
                bins = [b.strip() for b in row.get("bin_codes", "").split(";") if b.strip()]
                session.run("""
                    MATCH (p:Product {sku: $product_sku})
                    MATCH (w:Warehouse {code: $warehouse_code})
                    MERGE (p)-[r:STORED_IN]->(w)
                    SET r.quantity = $quantity,
                        r.reserved_qty = $reserved_qty,
                        r.last_updated = date($last_updated),
                        r.bin_codes = $bin_codes
                """,
                    product_sku=row["product_sku"],
                    warehouse_code=row["warehouse_code"],
                    quantity=int(row.get("quantity", 0) or 0),
                    reserved_qty=int(row.get("reserved_qty", 0) or 0),
                    last_updated=row.get("last_updated") or "2024-01-01",
                    bin_codes=bins,
                )
                created += 1
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})
    return {"created": created, "errors": errors}
