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
    return { name: "", country: "", active: true, rating: 0, certifications: "", founded_at: "" };
  }

  const columns = [
    { key: "name", label: "Nombre" },
    { key: "country", label: "País" },
    { key: "rating", label: "Rating" },
    { key: "active", label: "Activo", render: (v) => v ? "✅" : "❌" },
    { key: "founded_at", label: "Fundado" },
    { key: "certifications", label: "Certificaciones", render: (v) => Array.isArray(v) ? v.join(", ") : v },
  ];

  async function load() {
    loading = true;
    try { rows = await api.suppliers.list(); }
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
    form = {
      name: row.name,
      country: row.country,
      active: row.active,
      rating: row.rating,
      certifications: Array.isArray(row.certifications) ? row.certifications.join(", ") : "",
      founded_at: row.founded_at || "",
    };
    showModal = true;
  }

  async function save() {
    const data = {
      ...form,
      rating: Number(form.rating),
      certifications: form.certifications ? form.certifications.split(",").map((s) => s.trim()).filter(Boolean) : [],
      founded_at: form.founded_at || undefined,
    };
    try {
      if (editing) {
        await api.suppliers.update(editing.id, data);
        toast("Proveedor actualizado", "success");
      } else {
        await api.suppliers.create(data);
        toast("Proveedor creado", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar proveedor "${row.name}"?`)) return;
    try {
      await api.suppliers.remove(row.id);
      toast("Eliminado", "success");
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Proveedores</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nuevo</button>
  </div>

  <DataTable {rows} {columns} {loading} onEdit={openEdit} onDelete={remove} />
</div>

<Modal bind:open={showModal} title={editing ? "Editar Proveedor" : "Nuevo Proveedor"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <label>Nombre <input bind:value={form.name} required /></label>
    <label>País <input bind:value={form.country} required /></label>
    <label>Rating <input type="number" step="0.1" min="0" max="5" bind:value={form.rating} /></label>
    <label>Fundado
      <input type="date" bind:value={form.founded_at} />
    </label>
    <label>Certificaciones (coma-separadas)
      <input bind:value={form.certifications} placeholder="ISO9001, CE..." />
    </label>
    <label class="check">
      <input type="checkbox" bind:checked={form.active} />
      Activo
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
  label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; color: #94a3b8; }
  label.check { flex-direction: row; align-items: center; gap: 0.5rem; color: #e2e8f0; }
  input[type="text"], input:not([type="checkbox"]):not([type="date"]):not([type="number"]) {
    background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
    padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem;
  }
  input[type="date"], input[type="number"] {
    background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
    padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem;
  }
  input { width: 100%; box-sizing: border-box; }
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
  .btn-ghost:hover { background: #1e293b; }
</style>
