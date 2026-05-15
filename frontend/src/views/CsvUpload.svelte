<script>
  import { api } from "../lib/api.js";
  import { toast } from "../lib/toast.svelte.js";

  const loaders = [
    {
      key: "suppliers", label: "Proveedores", fn: (f) => api.csv.suppliers(f),
      columns: "name, country, active, rating, certifications (;-sep), founded_at",
    },
    {
      key: "products", label: "Productos", fn: (f) => api.csv.products(f),
      columns: "name, sku, price, weight, category, in_stock, description",
    },
    {
      key: "warehouses", label: "Bodegas", fn: (f) => api.csv.warehouses(f),
      columns: "code, city, capacity, active, opened_at",
    },
    {
      key: "orders", label: "Órdenes", fn: (f) => api.csv.orders(f),
      columns: "order_id, status, total, placed_at, fulfilled, notes",
    },
    {
      key: "carriers", label: "Transportistas", fn: (f) => api.csv.carriers(f),
      columns: "name, modes (;-sep), active, rating, regions (;-sep), onboarded_at",
    },
    {
      key: "relSupplies", label: "Relación: SUPPLIES", fn: (f) => api.csv.relSupplies(f),
      columns: "supplier_name, product_sku, since, contract_price, exclusive, min_order_qty",
    },
    {
      key: "relStoredIn", label: "Relación: STORED_IN", fn: (f) => api.csv.relStoredIn(f),
      columns: "product_sku, warehouse_code, quantity, reserved_qty, last_updated, bin_codes (;-sep)",
    },
  ];

  let files = $state({});
  let results = $state({});
  let loading = $state({});

  function onFile(key, e) {
    files[key] = e.target.files[0] || null;
  }

  async function upload(loader) {
    if (!files[loader.key]) { toast("Selecciona un archivo CSV", "error"); return; }
    loading[loader.key] = true;
    results[loader.key] = null;
    try {
      const r = await loader.fn(files[loader.key]);
      results[loader.key] = r;
      toast(`${r.created} registros cargados`, "success");
    } catch (e) {
      toast(e.message, "error");
    } finally {
      loading[loader.key] = false;
    }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Carga CSV</h1>
  </div>
  <p class="hint">Sube archivos CSV con encabezados. Los campos requeridos se muestran debajo de cada sección.</p>

  <div class="loaders">
    {#each loaders as loader}
      <div class="loader-card">
        <h3>{loader.label}</h3>
        <p class="cols"><strong>Columnas:</strong> {loader.columns}</p>
        <div class="upload-row">
          <input type="file" accept=".csv" onchange={(e) => onFile(loader.key, e)} />
          <button class="btn-primary" onclick={() => upload(loader)} disabled={loading[loader.key]}>
            {loading[loader.key] ? "Cargando..." : "Subir"}
          </button>
        </div>

        {#if results[loader.key]}
          <div class="result" class:has-errors={results[loader.key].errors?.length > 0}>
            <span>✅ Creados: {results[loader.key].created}</span>
            {#if results[loader.key].errors?.length > 0}
              <details>
                <summary>⚠️ {results[loader.key].errors.length} errores</summary>
                <ul>
                  {#each results[loader.key].errors as err}
                    <li>Fila {err.row}: {err.error}</li>
                  {/each}
                </ul>
              </details>
            {/if}
          </div>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.25rem; }
  .hint { color: var(--text-3); margin: -0.5rem 0 0; font-size: 0.8rem; }
  .loaders { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0.75rem; }
  .loader-card {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 6px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
  }
  h3 { margin: 0; font-size: 0.875rem; font-weight: 600; color: var(--text); }
  .cols { margin: 0; font-size: 0.75rem; color: var(--text-3); line-height: 1.6; }
  .cols strong { color: var(--text-2); font-weight: 600; }
  .upload-row { display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap; }
  input[type="file"] { flex: 1; color: var(--text-2); font-size: 0.8rem; font-family: inherit; }
  .result {
    background: var(--hover);
    border-radius: 5px;
    padding: 0.6rem 0.75rem;
    font-size: 0.8rem;
    color: var(--green);
    border: 1px solid var(--border-sub);
  }
  .result.has-errors { border-color: rgba(251,191,36,0.3); }
  details { margin-top: 0.35rem; }
  summary { cursor: pointer; color: var(--amber); font-size: 0.78rem; }
  ul { margin: 0.3rem 0 0 1rem; padding: 0; color: var(--red); font-size: 0.75rem; }
  li { margin-bottom: 0.2rem; }
</style>
