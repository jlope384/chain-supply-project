<script>
  import { toasts } from "./toast.svelte.js";
</script>

<div class="toasts">
  {#each toasts as t (t.id)}
    <div class="toast toast-{t.type}">{t.message}</div>
  {/each}
</div>

<style>
  .toasts {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 9999;
  }
  .toast {
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    font-size: 0.9rem;
    max-width: 380px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.2s ease;
  }
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  .toast-info { background: #1e40af; color: #bfdbfe; }
  .toast-success { background: #166534; color: #bbf7d0; }
  .toast-error { background: #7f1d1d; color: #fecaca; }
</style>
