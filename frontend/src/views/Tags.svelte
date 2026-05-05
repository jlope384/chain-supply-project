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
    return { name: "", category: "", color_hex: "#6366f1", global_tag: true };
  }

  const columns = [
    { key: "name", label: "Nombre" },
    { key: "category", label: "Categoría" },
    {
      key: "color_hex", label: "Color",
      render: (v) => `<span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:${v};vertical-align:middle;margin-right:6px;"></span>${v}`
    },
    { key: "global", label: "Global", render: (v) => v ? "✅" : "❌" },
    { key: "created_at", label: "Creado" },
  ];

  async function load() {
    loading = true;
    try { rows = await api.tags.list(); }
    catch (e) { toast(e.message, "error"); }
    finally { loading = false; }
  }

  onMount(load);

  function openCreate() { editing = null; form = defaultForm(); showModal = true; }

  function openEdit(row) {
    editing = row;
    form = { name: row.name, category: row.category, color_hex: row.color_hex || "#6366f1", global_tag: row.global ?? true };
    showModal = true;
  }

  async function save() {
    try {
      if (editing) {
        await api.tags.update(editing.id, { category: form.category, color_hex: form.color_hex, global_tag: form.global_tag });
        toast("Tag actualizado", "success");
      } else {
        await api.tags.create(form);
        toast("Tag creado", "success");
      }
      showModal = false;
      load();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function remove(row) {
    if (!confirm(`¿Eliminar tag "${row.name}"?`)) return;
    try { await api.tags.remove(row.id); toast("Eliminado", "success"); load(); }
    catch (e) { toast(e.message, "error"); }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Tags</h1>
    <button class="btn-primary" onclick={openCreate}>+ Nuevo</button>
  </div>
  <DataTable {rows} {columns} {loading} onEdit={openEdit} onDelete={remove} />
</div>

<Modal bind:open={showModal} title={editing ? "Editar Tag" : "Nuevo Tag"}>
  <form onsubmit={(e) => { e.preventDefault(); save(); }} class="form">
    <label>Nombre <input bind:value={form.name} required disabled={!!editing} /></label>
    <label>Categoría <input bind:value={form.category} required /></label>
    <label>Color
      <div class="color-row">
        <input type="color" bind:value={form.color_hex} class="color-pick" />
        <input bind:value={form.color_hex} class="color-text" placeholder="#6366f1" />
      </div>
    </label>
    <label class="check"><input type="checkbox" bind:checked={form.global_tag} /> Global</label>
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
  input { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }
  .color-row { display: flex; gap: 0.5rem; align-items: center; }
  .color-pick { width: 44px; height: 38px; padding: 2px; cursor: pointer; flex-shrink: 0; }
  .color-text { flex: 1; }
  .form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:hover { background: #4338ca; }
  .btn-ghost { background: none; border: 1px solid #334155; color: #94a3b8; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
</style>
