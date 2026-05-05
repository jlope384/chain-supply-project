<script>
  import { api } from "../lib/api.js";
  import { onMount } from "svelte";

  let counts = $state({});
  let supplierStats = $state(null);
  let orderStats = $state(null);
  let productStats = $state(null);
  let loading = $state(true);
  let backendOk = $state(null);

  onMount(async () => {
    try {
      await api.health();
      backendOk = true;
    } catch {
      backendOk = false;
    }

    try {
      [counts, supplierStats, orderStats, productStats] = await Promise.all([
        api.graph.counts(),
        api.suppliers.stats(),
        api.orders.stats(),
        api.products.stats(),
      ]);
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="dashboard">
  <div class="page-header">
    <h1>Dashboard</h1>
    <span class="status-badge" class:ok={backendOk === true} class:err={backendOk === false}>
      {backendOk === null ? "Conectando..." : backendOk ? "Backend OK" : "Backend sin conexión"}
    </span>
  </div>

  {#if loading}
    <p class="muted">Cargando estadísticas...</p>
  {:else}
    <section class="stats-grid">
      {#each Object.entries(counts) as [label, count]}
        <div class="stat-card">
          <div class="stat-number">{count}</div>
          <div class="stat-label">{label}</div>
        </div>
      {/each}
    </section>

    <div class="grid-2">
      {#if supplierStats}
        <div class="info-card">
          <h3>Proveedores</h3>
          <dl>
            <dt>Total</dt><dd>{supplierStats.total}</dd>
            <dt>Activos</dt><dd>{supplierStats.active_count}</dd>
            <dt>Rating promedio</dt><dd>{supplierStats.avg_rating}</dd>
            <dt>Países</dt><dd>{supplierStats.countries?.length ?? 0}</dd>
          </dl>
        </div>
      {/if}

      {#if orderStats}
        <div class="info-card">
          <h3>Órdenes</h3>
          <dl>
            <dt>Total</dt><dd>{orderStats.total}</dd>
            <dt>Pendientes</dt><dd class="warn">{orderStats.pending}</dd>
            <dt>Enviadas</dt><dd>{orderStats.shipped}</dd>
            <dt>Entregadas</dt><dd class="ok">{orderStats.delivered}</dd>
            <dt>Devueltas</dt><dd class="err">{orderStats.returned}</dd>
            <dt>Ingresos totales</dt><dd>${Number(orderStats.revenue ?? 0).toLocaleString("es", {minimumFractionDigits: 2})}</dd>
          </dl>
        </div>
      {/if}

      {#if productStats}
        <div class="info-card">
          <h3>Productos</h3>
          <dl>
            <dt>Total</dt><dd>{productStats.total}</dd>
            <dt>En stock</dt><dd class="ok">{productStats.in_stock_count}</dd>
            <dt>Precio promedio</dt><dd>${productStats.avg_price}</dd>
            <dt>Categorías</dt><dd>{productStats.categories?.length ?? 0}</dd>
          </dl>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .dashboard { display: flex; flex-direction: column; gap: 1.5rem; }
  .page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
  }
  .status-badge.ok { background: #14532d; color: #86efac; border-color: #166534; }
  .status-badge.err { background: #7f1d1d; color: #fca5a5; border-color: #991b1b; }
  .muted { color: #64748b; }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
  }
  .stat-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
  }
  .stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #818cf8;
  }
  .stat-label {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }
  .info-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1.25rem;
  }
  h3 { margin: 0 0 1rem; color: #f1f5f9; font-size: 1rem; }
  dl { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; margin: 0; }
  dt { color: #64748b; font-size: 0.85rem; }
  dd { margin: 0; color: #e2e8f0; font-size: 0.85rem; font-weight: 600; text-align: right; }
  dd.ok { color: #86efac; }
  dd.warn { color: #fde68a; }
  dd.err { color: #fca5a5; }
</style>
