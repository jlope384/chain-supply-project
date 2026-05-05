<script>
  import { onMount } from "svelte";
  import { api } from "../lib/api.js";
  import { toast } from "../lib/toast.svelte.js";
  import DataTable from "../lib/DataTable.svelte";
  import Modal from "../lib/Modal.svelte";

  let rows = $state([]);
  let loading = $state(true);
  let showModal = $state(false);
  let showInventory = $state(false);
  let editing = $state(null);
  let inventory = $state([]);
  let inventoryWarehouse = $state(null);
  let form = $state(defaultForm());

  function defaultForm() {
    return { code: "", city: "", capacity: 1000, active: true, opened_at: "" };
  }

  const columns = [
    { key: "code", label: "Código" },
    { key: "city", label: "Ciudad" },
    { key: "capacity", label: "Capacidad" },
    { key: "active", label: "Activo", render: (v) => v ? "✅" : "❌" },
    { key: "opened_at", label: "Apertura" },
  ];

  const invColumns = [
    { key: "sku", label: "SKU" },
    { key: "name", label: "Producto" },
    { key: "quantity", label: "Cantidad" },
    { key: "reserved_qty", label: "Reservado" },
    { key: "last_updated", label: "Actualizado" },
  ];

  async function load() {
    loading = true;
    try { rows = await api.warehouses.list(); }
    catch (e) { toast(e.message, "error"); }
    finally { loading = false; }
  }

  onMount(load);

  function openCreate() { editing = null; form = defaultForm(); showModal = true; }

  function openEdit(row) {
    editing = row;
    form = { code: row.code, city: row.city, capacity: row.capacity, active: row.active, opened_at: row.opened_at || "" };
    showModal = true;
  }

  async function viewInventory(row) {
    inventoryWarehouse = row;
    try { inventory = await api.warehouses.inventory(row.id); }
    catch (e) { inventory = []; toast(e.message, "error"); }
    showInventory = true;
  }

  async function save() {
    const data = { ...form, capacity: Number(form.capacity) };
    if (!data.opened_at) delete data.opened_at;
    try {
      if (editing) {
        await api.warehouses.update(editing.id, data);
        toast("Bodega actualizada", "success");
      } else {
        await api.warehouses.create(data);
        toast("Bodega creada", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar bodega "${row.code}"?`)) return;
    try { await api.warehouses.remove(row.id); toast("Eliminada", "success"); load(); }
    catch (e) { toast(e.message, "error"); }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Bodegas</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nueva</button>
  </div>

  <div class="table-wrap-custom">
    {#if loading}
      <p class="muted">Cargando...</p>
    {:else if rows.length === 0}
      <p class="muted">Sin bodegas registradas</p>
    {:else}
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              {#each columns as col}<th>{col.label}</th>{/each}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each rows as row}
              <tr>
                {#each columns as col}
                  <td>{col.render ? col.render(row[col.key]) : row[col.key] ?? "—"}</td>
                {/each}
                <td class="actions">
                  <button class="btn-icon" onclick={() => viewInventory(row)}>📦</button>
                  <button class="btn-icon" onclick={() => openEdit(row)}>✏️</button>
                  <button class="btn-icon" onclick={() => remove(row)}>🗑️</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<Modal bind:open={showModal} title={editing ? "Editar Bodega" : "Nueva Bodega"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <div class="grid-2">
      <label>Código <input bind:value={form.code} required /></label>
      <label>Ciudad <input bind:value={form.city} required /></label>
      <label>Capacidad <input type="number" min="1" bind:value={form.capacity} /></label>
      <label>Apertura <input type="date" bind:value={form.opened_at} /></label>
    </div>
    <label class="check"><input type="checkbox" bind:checked={form.active} /> Activa</label>
    <div class="form-actions">
      <button type="button" class="btn-ghost" onclick={() => showModal = false}>Cancelar</button>
      <button type="submit" class="btn-primary">Guardar</button>
    </div>
  </form>
</Modal>

<Modal bind:open={showInventory} title="Inventario — {inventoryWarehouse?.code} ({inventoryWarehouse?.city})">
  <DataTable rows={inventory} columns={invColumns} />
</Modal>

<style>
  .page { display: flex; flex-direction: column; gap: 1.25rem; }
  .page-header { display: flex; justify-content: space-between; align-items: center; }
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  .muted { color: #64748b; }
  .table-scroll { overflow-x: auto; border-radius: 8px; border: 1px solid #334155; }
  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  th { background: #1e293b; color: #94a3b8; padding: 0.75rem 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid #334155; }
  td { padding: 0.65rem 1rem; border-bottom: 1px solid #1e293b; color: #e2e8f0; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #1e293b; }
  .actions { display: flex; gap: 0.5rem; }
  .btn-icon { background: none; border: none; cursor: pointer; font-size: 1rem; opacity: 0.7; }
  .btn-icon:hover { opacity: 1; }
  .form { display: flex; flex-direction: column; gap: 0.75rem; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; color: #94a3b8; }
  label.check { flex-direction: row; align-items: center; gap: 0.5rem; color: #e2e8f0; }
  input { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }
  .form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:hover { background: #4338ca; }
  .btn-ghost { background: none; border: 1px solid #334155; color: #94a3b8; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
</style>
