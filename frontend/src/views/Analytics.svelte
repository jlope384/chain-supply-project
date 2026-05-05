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

  // Shortest path
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
  <h1>Analíticas del Grafo</h1>

  <div class="queries">
    {#each queries as q}
      <div class="query-card">
        <div class="query-header">
          <span>{q.label}</span>
          <button class="btn-run" onclick={() => run(q)} disabled={loading[q.key]}>
            {loading[q.key] ? "..." : "Ejecutar"}
          </button>
        </div>

        {#if results[q.key] !== undefined}
          {#if Array.isArray(results[q.key])}
            {#if results[q.key].length === 0}
              <p class="muted">Sin resultados</p>
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

  <div class="path-section">
    <h2>Camino más corto</h2>
    <div class="path-form">
      <input bind:value={fromId} placeholder="elementId del nodo origen" />
      <input bind:value={toId} placeholder="elementId del nodo destino" />
      <button class="btn-primary" onclick={findPath} disabled={pathLoading}>
        {pathLoading ? "Buscando..." : "Buscar"}
      </button>
    </div>
    {#if pathResult}
      <div class="path-result">
        <strong>Saltos: {pathResult.hops}</strong>
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
  .page { display: flex; flex-direction: column; gap: 1.5rem; }
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  h2 { margin: 0 0 0.75rem; font-size: 1.1rem; color: #f1f5f9; }
  .queries { display: flex; flex-direction: column; gap: 1rem; }
  .query-card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; overflow: hidden; }
  .query-header { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.25rem; border-bottom: 1px solid #334155; }
  .query-header span { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
  .btn-run {
    background: #4f46e5; color: #fff; border: none; padding: 0.4rem 1rem;
    border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
  }
  .btn-run:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-run:hover:not(:disabled) { background: #4338ca; }
  .muted { color: #64748b; padding: 0.75rem 1.25rem; margin: 0; }
  .result-table { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th { background: #0f172a; color: #64748b; padding: 0.5rem 0.75rem; text-align: left; font-weight: 600; }
  td { padding: 0.45rem 0.75rem; border-top: 1px solid #1e293b; color: #e2e8f0; }
  tr:hover td { background: #0f172a; }
  .json { padding: 0.75rem 1.25rem; margin: 0; color: #a5b4fc; font-size: 0.8rem; white-space: pre-wrap; word-break: break-all; }
  .path-section { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.25rem; }
  .path-form { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .path-form input { flex: 1; min-width: 200px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.85rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.55rem 1.25rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  .btn-primary:disabled { opacity: 0.5; }
  .path-result { background: #0f172a; border-radius: 8px; padding: 1rem; }
  .path-result strong { color: #94a3b8; font-size: 0.85rem; }
  .path-nodes { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem; margin-top: 0.5rem; }
  .node { background: #4f46e5; color: #fff; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.82rem; }
  .arrow { color: #64748b; }
</style>
