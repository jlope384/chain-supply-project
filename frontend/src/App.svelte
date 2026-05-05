<script>
  import Toast from "./lib/Toast.svelte";
  import Dashboard from "./views/Dashboard.svelte";
  import Suppliers from "./views/Suppliers.svelte";
  import Products from "./views/Products.svelte";
  import Warehouses from "./views/Warehouses.svelte";
  import Orders from "./views/Orders.svelte";
  import Carriers from "./views/Carriers.svelte";
  import Tags from "./views/Tags.svelte";
  import Relationships from "./views/Relationships.svelte";
  import Analytics from "./views/Analytics.svelte";
  import CsvUpload from "./views/CsvUpload.svelte";

  const views = [
    { key: "dashboard", label: "Dashboard", icon: "🏠", component: Dashboard },
    { key: "suppliers", label: "Proveedores", icon: "🏭", component: Suppliers },
    { key: "products", label: "Productos", icon: "📦", component: Products },
    { key: "warehouses", label: "Bodegas", icon: "🏗️", component: Warehouses },
    { key: "orders", label: "Órdenes", icon: "🛒", component: Orders },
    { key: "carriers", label: "Transportistas", icon: "🚚", component: Carriers },
    { key: "tags", label: "Tags", icon: "🏷️", component: Tags },
    { key: "relationships", label: "Relaciones", icon: "🔗", component: Relationships },
    { key: "analytics", label: "Analíticas", icon: "📊", component: Analytics },
    { key: "csv", label: "Carga CSV", icon: "📁", component: CsvUpload },
  ];

  let current = $state("dashboard");
  let sidebarOpen = $state(true);

  let activeView = $derived(views.find((v) => v.key === current));
</script>

<div class="app" class:sidebar-collapsed={!sidebarOpen}>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="brand-icon">⛓️</span>
      {#if sidebarOpen}<span class="brand-text">Supply Chain</span>{/if}
    </div>

    <nav>
      {#each views as view}
        <button
          class="nav-item"
          class:active={current === view.key}
          onclick={() => current = view.key}
          title={view.label}
        >
          <span class="nav-icon">{view.icon}</span>
          {#if sidebarOpen}<span class="nav-label">{view.label}</span>{/if}
        </button>
      {/each}
    </nav>

    <button class="toggle-btn" onclick={() => sidebarOpen = !sidebarOpen}>
      {sidebarOpen ? "◀" : "▶"}
    </button>
  </aside>

  <main class="content">
    <div class="content-inner">
      {#if activeView}
        <activeView.component />
      {/if}
    </div>
  </main>
</div>

<Toast />

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
  }
  :global(input:focus, select:focus) {
    outline: 2px solid #4f46e5;
    outline-offset: 0;
  }

  .app {
    display: grid;
    grid-template-columns: 220px 1fr;
    min-height: 100vh;
    transition: grid-template-columns 0.2s ease;
  }
  .app.sidebar-collapsed {
    grid-template-columns: 56px 1fr;
  }

  .sidebar {
    background: #1e293b;
    border-right: 1px solid #334155;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow: hidden;
  }

  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.25rem 1rem;
    border-bottom: 1px solid #334155;
    font-weight: 700;
    font-size: 1rem;
    color: #f1f5f9;
    white-space: nowrap;
    overflow: hidden;
  }
  .brand-icon { font-size: 1.3rem; flex-shrink: 0; }
  .brand-text { overflow: hidden; }

  nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 0.75rem 0.5rem;
    overflow-y: auto;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.75rem;
    border-radius: 8px;
    border: none;
    background: none;
    color: #94a3b8;
    cursor: pointer;
    font-size: 0.9rem;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    transition: background 0.15s, color 0.15s;
    width: 100%;
  }
  .nav-item:hover { background: #334155; color: #e2e8f0; }
  .nav-item.active { background: #4f46e5; color: #fff; }
  .nav-icon { font-size: 1.1rem; flex-shrink: 0; }
  .nav-label { overflow: hidden; text-overflow: ellipsis; }

  .toggle-btn {
    margin: 0.75rem 0.5rem;
    padding: 0.5rem;
    background: none;
    border: 1px solid #334155;
    color: #64748b;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.75rem;
    width: calc(100% - 1rem);
  }
  .toggle-btn:hover { background: #334155; color: #94a3b8; }

  .content {
    overflow-y: auto;
    min-height: 100vh;
  }
  .content-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
</style>
