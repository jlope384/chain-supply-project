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
    bottom: 1.25rem;
    right: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    z-index: 9999;
  }
  .toast {
    padding: 0.6rem 1rem 0.6rem 0.875rem;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 500;
    max-width: 340px;
    border: 1px solid transparent;
    border-left-width: 3px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    animation: slideIn 0.18s ease;
    font-family: "Inter", -apple-system, sans-serif;
  }
  @keyframes slideIn {
    from { transform: translateX(20px); opacity: 0; }
    to   { transform: translateX(0);    opacity: 1; }
  }
  .toast-info    { background: var(--card); border-color: var(--border-sub); border-left-color: var(--blue);  color: var(--text); }
  .toast-success { background: var(--card); border-color: var(--border-sub); border-left-color: var(--green); color: var(--text); }
  .toast-error   { background: var(--card); border-color: var(--border-sub); border-left-color: var(--red);   color: var(--text); }
</style>
