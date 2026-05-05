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
  <h1>Gestión de Relaciones</h1>

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
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  .tabs { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .tab {
    background: #1e293b; border: 1px solid #334155; color: #94a3b8;
    padding: 0.4rem 0.85rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-weight: 600;
    font-family: monospace;
  }
  .tab.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
  .form-card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.5rem; }
  .form { display: flex; flex-direction: column; gap: 0.75rem; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; }
  label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; color: #94a3b8; }
  label.check { flex-direction: row; align-items: center; gap: 0.5rem; color: #e2e8f0; }
  input, select {
    background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
    padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box;
  }
  .form-actions { display: flex; justify-content: flex-end; margin-top: 0.5rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.5rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-primary:hover:not(:disabled) { background: #4338ca; }
</style>
