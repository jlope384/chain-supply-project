"""
Seed script — genera exactamente 7500 nodos + todas las relaciones.
Ejecutar desde backend/:
    python seed.py           # agrega a datos existentes
    python seed.py --clear   # limpia la DB primero

Distribución de nodos:
    Supplier   750
    Product   2500
    Warehouse  250
    Order     3700
    Carrier    150
    Tag        150
    ─────────────
    TOTAL     7500
"""

import random
import sys
import uuid
from datetime import date, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

from neo4j import GraphDatabase

URI      = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
USER     = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "")
DATABASE = os.getenv("NEO4J_DATABASE") or None

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_session():
    return driver.session(database=DATABASE)

# ── Helpers ───────────────────────────────────────────────────────────────────

def rand_date(y0=2015, y1=2024) -> str:
    a = date(y0, 1, 1)
    b = date(y1, 12, 31)
    return str(a + timedelta(days=random.randint(0, (b - a).days)))

def rand_dt(y0=2022, y1=2025) -> str:
    d = rand_date(y0, y1)
    return f"{d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00"

def pick(lst):
    return random.choice(lst)

def picks(lst, k):
    return random.sample(lst, min(k, len(lst)))

def progress(label, done, total):
    bar = "█" * int(done / total * 20) + "░" * (20 - int(done / total * 20))
    print(f"\r  {label:<28s} [{bar}] {done:>5}/{total}", end="", flush=True)
    if done >= total:
        print()

def batch_run(sess, query, rows, batch=500, label=""):
    total = len(rows)
    for i in range(0, total, batch):
        sess.run(query, rows=rows[i:i+batch])
        progress(label, min(i + batch, total), total)

# ── Static pools ──────────────────────────────────────────────────────────────

COUNTRIES = [
    "Guatemala","México","Colombia","Brasil","Argentina","Chile","Perú","Ecuador",
    "Venezuela","Panamá","Costa Rica","El Salvador","Honduras","Nicaragua","Bolivia",
    "Paraguay","Uruguay","Cuba","USA","Canada","Germany","France","Spain","China",
    "Japan","South Korea","India","UK","Italy","Netherlands","Sweden","Poland",
    "Turkey","Australia","South Africa","Nigeria","Egypt","Saudi Arabia","UAE","Mexico",
]

PREFIXES = [
    "Global","Trans","Ultra","Prime","Alpha","Omega","Apex","Central","Pacific",
    "Atlantic","Nordic","Andean","Iberia","Euro","Asia","Latam","Caribe","Sierra",
    "Delta","United","Acme","Nova","Frontier","Summit","Horizon","Vanguard","Stellar",
    "Nexus","Vertex","Pinnacle","Crest","Allied","Imperial","Sovereign","Premier",
    "Elite","Quantum","Fusion","Dynamic","Synergy","Catalyst","Integral","Meridian",
]
SUFFIXES = [
    "Supply Co.","Industries","Corp.","Ltd.","S.A.","Group","Trading","Logistics",
    "Partners","Solutions","Ventures","Enterprises","Manufacturing","International",
    "Holdings","Systems","Networks","Services","Technologies","Distribution",
]
CERTS = ["ISO9001","ISO14001","CE","FDA","GMP","HACCP","OSHA","SA8000","B-Corp",
         "ISO45001","ISO27001","FSSC22000","BRC","SQF","WRAP"]

CATEGORIES = [
    "Electronics","Clothing","Food & Beverage","Pharmaceuticals","Machinery",
    "Chemicals","Furniture","Automotive Parts","Sporting Goods","Toys","Tools",
    "Cosmetics","Books","Agriculture","Construction Materials","Medical Devices",
    "Packaging","Textiles","Plastics","Metals","Paper","Rubber","Glass","Ceramics",
    "Jewelry","Footwear","Office Supplies","Cleaning Products","Pet Supplies",
    "Musical Instruments",
]
ADJ = [
    "Pro","Ultra","Smart","Eco","Premium","Standard","Advanced","Compact",
    "Heavy-Duty","Portable","Industrial","Digital","Precision","Modular","Flex",
    "Rapid","Micro","Maxi","Turbo","Nano","Mega","Multi","Dual","Tri","Quad",
]
NOUNS = [
    "Sensor","Module","Controller","Kit","Pack","Unit","Device","System","Component",
    "Assembly","Panel","Cable","Adapter","Container","Pump","Valve","Filter","Motor",
    "Gear","Bracket","Connector","Switch","Relay","Processor","Display","Battery",
    "Charger","Frame","Housing","Seal","Bolt","Nut","Washer","Bearing","Spring",
    "Gasket","Nozzle","Fitting","Coupling","Shaft","Pulley","Chain","Belt","Screw",
    "Hinge","Latch","Clamp","Bracket","Rod","Pipe","Tube","Wire","Coil","Drum",
]

CITIES = [
    "Guatemala City","México DF","Bogotá","São Paulo","Buenos Aires","Santiago",
    "Lima","Quito","Caracas","Panama City","San José","Tegucigalpa","Managua",
    "San Salvador","La Paz","Asunción","Montevideo","Havana","New York","Los Angeles",
    "Chicago","Miami","Houston","Toronto","London","Paris","Berlin","Madrid",
    "Barcelona","Beijing","Shanghai","Tokyo","Seoul","Mumbai","Amsterdam","Stockholm",
    "Warsaw","Istanbul","Sydney","Johannesburg","Cairo","Riyadh","Dubai","Singapore",
    "Guadalajara","Monterrey","Medellín","Cali","Río de Janeiro","Brasilia","Córdoba",
    "Rosario","Valparaíso","Arequipa","Guayaquil","Cuenca","Santa Cruz","Cochabamba",
    "Maracaibo","Valencia","Barranquilla","Cartagena","Cúcuta","Bucaramanga","Pereira",
    "Belém","Fortaleza","Recife","Salvador","Curitiba","Porto Alegre","Belo Horizonte",
]

CARRIER_NAMES = [
    "SwiftShip","AeroFreight","OceanLink","RoadRunner Express","SkyMove",
    "TerraLogix","PolarRoute","SunFreight","BlueWave","FastTrack","GlobalCarrier",
    "AndeanAir","PacificSea","NordCargo","EuroFreight","CaribbeanLink","AmazonEx",
    "CentralMover","AtlanticShip","MetroLog","ZenithCargo","IronRoute","CloudFreight",
    "TradeWing","CoastLine","ExpressLink","RapidMove","DirectShip","PriorityFreight",
    "ApexLogistics","NexusCarrier","OmegaShip","DeltaRoute","StellarFreight",
    "VertexMove","PinnacleLog","CrestCargo","AlphaShip","OrbitalEx","VanguardLog",
    "CatalystFreight","MeridianCargo","FusionShip","DynamicRoute","IntegralEx",
    "QuantumLog","SynergyFreight","EliteShip","PremierCargo","SovereignRoute",
    "ImperialFreight","AlliedMove","MidwayLog","CrossroadEx","JunctionCargo",
    "HarborFreight","MountainRoute","ValleyShip","PlainsCargo","SkylineLog",
    "MarineEx","TerraRoute","ArcticFreight","DesertShip","ForestCargo",
    "RiverLog","LakeFreight","CanyonRoute","IslandShip","CoastalCargo",
    "NorthLog","SouthEx","EastFreight","WestRoute","CentralShip",
]
MODES  = ["AIR","SEA","GROUND"]
REGIONS = ["LATAM","NA","EU","APAC","MEA","CARIBE","SA","CA","AFRICA","OCEANIA"]

# Tag name pool — 150 unique tags
TAG_BASES = [
    ("fragile","handling"),("hazardous","handling"),("perishable","handling"),
    ("flammable","handling"),("heavy","handling"),("oversized","handling"),
    ("refrigerated","handling"),("frozen","handling"),("liquid","handling"),
    ("pressurized","handling"),("corrosive","handling"),("radioactive","handling"),
    ("organic","quality"),("certified","quality"),("premium","quality"),
    ("recycled","quality"),("vegan","quality"),("gluten-free","quality"),
    ("non-gmo","quality"),("fair-trade","quality"),("kosher","quality"),
    ("halal","quality"),("biodegradable","quality"),("compostable","quality"),
    ("express","shipping"),("bulk","shipping"),("drop-ship","shipping"),
    ("last-mile","shipping"),("white-glove","shipping"),("pallet","shipping"),
    ("ltl","shipping"),("ftl","shipping"),("intermodal","shipping"),
    ("seasonal","marketing"),("new-arrival","marketing"),("bestseller","marketing"),
    ("clearance","marketing"),("promo","marketing"),("limited","marketing"),
    ("exclusive","marketing"),("bundle","marketing"),("gift","marketing"),
    ("import","origin"),("export","origin"),("domestic","origin"),
    ("handmade","origin"),("local","origin"),("foreign","origin"),
    ("low-stock","inventory"),("discontinued","inventory"),("reorder","inventory"),
    ("backorder","inventory"),("overstock","inventory"),("damaged","inventory"),
    ("quarantine","compliance"),("recall","compliance"),("restricted","compliance"),
    ("regulated","compliance"),("licensed","compliance"),("patented","compliance"),
    ("high-value","finance"),("insured","finance"),("bonded","finance"),
    ("taxable","finance"),("duty-free","finance"),("rebate","finance"),
    ("raw-material","category"),("semi-finished","category"),("finished","category"),
    ("consumable","category"),("durable","category"),("spare-part","category"),
    ("electronic","category"),("mechanical","category"),("chemical","category"),
    ("biological","category"),("digital","category"),("physical","category"),
    ("urgent","priority"),("normal","priority"),("low-priority","priority"),
    ("critical","priority"),("standard","priority"),("expedited","priority"),
    ("a-grade","grading"),("b-grade","grading"),("c-grade","grading"),
    ("refurbished","grading"),("new","grading"),("used","grading"),
    ("small","size"),("medium","size"),("large","size"),
    ("xl","size"),("xxl","size"),("custom","size"),
    ("red","color"),("blue","color"),("green","color"),
    ("black","color"),("white","color"),("mixed","color"),
    ("plastic","material"),("metal","material"),("wood","material"),
    ("glass","material"),("ceramic","material"),("composite","material"),
    ("food-safe","safety"),("child-safe","safety"),("flame-retardant","safety"),
    ("waterproof","safety"),("anti-static","safety"),("non-toxic","safety"),
    ("q1","season"),("q2","season"),("q3","season"),("q4","season"),
    ("summer","season"),("winter","season"),
    ("online","channel"),("retail","channel"),("wholesale","channel"),
    ("b2b","channel"),("b2c","channel"),("marketplace","channel"),
    ("verified","status"),("pending-review","status"),("approved","status"),
    ("rejected","status"),("in-testing","status"),("active","status"),
    ("domestic-made","trade"),("imported","trade"),("re-exported","trade"),
    ("cross-border","trade"),("bonded-zone","trade"),("freeport","trade"),
    ("sustainable","esg"),("carbon-neutral","esg"),("ethical","esg"),
    ("renewable","esg"),("zero-waste","esg"),("social-impact","esg"),
    ("iot-enabled","tech"),("rfid-tagged","tech"),("blockchain-traced","tech"),
    ("ai-optimized","tech"),("automated","tech"),("smart-sensor","tech"),
    ("high-demand","demand"),("low-demand","demand"),("steady-demand","demand"),
    ("seasonal-demand","demand"),("cyclical","demand"),("erratic","demand"),
]
TAG_COLORS = [
    "#ef4444","#f97316","#eab308","#22c55e","#14b8a6","#3b82f6",
    "#8b5cf6","#ec4899","#64748b","#6366f1","#a855f7","#06b6d4",
    "#10b981","#f59e0b","#84cc16","#e11d48",
]

ORDER_STATUSES  = ["PENDING","SHIPPED","DELIVERED","RETURNED"]
STATUS_WEIGHTS  = [0.22, 0.28, 0.38, 0.12]
RETURN_REASONS  = [
    "Defective product","Wrong item shipped","Customer changed mind",
    "Damaged in transit","Not as described","Quality issues",
    "Arrived too late","Duplicate order","Missing parts","Size mismatch",
]

# ── Node factories ────────────────────────────────────────────────────────────

def make_suppliers(n):
    used, rows = set(), []
    while len(rows) < n:
        name = f"{pick(PREFIXES)} {pick(SUFFIXES)}"
        if name in used:
            name = f"{name} {len(rows)+1}"
        used.add(name)
        k = random.randint(0, 4)
        rows.append({
            "name":           name,
            "country":        pick(COUNTRIES),
            "active":         random.random() > 0.08,
            "rating":         round(random.uniform(2.0, 5.0), 2),
            "certifications": picks(CERTS, k) if k else [],
            "founded_at":     rand_date(1985, 2022),
        })
    return rows

def make_products(n):
    used, rows = set(), []
    while len(rows) < n:
        cat  = pick(CATEGORIES)
        adj  = pick(ADJ)
        noun = pick(NOUNS)
        sku  = f"{cat[:3].upper()}{adj[:2].upper()}{noun[:3].upper()}{random.randint(100,9999)}"
        if sku in used:
            continue
        used.add(sku)
        rows.append({
            "name":        f"{adj} {noun}",
            "sku":         sku,
            "price":       round(random.uniform(0.5, 9999.99), 2),
            "weight":      round(random.uniform(0.01, 1000.0), 3),
            "category":    cat,
            "in_stock":    random.random() > 0.12,
            "perishable":  random.random() < 0.18,
            "description": f"{adj} {noun} — {cat} application.",
        })
    return rows

def make_warehouses(n):
    used, rows = set(), []
    while len(rows) < n:
        city = pick(CITIES)
        code = f"WH{city[:2].upper()}{random.randint(10,999)}"
        if code in used:
            continue
        used.add(code)
        rows.append({
            "code":        code,
            "city":        city,
            "capacity":    random.randint(200, 100000),
            "active":      random.random() > 0.05,
            "coordinates": [],
            "opened_at":   rand_date(1995, 2023),
        })
    return rows

def make_orders(n):
    rows = []
    for _ in range(n):
        status = random.choices(ORDER_STATUSES, STATUS_WEIGHTS)[0]
        rows.append({
            "order_id":  f"ORD{uuid.uuid4().hex[:10].upper()}",
            "status":    status,
            "total":     round(random.uniform(5.0, 99999.0), 2),
            "placed_at": rand_dt(2020, 2025),
            "fulfilled": status == "DELIVERED",
            "notes":     pick(["","","","Priority","Fragile","Handle with care",
                               "Cold chain","No signature needed","Business hours only"]),
        })
    return rows

def make_carriers(n):
    pool = CARRIER_NAMES[:n] + [f"Carrier_{i:03d}" for i in range(n)]
    pool = list(dict.fromkeys(pool))[:n]
    rows = []
    for name in pool:
        n_modes = random.randint(1, 3)
        modes   = picks(MODES, n_modes)
        rows.append({
            "name":         name,
            "modes":        modes,
            "active":       random.random() > 0.07,
            "rating":       round(random.uniform(2.5, 5.0), 2),
            "regions":      picks(REGIONS, random.randint(1, 5)),
            "onboarded_at": rand_date(2005, 2023),
        })
    return rows

def make_tags(n):
    pool = list(TAG_BASES)
    # If we need more than the pool, generate extra ones
    extra_domains = ["zone","tier","flag","mark","class","type","kind","form"]
    extra_vals    = [f"tag-{i:03d}" for i in range(n)]
    while len(pool) < n:
        pool.append((pick(extra_vals), pick(extra_domains)))
    random.shuffle(pool)
    rows = []
    for name, cat in pool[:n]:
        rows.append({
            "name":       name,
            "category":   cat,
            "color_hex":  pick(TAG_COLORS),
            "created_at": rand_date(2017, 2024),
            "global_tag": random.random() > 0.20,
        })
    return rows

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    clear = "--clear" in sys.argv

    print("\n🌱  Supply Chain Seed — 7500 nodos")
    print("=" * 55)

    with get_session() as sess:
        if clear:
            print("  Limpiando base de datos...", end="", flush=True)
            sess.run("MATCH (n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 1000 ROWS")
            print(" ✓\n")

        # ── CREATE NODES ───────────────────────────────────
        print("📦  Creando nodos...\n")

        suppliers = make_suppliers(750)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Supplier {
                name: r.name, country: r.country, active: r.active,
                rating: r.rating, certifications: r.certifications,
                founded_at: date(r.founded_at), created_at: datetime()
            })
        """, suppliers, label="Suppliers (750)")

        products = make_products(2500)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Product {
                name: r.name, sku: r.sku, price: r.price, weight: r.weight,
                category: r.category, in_stock: r.in_stock, perishable: r.perishable,
                description: r.description, created_at: datetime()
            })
        """, products, label="Products (2500)")

        warehouses = make_warehouses(250)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Warehouse {
                code: r.code, city: r.city, capacity: r.capacity,
                active: r.active, coordinates: r.coordinates,
                opened_at: date(r.opened_at)
            })
        """, warehouses, label="Warehouses (250)")

        orders = make_orders(3700)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Order {
                order_id: r.order_id, status: r.status, total: r.total,
                placed_at: datetime(r.placed_at), fulfilled: r.fulfilled,
                notes: r.notes
            })
        """, orders, label="Orders (3700)")

        carriers = make_carriers(150)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Carrier {
                name: r.name, modes: r.modes, active: r.active,
                rating: r.rating, regions: r.regions,
                onboarded_at: date(r.onboarded_at)
            })
        """, carriers, label="Carriers (150)")

        tags = make_tags(150)
        batch_run(sess, """
            UNWIND $rows AS r
            CREATE (:Tag {
                name: r.name, category: r.category, color_hex: r.color_hex,
                created_at: date(r.created_at), global: r.global_tag
            })
        """, tags, label="Tags (150)")

        total_nodes = 750 + 2500 + 250 + 3700 + 150 + 150
        print(f"\n  ✓ {total_nodes:,} nodos creados\n")

        # ── FETCH IDs ──────────────────────────────────────
        print("🔗  Construyendo relaciones...\n")

        sup_ids  = [r["id"] for r in sess.run("MATCH (n:Supplier)  RETURN elementId(n) AS id")]
        prod_ids = [r["id"] for r in sess.run("MATCH (n:Product)   RETURN elementId(n) AS id")]
        wh_ids   = [r["id"] for r in sess.run("MATCH (n:Warehouse) RETURN elementId(n) AS id")]
        ord_ids  = [r["id"] for r in sess.run("MATCH (n:Order)     RETURN elementId(n) AS id")]
        car_ids  = [r["id"] for r in sess.run("MATCH (n:Carrier)   RETURN elementId(n) AS id")]
        tag_ids  = [r["id"] for r in sess.run("MATCH (n:Tag)       RETURN elementId(n) AS id")]

        # SUPPLIES  Supplier → Product  (~4 per supplier)
        rows = []
        for sid in sup_ids:
            for pid in picks(prod_ids, random.randint(2, 7)):
                rows.append({
                    "sid": sid, "pid": pid,
                    "since":          rand_date(2012, 2023),
                    "contract_price": round(random.uniform(0.5, 5000.0), 2),
                    "exclusive":      random.random() < 0.08,
                    "min_order_qty":  random.randint(1, 1000),
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (s:Supplier) WHERE elementId(s) = r.sid
            MATCH (p:Product)  WHERE elementId(p) = r.pid
            MERGE (s)-[rel:SUPPLIES]->(p)
            SET rel.since          = date(r.since),
                rel.contract_price = r.contract_price,
                rel.exclusive      = r.exclusive,
                rel.min_order_qty  = r.min_order_qty
        """, rows, label="SUPPLIES")

        # STORED_IN  Product → Warehouse  (~2 per product)
        rows = []
        for pid in prod_ids:
            for wid in picks(wh_ids, random.randint(1, 4)):
                qty = random.randint(0, 10000)
                rows.append({
                    "pid": pid, "wid": wid,
                    "quantity":     qty,
                    "reserved_qty": random.randint(0, max(1, qty // 5)),
                    "last_updated": rand_date(2023, 2025),
                    "bin_codes":    [f"BIN{random.randint(1,999):03d}" for _ in range(random.randint(1,4))],
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (p:Product)   WHERE elementId(p) = r.pid
            MATCH (w:Warehouse) WHERE elementId(w) = r.wid
            MERGE (p)-[rel:STORED_IN]->(w)
            SET rel.quantity     = r.quantity,
                rel.reserved_qty = r.reserved_qty,
                rel.last_updated = date(r.last_updated),
                rel.bin_codes    = r.bin_codes
        """, rows, label="STORED_IN")

        # SHIPS_VIA  Warehouse → Carrier  (~3 per warehouse)
        rows = []
        for wid in wh_ids:
            for cid in picks(car_ids, random.randint(2, 6)):
                rows.append({
                    "wid": wid, "cid": cid,
                    "contracted_since": rand_date(2010, 2023),
                    "priority":         random.randint(1, 5),
                    "max_weight_kg":    round(random.uniform(50, 50000), 1),
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (w:Warehouse) WHERE elementId(w) = r.wid
            MATCH (c:Carrier)   WHERE elementId(c) = r.cid
            MERGE (w)-[rel:SHIPS_VIA]->(c)
            SET rel.contracted_since = date(r.contracted_since),
                rel.priority         = r.priority,
                rel.max_weight_kg    = r.max_weight_kg
        """, rows, label="SHIPS_VIA")

        # TRANSFERS_TO  Warehouse → Warehouse
        pairs = [(a, b) for a in wh_ids for b in wh_ids if a != b]
        sample = random.sample(pairs, min(400, len(pairs)))
        rows = [{"w1": a, "w2": b,
                 "transfer_id":  f"TRF{uuid.uuid4().hex[:8].upper()}",
                 "scheduled_at": rand_dt(2023, 2025),
                 "completed":    random.random() > 0.45}
                for a, b in sample]
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (w1:Warehouse) WHERE elementId(w1) = r.w1
            MATCH (w2:Warehouse) WHERE elementId(w2) = r.w2
            MERGE (w1)-[rel:TRANSFERS_TO]->(w2)
            SET rel.transfer_id  = r.transfer_id,
                rel.scheduled_at = datetime(r.scheduled_at),
                rel.completed    = r.completed
        """, rows, label="TRANSFERS_TO")

        # CONTAINS  Order → Product  (~3 per order)
        rows = []
        for oid in ord_ids:
            for pid in picks(prod_ids, random.randint(1, 6)):
                rows.append({
                    "oid": oid, "pid": pid,
                    "quantity":   random.randint(1, 100),
                    "unit_price": round(random.uniform(0.5, 5000.0), 2),
                    "discount":   round(pick([0,0,0,0.05,0.10,0.15,0.20,0.25,0.30]), 2),
                    "note":       pick(["","","","Gift wrap","Urgent","No substitutes",
                                        "Fragile","Cold chain required"]),
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (o:Order)   WHERE elementId(o) = r.oid
            MATCH (p:Product) WHERE elementId(p) = r.pid
            MERGE (o)-[rel:CONTAINS]->(p)
            SET rel.quantity   = r.quantity,
                rel.unit_price = r.unit_price,
                rel.discount   = r.discount,
                rel.note       = r.note
        """, rows, label="CONTAINS")

        # SHIPPED_BY  Order → Carrier  (~88 % of orders)
        shipped = random.sample(ord_ids, int(len(ord_ids) * 0.88))
        rows = [{"oid": oid, "cid": pick(car_ids),
                 "tracking_id":        f"TRK{uuid.uuid4().hex[:12].upper()}",
                 "cost":               round(random.uniform(3.0, 3000.0), 2),
                 "dispatched_at":      rand_dt(2020, 2025),
                 "estimated_delivery": rand_date(2020, 2025)}
                for oid in shipped]
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (o:Order)   WHERE elementId(o) = r.oid
            MATCH (c:Carrier) WHERE elementId(c) = r.cid
            MERGE (o)-[rel:SHIPPED_BY]->(c)
            SET rel.tracking_id        = r.tracking_id,
                rel.cost               = r.cost,
                rel.dispatched_at      = datetime(r.dispatched_at),
                rel.estimated_delivery = date(r.estimated_delivery)
        """, rows, label="SHIPPED_BY")

        # RETURNS_TO  Order → Supplier  (~15 % of orders)
        returned = random.sample(ord_ids, int(len(ord_ids) * 0.15))
        rows = [{"oid": oid, "sid": pick(sup_ids),
                 "reason":        pick(RETURN_REASONS),
                 "returned_at":   rand_dt(2020, 2025),
                 "refund_amount": round(random.uniform(1.0, 9999.0), 2)}
                for oid in returned]
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (o:Order)    WHERE elementId(o) = r.oid
            MATCH (s:Supplier) WHERE elementId(s) = r.sid
            MERGE (o)-[rel:RETURNS_TO]->(s)
            SET rel.reason        = r.reason,
                rel.returned_at   = datetime(r.returned_at),
                rel.refund_amount = r.refund_amount
        """, rows, label="RETURNS_TO")

        # PARTNERS_WITH  Carrier → Supplier  (~4 per carrier)
        rows = []
        for cid in car_ids:
            for sid in picks(sup_ids, random.randint(2, 7)):
                rows.append({
                    "cid": cid, "sid": sid,
                    "since":         rand_date(2010, 2023),
                    "discount_rate": round(random.uniform(0.01, 0.30), 3),
                    "preferred":     random.random() < 0.25,
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (c:Carrier)  WHERE elementId(c) = r.cid
            MATCH (s:Supplier) WHERE elementId(s) = r.sid
            MERGE (c)-[rel:PARTNERS_WITH]->(s)
            SET rel.since         = date(r.since),
                rel.discount_rate = r.discount_rate,
                rel.preferred     = r.preferred
        """, rows, label="PARTNERS_WITH")

        # TAGGED_AS  Tag → Product  (~3 per product on avg)
        rows = []
        for pid in prod_ids:
            for tid in picks(tag_ids, random.randint(1, 5)):
                rows.append({
                    "tid": tid, "pid": pid,
                    "tagged_at":     rand_dt(2019, 2025),
                    "auto_assigned": random.random() < 0.55,
                    "weight":        round(random.uniform(0.1, 1.0), 3),
                })
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (t:Tag)     WHERE elementId(t) = r.tid
            MATCH (p:Product) WHERE elementId(p) = r.pid
            MERGE (t)-[rel:TAGGED_AS]->(p)
            SET rel.tagged_at     = datetime(r.tagged_at),
                rel.auto_assigned = r.auto_assigned,
                rel.weight        = r.weight
        """, rows, label="TAGGED_AS")

        # FULFILLS  Warehouse → Order  (~90 % of orders)
        fulfilled = random.sample(ord_ids, int(len(ord_ids) * 0.90))
        rows = [{"wid": pick(wh_ids), "oid": oid,
                 "fulfilled_at": rand_dt(2020, 2025),
                 "items_count":  random.randint(1, 30),
                 "partial":      random.random() < 0.10}
                for oid in fulfilled]
        batch_run(sess, """
            UNWIND $rows AS r
            MATCH (w:Warehouse) WHERE elementId(w) = r.wid
            MATCH (o:Order)     WHERE elementId(o) = r.oid
            MERGE (w)-[rel:FULFILLS]->(o)
            SET rel.fulfilled_at = datetime(r.fulfilled_at),
                rel.items_count  = r.items_count,
                rel.partial      = r.partial
        """, rows, label="FULFILLS")

        # ── Final counts ───────────────────────────────────
        print()
        node_counts = {
            r["label"]: r["count"]
            for r in sess.run(
                "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
            ) if r["label"]
        }
        rel_counts = {
            r["type"]: r["count"]
            for r in sess.run(
                "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
            )
        }

    driver.close()

    tn = sum(node_counts.values())
    tr = sum(rel_counts.values())

    print("\n" + "=" * 55)
    print("✅  Seed completado!\n")
    print("  Nodos:")
    for k, v in sorted(node_counts.items(), key=lambda x: -x[1]):
        print(f"    {k:<20s} {v:>7,}")
    print(f"    {'─'*28}")
    print(f"    {'TOTAL':<20s} {tn:>7,}\n")
    print("  Relaciones:")
    for k, v in sorted(rel_counts.items(), key=lambda x: -x[1]):
        print(f"    {k:<20s} {v:>7,}")
    print(f"    {'─'*28}")
    print(f"    {'TOTAL':<20s} {tr:>7,}\n")
    print(f"  📊 Grand total registros: {tn + tr:,}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
