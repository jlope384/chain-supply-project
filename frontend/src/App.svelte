<script>
  import {
    LayoutDashboard, Factory, Package, Warehouse, ShoppingCart,
    Truck, Tag, Share2, BarChart3, FileUp, ChevronLeft, ChevronRight
  } from "lucide-svelte";

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
    { key: "dashboard",     label: "Dashboard",      icon: LayoutDashboard, component: Dashboard },
    { key: "suppliers",     label: "Proveedores",    icon: Factory,         component: Suppliers },
    { key: "products",      label: "Productos",      icon: Package,         component: Products },
    { key: "warehouses",    label: "Bodegas",        icon: Warehouse,       component: Warehouses },
    { key: "orders",        label: "Órdenes",        icon: ShoppingCart,    component: Orders },
    { key: "carriers",      label: "Transportistas", icon: Truck,           component: Carriers },
    { key: "tags",          label: "Tags",           icon: Tag,             component: Tags },
    { key: "relationships", label: "Relaciones",     icon: Share2,          component: Relationships },
    { key: "analytics",     label: "Analíticas",     icon: BarChart3,       component: Analytics },
    { key: "csv",           label: "Carga CSV",      icon: FileUp,          component: CsvUpload },
  ];

  let current = $state("dashboard");
  let collapsed = $state(false);

  let activeView = $derived(views.find((v) => v.key === current));
</script>

<div class="app" class:collapsed>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">
        <Share2 size={20} />
      </div>
      {#if !collapsed}
        <span class="brand-text">Supply Chain</span>
      {/if}
    </div>

    <nav>
      {#each views as view}
        {@const Icon = view.icon}
        <button
          class="nav-item"
          class:active={current === view.key}
          onclick={() => current = view.key}
          title={collapsed ? view.label : ""}
        >
          <span class="nav-icon"><Icon size={18} /></span>
          {#if !collapsed}<span class="nav-label">{view.label}</span>{/if}
        </button>
      {/each}
    </nav>

    <button class="collapse-btn" onclick={() => collapsed = !collapsed} title={collapsed ? "Expandir" : "Colapsar"}>
      {#if collapsed}
        <ChevronRight size={16} />
      {:else}
        <ChevronLeft size={16} />
      {/if}
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
    -webkit-font-smoothing: antialiased;
  }
  :global(input:focus, select:focus, textarea:focus) {
    outline: 2px solid #4f46e5;
    outline-offset: 0;
  }
  :global(.badge) { padding: 0.2rem 0.55rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
  :global(.badge.green)  { background: #14532d; color: #86efac; }
  :global(.badge.red)    { background: #7f1d1d; color: #fca5a5; }
  :global(.badge.yellow) { background: #713f12; color: #fde68a; }
  :global(.badge.blue)   { background: #1e3a5f; color: #93c5fd; }

  .app {
    display: grid;
    grid-template-columns: 220px 1fr;
    min-height: 100vh;
    transition: grid-template-columns 0.2s ease;
  }
  .app.collapsed { grid-template-columns: 60px 1fr; }

  /* ── Sidebar ── */
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

  .brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.1rem 1rem;
    border-bottom: 1px solid #334155;
    overflow: hidden;
  }
  .brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: #4f46e5;
    border-radius: 8px;
    color: #fff;
    flex-shrink: 0;
  }
  .brand-text {
    font-weight: 700;
    font-size: 0.95rem;
    color: #f1f5f9;
    white-space: nowrap;
  }

  nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1px;
    padding: 0.75rem 0.5rem;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.55rem 0.75rem;
    border-radius: 7px;
    border: none;
    background: none;
    color: #64748b;
    cursor: pointer;
    font-size: 0.875rem;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    transition: background 0.12s, color 0.12s;
    width: 100%;
  }
  .nav-item:hover { background: #273548; color: #cbd5e1; }
  .nav-item.active { background: #312e81; color: #a5b4fc; }
  .nav-item.active .nav-icon { color: #818cf8; }

  .nav-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: inherit;
  }
  .nav-label { overflow: hidden; text-overflow: ellipsis; }

  .collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0.75rem 0.5rem;
    padding: 0.5rem;
    background: none;
    border: 1px solid #334155;
    color: #475569;
    border-radius: 7px;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
  }
  .collapse-btn:hover { background: #334155; color: #94a3b8; }

  /* ── Content ── */
  .content { overflow-y: auto; min-height: 100vh; }
  .content-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 2rem;
  }
</style>
