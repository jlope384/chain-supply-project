<script>
  let { open = $bindable(false), title = "", children, onclose } = $props();

  function close() {
    open = false;
    onclose?.();
  }

  function onkeydown(e) {
    if (e.key === "Escape") close();
  }
</script>

<svelte:window onkeydown={onkeydown} />

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
  <div class="overlay" onclick={close}>
    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>{title}</h2>
        <button class="close-btn" onclick={close}>✕</button>
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
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    width: min(560px, 95vw);
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  }
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid #334155;
  }
  h2 {
    margin: 0;
    font-size: 1.1rem;
    color: #f1f5f9;
  }
  .close-btn {
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    font-size: 1.1rem;
    padding: 0.25rem;
    line-height: 1;
  }
  .close-btn:hover {
    color: #f1f5f9;
  }
  .modal-body {
    padding: 1.5rem;
  }
</style>
