<script>
  import { Pencil, Trash2, Search, Archive } from "lucide-svelte";

  let {
    rows = [],
    columns = [],
    onEdit,
    onDelete,
    onExtra,
    extraIcon = null,
    extraTitle = "",
    loading = false,
    searchable = true,
  } = $props();

  let query = $state("");

  let filtered = $derived(() => {
    if (!query.trim()) return rows;
    const q = query.toLowerCase();
    return rows.filter((row) =>
      columns.some((col) => {
        const v = row[col.key];
        if (v == null) return false;
        if (Array.isArray(v)) return v.join(" ").toLowerCase().includes(q);
        return String(v).toLowerCase().includes(q);
      })
    );
  });
</script>

<div class="table-container">
  {#if searchable && rows.length > 0}
    <div class="search-bar">
      <Search size={15} class="search-icon" />
      <input
        bind:value={query}
        placeholder="Buscar..."
        class="search-input"
      />
      {#if query}
        <button class="clear-btn" onclick={() => query = ""}>✕</button>
      {/if}
    </div>
  {/if}

  <div class="table-wrap">
    {#if loading}
      <div class="state-msg">Cargando...</div>
    {:else if rows.length === 0}
      <div class="state-msg">Sin resultados</div>
    {:else if filtered().length === 0}
      <div class="state-msg">Sin coincidencias para "{query}"</div>
    {:else}
      <table>
        <thead>
          <tr>
            {#each columns as col}
              <th>{col.label}</th>
            {/each}
            {#if onEdit || onDelete || onExtra}
              <th class="th-actions">Acciones</th>
            {/if}
          </tr>
        </thead>
        <tbody>
          {#each filtered() as row}
            <tr>
              {#each columns as col}
                <td>
                  {#if col.render}
                    {@html col.render(row[col.key], row)}
                  {:else}
                    {row[col.key] ?? "—"}
                  {/if}
                </td>
              {/each}
              {#if onEdit || onDelete || onExtra}
                <td class="td-actions">
                  {#if onExtra}
                    <button
                      class="btn-action extra"
                      title={extraTitle}
                      onclick={() => onExtra(row)}
                    >
                      <Archive size={14} />
                    </button>
                  {/if}
                  {#if onEdit}
                    <button
                      class="btn-action edit"
                      title="Editar"
                      onclick={() => onEdit(row)}
                    >
                      <Pencil size={14} />
                    </button>
                  {/if}
                  {#if onDelete}
                    <button
                      class="btn-action del"
                      title="Eliminar"
                      onclick={() => onDelete(row)}
                    >
                      <Trash2 size={14} />
                    </button>
                  {/if}
                </td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
      {#if query}
        <div class="count-bar">
          {filtered().length} de {rows.length} resultados
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .table-container { display: flex; flex-direction: column; gap: 0; }

  .search-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 0.6rem 0.875rem;
  }
  :global(.search-icon) { color: #475569; flex-shrink: 0; }
  .search-input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: #e2e8f0;
    font-size: 0.875rem;
  }
  .search-input::placeholder { color: #475569; }
  .clear-btn {
    background: none;
    border: none;
    color: #475569;
    cursor: pointer;
    font-size: 0.75rem;
    padding: 0;
    line-height: 1;
  }
  .clear-btn:hover { color: #94a3b8; }

  .table-wrap {
    overflow-x: auto;
    border: 1px solid #334155;
    border-radius: 0 0 8px 8px;
  }
  /* when no search bar, round all corners */
  .table-container:not(:has(.search-bar)) .table-wrap {
    border-radius: 8px;
  }

  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }

  th {
    background: #1e293b;
    color: #64748b;
    padding: 0.65rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
    border-bottom: 1px solid #334155;
  }
  .th-actions { text-align: right; padding-right: 1rem; }

  td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #1e293b;
    color: #cbd5e1;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #1a2740; }

  .td-actions {
    display: flex;
    gap: 0.35rem;
    justify-content: flex-end;
    padding-right: 0.75rem;
    white-space: nowrap;
  }

  .btn-action {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: background 0.12s, border-color 0.12s, color 0.12s;
  }
  .btn-action.edit {
    background: #1e3a5f;
    color: #60a5fa;
    border-color: #1e40af44;
  }
  .btn-action.edit:hover { background: #1e40af; color: #bfdbfe; }
  .btn-action.del {
    background: #3f1f1f;
    color: #f87171;
    border-color: #7f1d1d44;
  }
  .btn-action.del:hover { background: #7f1d1d; color: #fecaca; }
  .btn-action.extra {
    background: #1a3a2a;
    color: #4ade80;
    border-color: #14532d44;
  }
  .btn-action.extra:hover { background: #14532d; color: #bbf7d0; }

  .state-msg {
    padding: 2.5rem;
    text-align: center;
    color: #475569;
    font-size: 0.9rem;
  }
  .count-bar {
    padding: 0.4rem 1rem;
    font-size: 0.75rem;
    color: #475569;
    border-top: 1px solid #1e293b;
    background: #0f172a;
    border-radius: 0 0 8px 8px;
  }
</style>
