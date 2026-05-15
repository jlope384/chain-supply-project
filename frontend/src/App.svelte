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
      <div class="brand-mark">
        <Share2 size={14} />
      </div>
      {#if !collapsed}
        <div class="brand-name">
          <span class="brand-top">Supply</span>
          <span class="brand-bottom">Chain</span>
        </div>
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
          <span class="nav-icon"><Icon size={15} /></span>
          {#if !collapsed}<span class="nav-label">{view.label}</span>{/if}
        </button>
      {/each}
    </nav>

    <div class="sidebar-footer">
      <button
        class="collapse-btn"
        onclick={() => collapsed = !collapsed}
        title={collapsed ? "Expandir" : "Colapsar"}
      >
        {#if collapsed}<ChevronRight size={13} />{:else}<ChevronLeft size={13} />{/if}
      </button>
    </div>
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
  /* ── Reset & tokens ── */
  :global(*, *::before, *::after) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    font-size: 14px;
    line-height: 1.6;
  }

  /* ── Global form overrides ── */
  :global(input:not([type=checkbox]):not([type=radio]):not(.search-input)),
  :global(select),
  :global(textarea) {
    background: var(--surface) !important;
    border: 1px solid var(--border-sub) !important;
    color: var(--text) !important;
    padding: 0.45rem 0.7rem !important;
    border-radius: 5px !important;
    font-size: 0.875rem !important;
    font-family: inherit !important;
    width: 100% !important;
    transition: border-color 0.15s !important;
  }
  :global(input:not([type=checkbox]):not([type=radio]):not(.search-input):focus),
  :global(select:focus),
  :global(textarea:focus) {
    outline: none !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-dim) !important;
  }
  :global(label) {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: var(--text-2) !important;
    letter-spacing: 0.01em !important;
  }
  :global(label.check) {
    flex-direction: row !important;
    align-items: center !important;
    color: var(--text) !important;
  }

  /* ── Global button overrides ── */
  :global(.btn-primary) {
    background: var(--cyan) !important;
    color: #000 !important;
    border: none !important;
    padding: 0.45rem 1rem !important;
    border-radius: 5px !important;
    cursor: pointer !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    font-family: inherit !important;
    transition: opacity 0.15s !important;
    letter-spacing: 0.01em !important;
  }
  :global(.btn-primary:hover) { opacity: 0.88 !important; }
  :global(.btn-primary:disabled) { opacity: 0.4 !important; cursor: not-allowed !important; }

  :global(.btn-ghost) {
    background: transparent !important;
    border: 1px solid var(--border-sub) !important;
    color: var(--text-2) !important;
    padding: 0.45rem 1rem !important;
    border-radius: 5px !important;
    cursor: pointer !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    font-family: inherit !important;
    transition: background 0.15s, color 0.15s, border-color 0.15s !important;
  }
  :global(.btn-ghost:hover) {
    background: var(--hover) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
  }

  /* ── Badge ── */
  :global(.badge) {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.03em;
  }
  :global(.badge.green)  { background: var(--green-dim);  color: var(--green); }
  :global(.badge.red)    { background: var(--red-dim);    color: var(--red); }
  :global(.badge.yellow) { background: var(--amber-dim);  color: var(--amber); }
  :global(.badge.blue)   { background: var(--blue-dim);   color: var(--blue); }

  /* ── Page layout ── */
  :global(.page) { display: flex; flex-direction: column; gap: 1.25rem; }
  :global(.page-header) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-sub);
  }
  :global(.page-header h1) {
    margin: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: -0.01em !important;
  }
  :global(h1) {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
    margin: 0;
  }
  :global(.form) { display: flex; flex-direction: column; gap: 0.8rem; }
  :global(.grid-2) { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  :global(.form-actions) {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.25rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-sub);
  }

  /* ── App shell ── */
  .app {
    display: grid;
    grid-template-columns: 200px 1fr;
    min-height: 100vh;
    transition: grid-template-columns 0.2s ease;
  }
  .app.collapsed { grid-template-columns: 52px 1fr; }

  /* ── Sidebar ── */
  .sidebar {
    background: var(--surface);
    border-right: 1px solid var(--border-sub);
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
    gap: 0.6rem;
    padding: 0.875rem;
    border-bottom: 1px solid var(--border-sub);
    overflow: hidden;
    min-height: 50px;
    flex-shrink: 0;
  }
  .brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    background: var(--cyan);
    border-radius: 5px;
    color: #000;
    flex-shrink: 0;
  }
  .brand-name {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
    overflow: hidden;
  }
  .brand-top {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text);
    white-space: nowrap;
  }
  .brand-bottom {
    font-size: 0.64rem;
    font-weight: 500;
    color: var(--text-3);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
  }

  nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0.5rem 0;
    overflow-y: auto;
    overflow-x: hidden;
    gap: 1px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.42rem 0.875rem;
    border: none;
    border-left: 2px solid transparent;
    background: none;
    color: var(--text-3);
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 500;
    font-family: inherit;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    transition: color 0.1s, background 0.1s, border-color 0.1s;
    width: 100%;
  }
  .nav-item:hover { color: var(--text-2); background: rgba(255,255,255,0.03); }
  .nav-item.active {
    color: var(--cyan);
    border-left-color: var(--cyan);
    background: var(--cyan-dim);
  }

  .nav-icon { display: flex; align-items: center; flex-shrink: 0; }
  .nav-label { overflow: hidden; text-overflow: ellipsis; }

  .sidebar-footer {
    flex-shrink: 0;
    padding: 0.6rem 0.875rem;
    border-top: 1px solid var(--border-sub);
  }
  .collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 0.35rem;
    background: none;
    border: 1px solid var(--border-sub);
    color: var(--text-3);
    border-radius: 5px;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.1s, color 0.1s, border-color 0.1s;
  }
  .collapse-btn:hover {
    background: var(--hover);
    color: var(--text-2);
    border-color: var(--border);
  }

  /* ── Content ── */
  .content { overflow-y: auto; min-height: 100vh; }
  .content-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 2.5rem;
  }
</style>
