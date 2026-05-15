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
        <button class="close-btn" onclick={close}><X size={15} /></button>
      </div>
      <div class="modal-body">
        {@render children()}
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(3px);
  }
  .modal {
    background: var(--card);
    border: 1px solid var(--border-sub);
    border-radius: 8px;
    width: min(560px, 95vw);
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04), 0 24px 64px rgba(0,0,0,0.6);
  }
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1.25rem;
    border-bottom: 1px solid var(--border-sub);
  }
  h2 { margin: 0; font-size: 0.875rem; color: var(--text); font-weight: 600; }
  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    color: var(--text-3);
    cursor: pointer;
    width: 26px;
    height: 26px;
    border-radius: 4px;
    transition: background 0.1s, color 0.1s;
    font-family: inherit;
  }
  .close-btn:hover { background: var(--hover); color: var(--text); }
  .modal-body { padding: 1.25rem; }
</style>
