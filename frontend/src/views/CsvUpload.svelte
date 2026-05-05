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
  <h1>Carga Masiva CSV</h1>
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
  .page { display: flex; flex-direction: column; gap: 1.5rem; }
  h1 { margin: 0; font-size: 1.5rem; color: #f1f5f9; }
  .hint { color: #64748b; margin: 0; font-size: 0.9rem; }
  .loaders { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }
  .loader-card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; }
  h3 { margin: 0; font-size: 1rem; color: #f1f5f9; }
  .cols { margin: 0; font-size: 0.8rem; color: #64748b; line-height: 1.5; }
  .cols strong { color: #94a3b8; }
  .upload-row { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
  input[type="file"] { flex: 1; color: #94a3b8; font-size: 0.85rem; }
  .btn-primary { background: #4f46e5; color: #fff; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; white-space: nowrap; }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-primary:hover:not(:disabled) { background: #4338ca; }
  .result { background: #0f172a; border-radius: 6px; padding: 0.75rem; font-size: 0.85rem; color: #86efac; }
  .result.has-errors { border: 1px solid #f59e0b; }
  details { margin-top: 0.5rem; }
  summary { cursor: pointer; color: #fde68a; font-size: 0.82rem; }
  ul { margin: 0.35rem 0 0 1rem; padding: 0; color: #fca5a5; font-size: 0.8rem; }
  li { margin-bottom: 0.25rem; }
</style>
