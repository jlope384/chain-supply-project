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

  function defaultForm() {
    return { name: "", sku: "", price: 0, weight: 0, category: "", in_stock: true, description: "" };
  }

  const columns = [
    { key: "sku", label: "SKU" },
    { key: "name", label: "Nombre" },
    { key: "category", label: "Categoría" },
    { key: "price", label: "Precio", render: (v) => `$${Number(v ?? 0).toFixed(2)}` },
    { key: "weight", label: "Peso (kg)" },
    { key: "in_stock", label: "En Stock", render: (v) => v
        ? '<span class="badge green">En stock</span>'
        : '<span class="badge red">Sin stock</span>' },
  ];

  async function load() {
    loading = true;
    try { rows = await api.products.list(); }
    catch (e) { toast(e.message, "error"); }
    finally { loading = false; }
  }

  onMount(load);

  function openCreate() {
    editing = null;
    form = defaultForm();
    showModal = true;
  }

  function openEdit(row) {
    editing = row;
    form = { name: row.name, sku: row.sku, price: row.price, weight: row.weight, category: row.category, in_stock: row.in_stock, description: row.description || "" };
    showModal = true;
  }

  async function save() {
    const data = { ...form, price: Number(form.price), weight: Number(form.weight) };
    try {
      if (editing) {
        await api.products.update(editing.id, data);
        toast("Producto actualizado", "success");
      } else {
        await api.products.create(data);
        toast("Producto creado", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar producto "${row.name}"?`)) return;
    try {
      await api.products.remove(row.id);
      toast("Eliminado", "success");
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Productos</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nuevo</button>
  </div>

  <DataTable {rows} {columns} {loading} onEdit={openEdit} onDelete={remove} />
</div>

<Modal bind:open={showModal} title={editing ? "Editar Producto" : "Nuevo Producto"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <div class="grid-2">
      <label>Nombre <input bind:value={form.name} required /></label>
      <label>SKU <input bind:value={form.sku} required /></label>
      <label>Precio ($) <input type="number" step="0.01" min="0" bind:value={form.price} /></label>
      <label>Peso (kg) <input type="number" step="0.01" min="0" bind:value={form.weight} /></label>
    </div>
    <label>Categoría <input bind:value={form.category} required /></label>
    <label>Descripción <input bind:value={form.description} /></label>
    <label class="check">
      <input type="checkbox" bind:checked={form.in_stock} />
      En Stock
    </label>
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
  input {
    background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
    padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box;
  }
  .form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
  .btn-primary {
    background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem;
    border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600;
  }
  .btn-primary:hover { background: #4338ca; }
  .btn-ghost {
    background: none; border: 1px solid #334155; color: #94a3b8;
    padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem;
  }
</style>
