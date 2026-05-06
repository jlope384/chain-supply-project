<script>
  import { X } from "lucide-svelte";
  let { open = $bindable(false), title = "", children, onclose } = $props();

  function close() { open = false; onclose?.(); }
  function onkeydown(e) { if (e.key === "Escape") close(); }
</script>

<svelte:window onkeydown={onkeydown} />

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
  <div class="overlay" onclick={close}>
    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>{title}</h2>
        <button class="close-btn" onclick={close}><X size={18} /></button>
      </div>
      <div class="modal-body">
        {@render children()}
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.55);
    display: flex; align-items: center; justify-content: center; z-index: 1000;
    backdrop-filter: blur(2px);
  }
  .modal {
    background: #1e293b; border: 1px solid #334155; border-radius: 12px;
    width: min(580px, 95vw); max-height: 90vh; overflow-y: auto;
    box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  }
  .modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 1.5rem; border-bottom: 1px solid #334155;
  }
  h2 { margin: 0; font-size: 1rem; color: #f1f5f9; font-weight: 600; }
  .close-btn {
    display: flex; align-items: center; justify-content: center;
    background: none; border: none; color: #475569; cursor: pointer;
    width: 30px; height: 30px; border-radius: 6px; transition: background 0.12s, color 0.12s;
  }
  .close-btn:hover { background: #334155; color: #f1f5f9; }
  .modal-body { padding: 1.5rem; }
</style>
