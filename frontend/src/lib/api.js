const BASE = "http://localhost:8000";

async function req(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  if (res.status === 204) return null;
  return res.json();
}

async function upload(path, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(BASE + path, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export const api = {
  health: () => req("GET", "/health"),

  // Suppliers
  suppliers: {
    list: (p = {}) => req("GET", "/suppliers/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/suppliers/${id}`),
    create: (d) => req("POST", "/suppliers/", d),
    update: (id, d) => req("PATCH", `/suppliers/${id}`, d),
    remove: (id) => req("DELETE", `/suppliers/${id}`),
    stats: () => req("GET", "/suppliers/stats"),
  },

  // Products
  products: {
    list: (p = {}) => req("GET", "/products/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/products/${id}`),
    create: (d) => req("POST", "/products/", d),
    update: (id, d) => req("PATCH", `/products/${id}`, d),
    remove: (id) => req("DELETE", `/products/${id}`),
    stats: () => req("GET", "/products/stats"),
  },

  // Warehouses
  warehouses: {
    list: (p = {}) => req("GET", "/warehouses/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/warehouses/${id}`),
    create: (d) => req("POST", "/warehouses/", d),
    update: (id, d) => req("PATCH", `/warehouses/${id}`, d),
    remove: (id) => req("DELETE", `/warehouses/${id}`),
    inventory: (id) => req("GET", `/warehouses/${id}/inventory`),
  },

  // Orders
  orders: {
    list: (p = {}) => req("GET", "/orders/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/orders/${id}`),
    create: (d) => req("POST", "/orders/", d),
    update: (id, d) => req("PATCH", `/orders/${id}`, d),
    remove: (id) => req("DELETE", `/orders/${id}`),
    stats: () => req("GET", "/orders/stats"),
  },

  // Carriers
  carriers: {
    list: (p = {}) => req("GET", "/carriers/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/carriers/${id}`),
    create: (d) => req("POST", "/carriers/", d),
    update: (id, d) => req("PATCH", `/carriers/${id}`, d),
    remove: (id) => req("DELETE", `/carriers/${id}`),
  },

  // Tags
  tags: {
    list: (p = {}) => req("GET", "/tags/?" + new URLSearchParams(p)),
    get: (id) => req("GET", `/tags/${id}`),
    create: (d) => req("POST", "/tags/", d),
    update: (id, d) => req("PATCH", `/tags/${id}`, d),
    remove: (id) => req("DELETE", `/tags/${id}`),
  },

  // Relationships
  relationships: {
    supplies: (d) => req("POST", "/relationships/supplies", d),
    storedIn: (d) => req("POST", "/relationships/stored_in", d),
    shipsVia: (d) => req("POST", "/relationships/ships_via", d),
    contains: (d) => req("POST", "/relationships/contains", d),
    shippedBy: (d) => req("POST", "/relationships/shipped_by", d),
    returnsTo: (d) => req("POST", "/relationships/returns_to", d),
    partnersWith: (d) => req("POST", "/relationships/partners_with", d),
    taggedAs: (d) => req("POST", "/relationships/tagged_as", d),
    fulfills: (d) => req("POST", "/relationships/fulfills", d),
    transfersTo: (d) => req("POST", "/relationships/transfers_to", d),
    deleteSingle: (d) => req("DELETE", "/relationships/single", d),
  },

  // Graph / Analytics
  graph: {
    counts: () => req("GET", "/graph/counts"),
    overview: () => req("GET", "/graph/overview"),
    topSuppliers: () => req("GET", "/graph/queries/top_suppliers_by_products"),
    warehouseInventory: () => req("GET", "/graph/queries/warehouse_inventory_summary"),
    carrierPerformance: () => req("GET", "/graph/queries/order_carrier_performance"),
    returnAnalysis: () => req("GET", "/graph/queries/return_analysis"),
    supplyChainPaths: () => req("GET", "/graph/queries/supply_chain_paths"),
    taggedProducts: () => req("GET", "/graph/queries/tagged_product_count"),
    pagerank: () => req("GET", "/graph/algorithms/pagerank"),
    shortestPath: (from, to) => req("GET", `/graph/algorithms/shortest_path?from_id=${from}&to_id=${to}`),
  },

  // CSV
  csv: {
    suppliers: (file) => upload("/csv/suppliers", file),
    products: (file) => upload("/csv/products", file),
    warehouses: (file) => upload("/csv/warehouses", file),
    orders: (file) => upload("/csv/orders", file),
    carriers: (file) => upload("/csv/carriers", file),
    relSupplies: (file) => upload("/csv/relationships/supplies", file),
    relStoredIn: (file) => upload("/csv/relationships/stored_in", file),
  },
};
