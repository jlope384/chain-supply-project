<script>
  import { onMount } from "svelte";
  import { api } from "../lib/api.js";
  import { toast } from "../lib/toast.svelte.js";
  import DataTable from "../lib/DataTable.svelte";
  import Modal from "../lib/Modal.svelte";

  let rows = $state([]);
  let loading = $state(true);
  let showModal = $state(false);
  let editing = $state(null);
  let form = $state(defaultForm());

  const STATUSES = ["PENDING", "SHIPPED", "DELIVERED", "RETURNED"];

  function defaultForm() {
    return { order_id: "", status: "PENDING", total: 0, placed_at: "", fulfilled: false, notes: "" };
  }

  const statusColors = { PENDING: "#fde68a", SHIPPED: "#93c5fd", DELIVERED: "#86efac", RETURNED: "#fca5a5" };

  const columns = [
    { key: "order_id", label: "ID Orden" },
    { key: "status", label: "Estado", render: (v) => `<span style="color:${statusColors[v] || '#e2e8f0'}">${v}</span>` },
    { key: "total", label: "Total", render: (v) => `$${Number(v ?? 0).toFixed(2)}` },
    { key: "fulfilled", label: "Cumplida", render: (v) => v ? "✅" : "❌" },
    { key: "placed_at", label: "Fecha", render: (v) => v ? v.substring(0, 10) : "—" },
    { key: "notes", label: "Notas" },
  ];

  async function load() {
    loading = true;
    try { rows = await api.orders.list(); }
    catch (e) { toast(e.message, "error"); }
    finally { loading = false; }
  }

  onMount(load);

  function openCreate() { editing = null; form = defaultForm(); showModal = true; }

  function openEdit(row) {
    editing = row;
    form = { order_id: row.order_id, status: row.status, total: row.total, placed_at: "", fulfilled: row.fulfilled, notes: row.notes || "" };
    showModal = true;
  }

  async function save() {
    const data = { ...form, total: Number(form.total) };
    if (!data.placed_at) delete data.placed_at;
    try {
      if (editing) {
        const { order_id, placed_at, ...updateData } = data;
        await api.orders.update(editing.id, updateData);
        toast("Orden actualizada", "success");
      } else {
        await api.orders.create(data);
        toast("Orden creada", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar orden "${row.order_id}"?`)) return;
    try { await api.orders.remove(row.id); toast("Eliminada", "success"); load(); }
    catch (e) { toast(e.message, "error"); }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Órdenes</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nueva</button>
  </div>

  <DataTable {rows} {columns} {loading} onEdit={openEdit} onDelete={remove} />
</div>

<Modal bind:open={showModal} title={editing ? "Editar Orden" : "Nueva Orden"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <div class="grid-2">
      <label>ID Orden <input bind:value={form.order_id} required disabled={!!editing} /></label>
      <label>Estado
        <select bind:value={form.status}>
          {#each STATUSES as s}<option value={s}>{s}</option>{/each}
        </select>
      </label>
      <label>Total ($) <input type="number" step="0.01" min="0" bind:value={form.total} /></label>
      {#if !editing}
        <label>Fecha <input type="datetime-local" bind:value={form.placed_at} /></label>
      {/if}
    </div>
    <label>Notas <input bind:value={form.notes} /></label>
    <label class="check"><input type="checkbox" bind:checked={form.fulfilled} /> Cumplida</label>
    <div class="form-actions">
      <button type="button" class="btn-ghost" onclick={() => showModal = false}>Cancelar</button>
      <button type="submit" class="btn-primary">Guardar</button>
    </div>
  </form>
</Modal>

<style>
  .page { display: flex; flex-direction: column; gap: 1.25rem; }
  .page-header { display: flex; justify-content: space-between; align-items: center; }
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  .form { display: flex; flex-direction: column; gap: 0.75rem; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; color: #94a3b8; }
  label.check { flex-direction: row; align-items: center; gap: 0.5rem; color: #e2e8f0; }
  input, select {
    background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
    padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box;
  }
  .form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:hover { background: #4338ca; }
  .btn-ghost { background: none; border: 1px solid #334155; color: #94a3b8; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
</style>
