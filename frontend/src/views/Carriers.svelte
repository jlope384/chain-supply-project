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
    return { name: "", modes: "", active: true, rating: 0, regions: "", onboarded_at: "" };
  }

  const columns = [
    { key: "name", label: "Nombre" },
    { key: "modes", label: "Modos", render: (v) => Array.isArray(v) ? v.join(", ") : v },
    { key: "rating", label: "Rating" },
    { key: "active", label: "Activo", render: (v) => v ? "✅" : "❌" },
    { key: "regions", label: "Regiones", render: (v) => Array.isArray(v) ? v.join(", ") : v },
    { key: "onboarded_at", label: "Incorporado" },
  ];

  async function load() {
    loading = true;
    try { rows = await api.carriers.list(); }
    catch (e) { toast(e.message, "error"); }
    finally { loading = false; }
  }

  onMount(load);

  function openCreate() { editing = null; form = defaultForm(); showModal = true; }

  function openEdit(row) {
    editing = row;
    form = {
      name: row.name, modes: Array.isArray(row.modes) ? row.modes.join(", ") : "",
      active: row.active, rating: row.rating,
      regions: Array.isArray(row.regions) ? row.regions.join(", ") : "",
      onboarded_at: row.onboarded_at || "",
    };
    showModal = true;
  }

  async function save() {
    const data = {
      ...form,
      rating: Number(form.rating),
      modes: form.modes ? form.modes.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean) : [],
      regions: form.regions ? form.regions.split(",").map((s) => s.trim()).filter(Boolean) : [],
      onboarded_at: form.onboarded_at || undefined,
    };
    try {
      if (editing) {
        await api.carriers.update(editing.id, data);
        toast("Transportista actualizado", "success");
      } else {
        await api.carriers.create(data);
        toast("Transportista creado", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar "${row.name}"?`)) return;
    try { await api.carriers.remove(row.id); toast("Eliminado", "success"); load(); }
    catch (e) { toast(e.message, "error"); }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Transportistas</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nuevo</button>
  </div>
  <DataTable {rows} {columns} {loading} onEdit={openEdit} onDelete={remove} />
</div>

<Modal bind:open={showModal} title={editing ? "Editar Transportista" : "Nuevo Transportista"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <label>Nombre <input bind:value={form.name} required /></label>
    <label>Modos (coma-separados: AIR, SEA, GROUND) <input bind:value={form.modes} placeholder="AIR, SEA" /></label>
    <div class="grid-2">
      <label>Rating <input type="number" step="0.1" min="0" max="5" bind:value={form.rating} /></label>
      <label>Incorporado <input type="date" bind:value={form.onboarded_at} /></label>
    </div>
    <label>Regiones (coma-separadas) <input bind:value={form.regions} placeholder="LATAM, NA..." /></label>
    <label class="check"><input type="checkbox" bind:checked={form.active} /> Activo</label>
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
  input { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }
  .form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:hover { background: #4338ca; }
  .btn-ghost { background: none; border: 1px solid #334155; color: #94a3b8; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
</style>
