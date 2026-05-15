<script>
  import { api } from "../lib/api.js";
  import { toast } from "../lib/toast.svelte.js";

  const queries = [
    { key: "topSuppliers", label: "Top Proveedores por Productos", fn: () => api.graph.topSuppliers() },
    { key: "warehouseInventory", label: "Inventario por Bodega", fn: () => api.graph.warehouseInventory() },
    { key: "carrierPerformance", label: "Rendimiento de Transportistas", fn: () => api.graph.carrierPerformance() },
    { key: "returnAnalysis", label: "Análisis de Devoluciones", fn: () => api.graph.returnAnalysis() },
    { key: "supplyChainPaths", label: "Rutas de Cadena de Suministro", fn: () => api.graph.supplyChainPaths() },
    { key: "taggedProducts", label: "Tags con más Productos", fn: () => api.graph.taggedProducts() },
    { key: "pagerank", label: "PageRank (GDS)", fn: () => api.graph.pagerank() },
  ];

  let results = $state({});
  let loading = $state({});

  async function run(q) {
    loading[q.key] = true;
    try {
      results[q.key] = await q.fn();
    } catch (e) {
      toast(e.message, "error");
      results[q.key] = [];
    } finally {
      loading[q.key] = false;
    }
  }

  let fromId = $state("");
  let toId = $state("");
  let pathResult = $state(null);
  let pathLoading = $state(false);

  async function findPath() {
    if (!fromId || !toId) { toast("Ingresa ambos IDs", "error"); return; }
    pathLoading = true;
    try {
      pathResult = await api.graph.shortestPath(fromId, toId);
    } catch (e) {
      toast(e.message, "error");
      pathResult = null;
    } finally {
      pathLoading = false;
    }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Analíticas</h1>
  </div>

  <div class="queries">
    {#each queries as q}
      <div class="query-card">
        <div class="query-header">
          <span class="query-label">{q.label}</span>
          <button class="btn-run" onclick={() => run(q)} disabled={loading[q.key]}>
            {loading[q.key] ? "···" : "Ejecutar"}
          </button>
        </div>

        {#if results[q.key] !== undefined}
          {#if Array.isArray(results[q.key])}
            {#if results[q.key].length === 0}
              <p class="empty">Sin resultados</p>
            {:else}
              <div class="result-table">
                <table>
                  <thead>
                    <tr>
                      {#each Object.keys(results[q.key][0]) as col}
                        <th>{col}</th>
                      {/each}
                    </tr>
                  </thead>
                  <tbody>
                    {#each results[q.key] as row}
                      <tr>
                        {#each Object.values(row) as val}
                          <td>{Array.isArray(val) ? val.join(", ") : (val ?? "—")}</td>
                        {/each}
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}
          {:else}
            <pre class="json">{JSON.stringify(results[q.key], null, 2)}</pre>
          {/if}
        {/if}
      </div>
    {/each}
  </div>

  <div class="path-card">
    <div class="path-header">Camino más corto</div>
    <div class="path-form">
      <input bind:value={fromId} placeholder="elementId del nodo origen" />
      <input bind:value={toId} placeholder="elementId del nodo destino" />
      <button class="btn-primary" onclick={findPath} disabled={pathLoading}>
        {pathLoading ? "Buscando..." : "Buscar"}
      </button>
    </div>
    {#if pathResult}
      <div class="path-result">
        <span class="hops">{pathResult.hops} saltos</span>
        <div class="path-nodes">
          {#each pathResult.path as node, i}
            <span class="node">{node}</span>
            {#if i < pathResult.path.length - 1}<span class="arrow">→</span>{/if}
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.25rem; }

  .queries { display: flex; flex-direction: column; gap: 0.6rem; }

  .query-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    overflow: hidden;
  }
  .query-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 1rem;
    border-bottom: 1px solid transparent;
    gap: 1rem;
  }
  .query-card:has(.result-table) .query-header,
  .query-card:has(.json) .query-header,
  .query-card:has(.empty) .query-header {
    border-bottom-color: var(--border-sub);
  }
  .query-label { font-size: 0.82rem; font-weight: 500; color: var(--text-2); }

  .btn-run {
    background: var(--hover);
    color: var(--text-2);
    border: 1px solid var(--border-sub);
    padding: 0.28rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
    font-family: inherit;
    transition: background 0.1s, color 0.1s, border-color 0.1s;
    flex-shrink: 0;
  }
  .btn-run:hover:not(:disabled) {
    background: var(--cyan-dim);
    color: var(--cyan);
    border-color: var(--cyan-border);
  }
  .btn-run:disabled { opacity: 0.4; cursor: not-allowed; }

  .empty { color: var(--text-3); padding: 0.75rem 1rem; margin: 0; font-size: 0.82rem; }

  .result-table { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  th {
    background: rgba(255,255,255,0.02);
    color: var(--text-3);
    padding: 0.45rem 0.875rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border-sub);
  }
  td {
    padding: 0.4rem 0.875rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: var(--text-2);
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,0.02); color: var(--text); }

  .json {
    padding: 0.75rem 1rem;
    margin: 0;
    color: var(--cyan);
    font-size: 0.75rem;
    white-space: pre-wrap;
    word-break: break-all;
    opacity: 0.8;
  }

  /* ── Shortest path ── */
  .path-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    overflow: hidden;
  }
  .path-header {
    padding: 0.65rem 1rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
    border-bottom: 1px solid var(--border-sub);
    background: rgba(255,255,255,0.02);
  }
  .path-form {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    align-items: flex-end;
    padding: 1rem;
  }
  .path-form input { flex: 1; min-width: 180px; }
  .path-result {
    margin: 0 1rem 1rem;
    background: var(--hover);
    border-radius: 5px;
    padding: 0.75rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .hops { font-size: 0.75rem; color: var(--text-3); font-weight: 500; }
  .path-nodes { display: flex; flex-wrap: wrap; align-items: center; gap: 0.3rem; }
  .node {
    background: var(--cyan-dim);
    color: var(--cyan);
    border: 1px solid var(--cyan-border);
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  .arrow { color: var(--text-3); font-size: 0.75rem; }
</style>
