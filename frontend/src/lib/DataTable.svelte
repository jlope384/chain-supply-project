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

<div class="table-wrap">
  {#if searchable && rows.length > 0}
    <div class="search-bar">
      <Search size={14} class="si" />
      <input
        bind:value={query}
        placeholder="Buscar..."
        class="search-input"
      />
      {#if query}
        <button class="clear" onclick={() => query = ""}>✕</button>
      {/if}
    </div>
  {/if}

  <div class="table-scroll">
    {#if loading}
      <div class="empty-state">
        <div class="spinner"></div>
        <span>Cargando...</span>
      </div>
    {:else if rows.length === 0}
      <div class="empty-state">
        <span class="empty-icon">—</span>
        <span>Sin registros</span>
      </div>
    {:else if filtered().length === 0}
      <div class="empty-state">
        <span>Sin coincidencias para "<em>{query}</em>"</span>
      </div>
    {:else}
      <table>
        <thead>
          <tr>
            {#each columns as col}
              <th>{col.label}</th>
            {/each}
            {#if onEdit || onDelete || onExtra}
              <th class="th-act"></th>
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
                <td class="td-act">
                  {#if onExtra}
                    <button class="act-btn extra" title={extraTitle} onclick={() => onExtra(row)}>
                      <Archive size={13} />
                    </button>
                  {/if}
                  {#if onEdit}
                    <button class="act-btn edit" title="Editar" onclick={() => onEdit(row)}>
                      <Pencil size={13} />
                    </button>
                  {/if}
                  {#if onDelete}
                    <button class="act-btn del" title="Eliminar" onclick={() => onDelete(row)}>
                      <Trash2 size={13} />
                    </button>
                  {/if}
                </td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
      {#if query}
        <div class="count-bar">{filtered().length} de {rows.length}</div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .table-wrap {
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    overflow: hidden;
    background: var(--card);
  }

  .search-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--border-sub);
    background: rgba(255,255,255,0.02);
  }
  :global(.si) { color: var(--text-3); flex-shrink: 0; }
  .search-input {
    flex: 1;
    background: none !important;
    border: none !important;
    outline: none !important;
    color: var(--text) !important;
    font-size: 0.82rem !important;
    padding: 0 !important;
    width: auto !important;
    box-shadow: none !important;
  }
  .search-input::placeholder { color: var(--text-3); }
  .clear {
    background: none;
    border: none;
    color: var(--text-3);
    cursor: pointer;
    font-size: 0.72rem;
    padding: 0;
    line-height: 1;
    font-family: inherit;
  }
  .clear:hover { color: var(--text-2); }

  .table-scroll { overflow-x: auto; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }

  th {
    background: rgba(255,255,255,0.02);
    color: var(--text-3);
    padding: 0.55rem 0.875rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    border-bottom: 1px solid var(--border-sub);
  }
  .th-act { width: 1px; }

  td {
    padding: 0.55rem 0.875rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: var(--text-2);
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,0.02); color: var(--text); }

  .td-act {
    display: flex;
    gap: 0.25rem;
    justify-content: flex-end;
    padding-right: 0.6rem;
    white-space: nowrap;
  }

  .act-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 4px;
    border: 1px solid transparent;
    cursor: pointer;
    background: none;
    color: var(--text-3);
    transition: background 0.1s, color 0.1s, border-color 0.1s;
    font-family: inherit;
  }
  .act-btn:hover { color: var(--text); border-color: var(--border-sub); background: var(--hover); }
  .act-btn.edit:hover { color: var(--blue); border-color: rgba(96,165,250,0.2); background: var(--blue-dim); }
  .act-btn.del:hover  { color: var(--red);  border-color: rgba(248,113,113,0.2); background: var(--red-dim); }
  .act-btn.extra:hover { color: var(--green); border-color: rgba(74,222,128,0.2); background: var(--green-dim); }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 3rem;
    color: var(--text-3);
    font-size: 0.82rem;
  }
  .empty-icon { font-size: 1.5rem; }
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-sub);
    border-top-color: var(--cyan);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .count-bar {
    padding: 0.3rem 0.875rem;
    font-size: 0.72rem;
    color: var(--text-3);
    border-top: 1px solid var(--border-sub);
    background: rgba(255,255,255,0.015);
  }
</style>
