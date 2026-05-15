<script>
  import { onMount } from "svelte";
  import { api } from "../lib/api.js";
  import { toast } from "../lib/toast.svelte.js";

  let suppliers = $state([]);
  let products = $state([]);
  let warehouses = $state([]);
  let orders = $state([]);
  let carriers = $state([]);
  let tags = $state([]);

  let activeRel = $state("supplies");
  let loading = $state(false);

  onMount(async () => {
    try {
      [suppliers, products, warehouses, orders, carriers, tags] = await Promise.all([
        api.suppliers.list({ limit: 200 }),
        api.products.list({ limit: 200 }),
        api.warehouses.list({ limit: 200 }),
        api.orders.list({ limit: 200 }),
        api.carriers.list({ limit: 200 }),
        api.tags.list({ limit: 200 }),
      ]);
    } catch (e) {
      toast(e.message, "error");
    }
  });

  // Form state for each relationship type
  let forms = $state({
    supplies: { supplier_id: "", product_id: "", since: "", contract_price: 0, exclusive: false, min_order_qty: 1 },
    stored_in: { product_id: "", warehouse_id: "", quantity: 0, last_updated: "", bin_codes: "", reserved_qty: 0 },
    ships_via: { warehouse_id: "", carrier_id: "", contracted_since: "", priority: 1, max_weight_kg: 1000 },
    contains: { order_id: "", product_id: "", quantity: 1, unit_price: 0, discount: 0, note: "" },
    shipped_by: { order_id: "", carrier_id: "", tracking_id: "", cost: 0, dispatched_at: "", estimated_delivery: "" },
    returns_to: { order_id: "", supplier_id: "", reason: "", returned_at: "", refund_amount: 0 },
    partners_with: { carrier_id: "", supplier_id: "", since: "", discount_rate: 0, preferred: false },
    tagged_as: { tag_id: "", product_id: "", tagged_at: "", auto_assigned: false, weight: 1.0 },
    fulfills: { warehouse_id: "", order_id: "", fulfilled_at: "", items_count: 1, partial: false },
    transfers_to: { from_warehouse_id: "", to_warehouse_id: "", transfer_id: "", scheduled_at: "", completed: false },
  });

  const relTabs = [
    { key: "supplies", label: "SUPPLIES" },
    { key: "stored_in", label: "STORED_IN" },
    { key: "ships_via", label: "SHIPS_VIA" },
    { key: "contains", label: "CONTAINS" },
    { key: "shipped_by", label: "SHIPPED_BY" },
    { key: "returns_to", label: "RETURNS_TO" },
    { key: "partners_with", label: "PARTNERS_WITH" },
    { key: "tagged_as", label: "TAGGED_AS" },
    { key: "fulfills", label: "FULFILLS" },
    { key: "transfers_to", label: "TRANSFERS_TO" },
  ];

  function opt(list, labelKey = "name") {
    return list.map((i) => ({ value: i.id, label: i[labelKey] || i.code || i.order_id || i.id }));
  }

  async function submit() {
    loading = true;
    const f = forms[activeRel];
    try {
      let data = { ...f };
      // Convert numeric fields
      ["contract_price","min_order_qty","quantity","reserved_qty","priority","max_weight_kg",
       "unit_price","discount","cost","refund_amount","discount_rate","weight","items_count"].forEach((k) => {
        if (k in data) data[k] = Number(data[k]);
      });
      if ("bin_codes" in data) {
        data.bin_codes = data.bin_codes ? data.bin_codes.split(",").map((s) => s.trim()).filter(Boolean) : [];
      }
      if (activeRel === "supplies") await api.relationships.supplies(data);
      else if (activeRel === "stored_in") await api.relationships.storedIn(data);
      else if (activeRel === "ships_via") await api.relationships.shipsVia(data);
      else if (activeRel === "contains") await api.relationships.contains(data);
      else if (activeRel === "shipped_by") await api.relationships.shippedBy(data);
      else if (activeRel === "returns_to") await api.relationships.returnsTo(data);
      else if (activeRel === "partners_with") await api.relationships.partnersWith(data);
      else if (activeRel === "tagged_as") await api.relationships.taggedAs(data);
      else if (activeRel === "fulfills") await api.relationships.fulfills(data);
      else if (activeRel === "transfers_to") await api.relationships.transfersTo(data);
      toast("Relación creada", "success");
    } catch (e) {
      toast(e.message, "error");
    } finally {
      loading = false;
    }
  }

  function sel(items, labelFn) {
    return items.map((i) => ({ value: i.id, label: labelFn(i) }));
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Relaciones</h1>
  </div>

  <div class="tabs">
    {#each relTabs as tab}
      <button class="tab" class:active={activeRel === tab.key} onclick={() => activeRel = tab.key}>
        {tab.label}
      </button>
    {/each}
  </div>

  <div class="form-card">
    <form onsubmit={(e) => { e.preventDefault(); submit(); }} class="form">

      {#if activeRel === "supplies"}
        <label>Proveedor
          <select bind:value={forms.supplies.supplier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(suppliers, (s) => s.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Producto
          <select bind:value={forms.supplies.product_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(products, (p) => `${p.sku} — ${p.name}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-3">
          <label>Desde <input type="date" bind:value={forms.supplies.since} required /></label>
          <label>Precio contrato ($) <input type="number" step="0.01" bind:value={forms.supplies.contract_price} /></label>
          <label>Cant. mínima <input type="number" min="1" bind:value={forms.supplies.min_order_qty} /></label>
        </div>
        <label class="check"><input type="checkbox" bind:checked={forms.supplies.exclusive} /> Exclusivo</label>

      {:else if activeRel === "stored_in"}
        <label>Producto
          <select bind:value={forms.stored_in.product_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(products, (p) => `${p.sku} — ${p.name}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Bodega
          <select bind:value={forms.stored_in.warehouse_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(warehouses, (w) => `${w.code} — ${w.city}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-3">
          <label>Cantidad <input type="number" min="0" bind:value={forms.stored_in.quantity} /></label>
          <label>Reservado <input type="number" min="0" bind:value={forms.stored_in.reserved_qty} /></label>
          <label>Actualizado <input type="date" bind:value={forms.stored_in.last_updated} required /></label>
        </div>
        <label>Bin codes (coma-sep) <input bind:value={forms.stored_in.bin_codes} placeholder="A1, B2..." /></label>

      {:else if activeRel === "ships_via"}
        <label>Bodega
          <select bind:value={forms.ships_via.warehouse_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(warehouses, (w) => `${w.code} — ${w.city}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Transportista
          <select bind:value={forms.ships_via.carrier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(carriers, (c) => c.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-3">
          <label>Contrato desde <input type="date" bind:value={forms.ships_via.contracted_since} required /></label>
          <label>Prioridad <input type="number" min="1" bind:value={forms.ships_via.priority} /></label>
          <label>Peso máx (kg) <input type="number" step="0.1" bind:value={forms.ships_via.max_weight_kg} /></label>
        </div>

      {:else if activeRel === "contains"}
        <label>Orden
          <select bind:value={forms.contains.order_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(orders, (o) => o.order_id) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Producto
          <select bind:value={forms.contains.product_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(products, (p) => `${p.sku} — ${p.name}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-3">
          <label>Cantidad <input type="number" min="1" bind:value={forms.contains.quantity} /></label>
          <label>Precio unitario ($) <input type="number" step="0.01" bind:value={forms.contains.unit_price} /></label>
          <label>Descuento (%) <input type="number" step="0.01" min="0" bind:value={forms.contains.discount} /></label>
        </div>
        <label>Nota <input bind:value={forms.contains.note} /></label>

      {:else if activeRel === "shipped_by"}
        <label>Orden
          <select bind:value={forms.shipped_by.order_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(orders, (o) => o.order_id) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Transportista
          <select bind:value={forms.shipped_by.carrier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(carriers, (c) => c.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Tracking ID <input bind:value={forms.shipped_by.tracking_id} required /></label>
          <label>Costo ($) <input type="number" step="0.01" bind:value={forms.shipped_by.cost} /></label>
          <label>Despacho <input type="datetime-local" bind:value={forms.shipped_by.dispatched_at} required /></label>
          <label>Entrega estimada <input type="date" bind:value={forms.shipped_by.estimated_delivery} required /></label>
        </div>

      {:else if activeRel === "returns_to"}
        <label>Orden
          <select bind:value={forms.returns_to.order_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(orders, (o) => o.order_id) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Proveedor
          <select bind:value={forms.returns_to.supplier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(suppliers, (s) => s.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Razón <input bind:value={forms.returns_to.reason} required /></label>
          <label>Monto reembolso ($) <input type="number" step="0.01" bind:value={forms.returns_to.refund_amount} /></label>
          <label>Fecha devolución <input type="datetime-local" bind:value={forms.returns_to.returned_at} required /></label>
        </div>

      {:else if activeRel === "partners_with"}
        <label>Transportista
          <select bind:value={forms.partners_with.carrier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(carriers, (c) => c.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Proveedor
          <select bind:value={forms.partners_with.supplier_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(suppliers, (s) => s.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Desde <input type="date" bind:value={forms.partners_with.since} required /></label>
          <label>Descuento (%) <input type="number" step="0.01" min="0" bind:value={forms.partners_with.discount_rate} /></label>
        </div>
        <label class="check"><input type="checkbox" bind:checked={forms.partners_with.preferred} /> Preferido</label>

      {:else if activeRel === "tagged_as"}
        <label>Tag
          <select bind:value={forms.tagged_as.tag_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(tags, (t) => t.name) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Producto
          <select bind:value={forms.tagged_as.product_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(products, (p) => `${p.sku} — ${p.name}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Etiquetado en <input type="datetime-local" bind:value={forms.tagged_as.tagged_at} required /></label>
          <label>Peso <input type="number" step="0.1" min="0" bind:value={forms.tagged_as.weight} /></label>
        </div>
        <label class="check"><input type="checkbox" bind:checked={forms.tagged_as.auto_assigned} /> Auto-asignado</label>

      {:else if activeRel === "fulfills"}
        <label>Bodega
          <select bind:value={forms.fulfills.warehouse_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(warehouses, (w) => `${w.code} — ${w.city}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Orden
          <select bind:value={forms.fulfills.order_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(orders, (o) => o.order_id) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Cumplida en <input type="datetime-local" bind:value={forms.fulfills.fulfilled_at} required /></label>
          <label>Artículos <input type="number" min="1" bind:value={forms.fulfills.items_count} /></label>
        </div>
        <label class="check"><input type="checkbox" bind:checked={forms.fulfills.partial} /> Parcial</label>

      {:else if activeRel === "transfers_to"}
        <label>Bodega origen
          <select bind:value={forms.transfers_to.from_warehouse_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(warehouses, (w) => `${w.code} — ${w.city}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <label>Bodega destino
          <select bind:value={forms.transfers_to.to_warehouse_id} required>
            <option value="">-- seleccionar --</option>
            {#each sel(warehouses, (w) => `${w.code} — ${w.city}`) as o}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </label>
        <div class="grid-2">
          <label>Transfer ID <input bind:value={forms.transfers_to.transfer_id} required /></label>
          <label>Programado <input type="datetime-local" bind:value={forms.transfers_to.scheduled_at} required /></label>
        </div>
        <label class="check"><input type="checkbox" bind:checked={forms.transfers_to.completed} /> Completado</label>
      {/if}

      <div class="form-actions">
        <button type="submit" class="btn-primary" disabled={loading}>
          {loading ? "Creando..." : "Crear Relación"}
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.25rem; }
  .tabs { display: flex; flex-wrap: wrap; gap: 0.35rem; }
  .tab {
    background: var(--card);
    border: 1px solid var(--border-sub);
    color: var(--text-3);
    padding: 0.28rem 0.65rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: ui-monospace, "Cascadia Code", "Fira Code", monospace;
    letter-spacing: 0.03em;
    transition: background 0.1s, color 0.1s, border-color 0.1s;
    font-family: inherit;
  }
  .tab:hover { color: var(--text-2); border-color: var(--border); background: var(--hover); }
  .tab.active {
    background: var(--cyan-dim);
    color: var(--cyan);
    border-color: var(--cyan-border);
  }
  .form-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    padding: 1.25rem;
  }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; }
</style>
