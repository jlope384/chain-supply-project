from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_session

router = APIRouter()

def node_to_dict(node):
    d = dict(node)
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d

@router.get("/overview")
async def graph_overview():
    """Overall node and relationship counts by label/type."""
    with get_session() as session:
        node_result = session.run("""
            CALL apoc.meta.stats() YIELD labels, relTypesCount
            RETURN labels, relTypesCount
        """)
        record = node_result.single()
        if record:
            return {"labels": dict(record["labels"]), "relationships": dict(record["relTypesCount"])}
        # Fallback without APOC
        nr = session.run("""
            MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count
        """)
        rr = session.run("""
            MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count
        """)
        return {
            "labels": {r["label"]: r["count"] for r in nr if r["label"]},
            "relationships": {r["type"]: r["count"] for r in rr},
        }

@router.get("/counts")
async def node_counts():
    with get_session() as session:
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] AS label, count(n) AS count
            ORDER BY count DESC
        """)
        return {r["label"]: r["count"] for r in result if r["label"]}

@router.get("/connectivity")
async def connectivity_check():
    """Check if graph is connected (weakly)."""
    with get_session() as session:
        result = session.run("""
            MATCH (n)
            WITH count(n) AS total
            CALL {
                MATCH (start) WITH start LIMIT 1
                CALL apoc.path.subgraphNodes(start, {}) YIELD node
                RETURN count(node) AS reachable
            }
            RETURN total, reachable, total = reachable AS connected
        """)
        record = result.single()
        if record:
            return {"total_nodes": record["total"], "reachable": record["reachable"], "connected": record["connected"]}
        return {"message": "APOC not available for connectivity check"}

# ──────────────────────────────────────────────
# Predefined analytics Cypher queries (6 total)
# ──────────────────────────────────────────────

@router.get("/queries/top_suppliers_by_products")
async def top_suppliers_by_products():
    """Query 1: Top suppliers by number of products they supply."""
    with get_session() as session:
        result = session.run("""
            MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)
            RETURN s.name AS supplier, s.country AS country,
                   count(p) AS product_count,
                   avg(s.rating) AS rating
            ORDER BY product_count DESC
            LIMIT 10
        """)
        return [dict(r) for r in result]

@router.get("/queries/warehouse_inventory_summary")
async def warehouse_inventory_summary():
    """Query 2: Inventory summary per warehouse."""
    with get_session() as session:
        result = session.run("""
            MATCH (p:Product)-[r:STORED_IN]->(w:Warehouse)
            RETURN w.code AS warehouse, w.city AS city,
                   count(p) AS distinct_products,
                   sum(r.quantity) AS total_units,
                   sum(r.reserved_qty) AS reserved_units
            ORDER BY total_units DESC
        """)
        return [dict(r) for r in result]

@router.get("/queries/order_carrier_performance")
async def order_carrier_performance():
    """Query 3: Carrier performance by shipment count and avg cost."""
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order)-[r:SHIPPED_BY]->(c:Carrier)
            RETURN c.name AS carrier,
                   count(o) AS shipments,
                   avg(r.cost) AS avg_shipping_cost,
                   c.rating AS carrier_rating
            ORDER BY shipments DESC
        """)
        return [dict(r) for r in result]

@router.get("/queries/return_analysis")
async def return_analysis():
    """Query 4: Return analysis by supplier."""
    with get_session() as session:
        result = session.run("""
            MATCH (o:Order)-[r:RETURNS_TO]->(s:Supplier)
            RETURN s.name AS supplier,
                   count(o) AS return_count,
                   sum(r.refund_amount) AS total_refund,
                   collect(DISTINCT r.reason) AS reasons
            ORDER BY return_count DESC
        """)
        return [dict(r) for r in result]

@router.get("/queries/supply_chain_paths")
async def supply_chain_paths():
    """Query 5: Full supply chain path Supplier->Product->Warehouse->Carrier."""
    with get_session() as session:
        result = session.run("""
            MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)-[:STORED_IN]->(w:Warehouse)-[:SHIPS_VIA]->(c:Carrier)
            RETURN s.name AS supplier, p.name AS product,
                   w.code AS warehouse, c.name AS carrier
            LIMIT 20
        """)
        return [dict(r) for r in result]

@router.get("/queries/tagged_product_count")
async def tagged_product_count():
    """Query 6: Tags with most products, with aggregation."""
    with get_session() as session:
        result = session.run("""
            MATCH (t:Tag)-[:TAGGED_AS]->(p:Product)
            RETURN t.name AS tag, t.category AS category,
                   count(p) AS product_count,
                   avg(p.price) AS avg_product_price
            ORDER BY product_count DESC
            LIMIT 15
        """)
        return [dict(r) for r in result]

# ──────────────────────────────────────────────
# Data Science: PageRank on supplier network
# ──────────────────────────────────────────────
@router.get("/algorithms/pagerank")
async def pagerank():
    """Run PageRank on the supply chain graph using GDS (if available)."""
    with get_session() as session:
        try:
            # Project graph
            session.run("""
                CALL gds.graph.project.cypher(
                    'supply_graph',
                    'MATCH (n) RETURN id(n) AS id',
                    'MATCH (a)-[]->(b) RETURN id(a) AS source, id(b) AS target'
                )
            """)
            result = session.run("""
                CALL gds.pageRank.stream('supply_graph')
                YIELD nodeId, score
                MATCH (n) WHERE id(n) = nodeId
                RETURN labels(n)[0] AS label,
                       coalesce(n.name, n.code, n.order_id, n.sku) AS name,
                       round(score, 4) AS score
                ORDER BY score DESC LIMIT 20
            """)
            data = [dict(r) for r in result]
            session.run("CALL gds.graph.drop('supply_graph')")
            return data
        except Exception as e:
            return {"error": str(e), "message": "GDS plugin may not be available"}

@router.get("/algorithms/shortest_path")
async def shortest_path(from_id: str, to_id: str):
    """Find shortest path between two nodes."""
    with get_session() as session:
        result = session.run("""
            MATCH (a) WHERE elementId(a) = $from_id
            MATCH (b) WHERE elementId(b) = $to_id
            MATCH path = shortestPath((a)-[*]-(b))
            RETURN [n IN nodes(path) | 
                coalesce(n.name, n.code, n.order_id, n.sku, 'unknown')] AS path_nodes,
                length(path) AS hops
        """, from_id=from_id, to_id=to_id)
        record = result.single()
        if not record:
            raise HTTPException(404, "No path found")
        return {"path": record["path_nodes"], "hops": record["hops"]}
