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

  const countLabels = {
    suppliers: "Proveedores",
    products: "Productos",
    warehouses: "Bodegas",
    orders: "Órdenes",
    carriers: "Transportistas",
    tags: "Tags",
  };
</script>

<div class="dashboard">
  <div class="page-top">
    <div>
      <h1 class="page-title">Dashboard</h1>
      <p class="page-sub">Resumen de operaciones</p>
    </div>
    <div class="conn" class:ok={backendOk === true} class:err={backendOk === false}>
      <span class="conn-dot"></span>
      <span class="conn-label">
        {backendOk === null ? "Conectando..." : backendOk ? "Backend activo" : "Sin conexión"}
      </span>
    </div>
  </div>

  {#if loading}
    <div class="skeleton-row">
      {#each Array(6) as _}
        <div class="skeleton-card"></div>
      {/each}
    </div>
    <div class="skeleton-grid">
      {#each Array(3) as _}
        <div class="skeleton-info"></div>
      {/each}
    </div>
  {:else}
    <div class="metrics-row">
      {#each Object.entries(counts) as [key, count]}
        <div class="metric-card">
          <span class="metric-num">{count}</span>
          <span class="metric-lbl">{countLabels[key] ?? key}</span>
        </div>
      {/each}
    </div>

    <div class="info-grid">
      {#if supplierStats}
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Proveedores</span>
            <span class="info-count">{supplierStats.total}</span>
          </div>
          <div class="info-rows">
            <div class="info-row">
              <span class="irow-k">Activos</span>
              <span class="irow-v ok">{supplierStats.active_count}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Rating promedio</span>
              <span class="irow-v">★ {supplierStats.avg_rating}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Países distintos</span>
              <span class="irow-v">{supplierStats.countries?.length ?? 0}</span>
            </div>
          </div>
        </div>
      {/if}

      {#if orderStats}
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Órdenes</span>
            <span class="info-count">{orderStats.total}</span>
          </div>
          <div class="info-rows">
            <div class="info-row">
              <span class="irow-k">Pendientes</span>
              <span class="irow-v warn">{orderStats.pending}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Enviadas</span>
              <span class="irow-v">{orderStats.shipped}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Entregadas</span>
              <span class="irow-v ok">{orderStats.delivered}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Devueltas</span>
              <span class="irow-v err">{orderStats.returned}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Ingresos totales</span>
              <span class="irow-v accent">
                ${Number(orderStats.revenue ?? 0).toLocaleString("es", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>
      {/if}

      {#if productStats}
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Productos</span>
            <span class="info-count">{productStats.total}</span>
          </div>
          <div class="info-rows">
            <div class="info-row">
              <span class="irow-k">En stock</span>
              <span class="irow-v ok">{productStats.in_stock_count}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Precio promedio</span>
              <span class="irow-v">${productStats.avg_price}</span>
            </div>
            <div class="info-row">
              <span class="irow-k">Categorías</span>
              <span class="irow-v">{productStats.categories?.length ?? 0}</span>
            </div>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .dashboard { display: flex; flex-direction: column; gap: 1.75rem; }

  /* ── Header ── */
  .page-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border-sub);
  }
  .page-title { margin: 0; font-size: 1.1rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
  .page-sub { margin: 2px 0 0; font-size: 0.78rem; color: var(--text-3); }

  .conn { display: flex; align-items: center; gap: 0.45rem; padding: 0.3rem 0.7rem; border-radius: 99px; border: 1px solid var(--border-sub); background: var(--card); }
  .conn-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--text-3); flex-shrink: 0; }
  .conn.ok .conn-dot { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .conn.err .conn-dot { background: var(--red); }
  .conn-label { font-size: 0.75rem; font-weight: 500; color: var(--text-2); white-space: nowrap; }

  /* ── Skeleton ── */
  .skeleton-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
  .skeleton-card { height: 76px; flex: 1; min-width: 100px; background: var(--card); border-radius: 6px; border: 1px solid var(--border-sub); animation: pulse 1.5s ease-in-out infinite; }
  .skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.75rem; margin-top: 0.25rem; }
  .skeleton-info { height: 160px; background: var(--card); border-radius: 6px; border: 1px solid var(--border-sub); animation: pulse 1.5s ease-in-out infinite; }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* ── Metrics ── */
  .metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.75rem;
  }
  .metric-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    padding: 1rem 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }
  .metric-num {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--cyan);
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .metric-lbl {
    font-size: 0.72rem;
    color: var(--text-3);
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  /* ── Info cards ── */
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 0.75rem;
  }
  .info-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    overflow: hidden;
  }
  .info-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-sub);
    background: rgba(255,255,255,0.015);
  }
  .info-title { font-size: 0.8rem; font-weight: 600; color: var(--text); }
  .info-count { font-size: 0.8rem; font-weight: 600; color: var(--text-3); font-variant-numeric: tabular-nums; }

  .info-rows { display: flex; flex-direction: column; }
  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .info-row:last-child { border-bottom: none; }
  .irow-k { font-size: 0.8rem; color: var(--text-3); }
  .irow-v { font-size: 0.8rem; color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }
  .irow-v.ok { color: var(--green); }
  .irow-v.warn { color: var(--amber); }
  .irow-v.err { color: var(--red); }
  .irow-v.accent { color: var(--cyan); }
</style>
