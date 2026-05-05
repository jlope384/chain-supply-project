<script>
  let { rows = [], columns = [], onEdit, onDelete, loading = false } = $props();
</script>

<div class="table-wrap">
  {#if loading}
    <div class="loading">Cargando...</div>
  {:else if rows.length === 0}
    <div class="empty">Sin resultados</div>
  {:else}
    <table>
      <thead>
        <tr>
          {#each columns as col}
            <th>{col.label}</th>
          {/each}
          {#if onEdit || onDelete}
            <th>Acciones</th>
          {/if}
        </tr>
      </thead>
      <tbody>
        {#each rows as row}
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
            {#if onEdit || onDelete}
              <td class="actions">
                {#if onEdit}
                  <button class="btn-icon edit" onclick={() => onEdit(row)}>✏️</button>
                {/if}
                {#if onDelete}
                  <button class="btn-icon del" onclick={() => onDelete(row)}>🗑️</button>
                {/if}
              </td>
            {/if}
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .table-wrap {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #334155;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
  }
  th {
    background: #1e293b;
    color: #94a3b8;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
    border-bottom: 1px solid #334155;
  }
  td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid #1e293b;
    color: #e2e8f0;
    max-width: 240px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  tr:last-child td {
    border-bottom: none;
  }
  tr:hover td {
    background: #1e293b;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    white-space: nowrap;
  }
  .btn-icon {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.2rem;
    opacity: 0.7;
    transition: opacity 0.15s;
  }
  .btn-icon:hover { opacity: 1; }
  .loading, .empty {
    padding: 2rem;
    text-align: center;
    color: #64748b;
  }
</style>
