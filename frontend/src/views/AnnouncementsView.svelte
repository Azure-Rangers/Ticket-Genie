<script>
  import { onMount } from 'svelte';
  import { apiFetchAnnouncements } from '../lib/api.js';

  let announcements = [];
  let loading = true;

  onMount(async () => {
    announcements = await apiFetchAnnouncements();
    if (!announcements || announcements.length === 0) {
      announcements = [
        { id: 1, title: 'Q3 Enterprise System Maintenance Window', category: 'IT System Update', date: '2026-08-22', content: 'Scheduled database indexing and security updates will take place on Saturday from 02:00 AM to 04:00 AM UTC.' },
        { id: 2, title: 'Updated Remote Work & Expense Reimbursement Policy', category: 'HR & Operations', date: '2026-08-15', content: 'Please review the newly published 2026 expense policy under the Knowledge Base portal.' }
      ];
    }
    loading = false;
  });
</script>

<div class="announcements-view animate-fade">
  <div class="view-header">
    <div>
      <h1 class="view-title"><i class="ph-bold ph-megaphone"></i> Company Announcements</h1>
      <p class="view-subtitle">Official corporate news, operational notices, and IT system maintenance windows</p>
    </div>
  </div>

  {#if loading}
    <div class="loading-state">
      <i class="ph-bold ph-spinner animate-spin"></i> Loading announcements...
    </div>
  {:else}
    <div class="announcements-list">
      {#each announcements as item}
        <div class="announcement-card">
          <div class="card-header">
            <div>
              <span class="category-chip">{item.category}</span>
              <h2>{item.title}</h2>
            </div>
            <span class="date-chip"><i class="ph-bold ph-calendar"></i> {item.date}</span>
          </div>
          <p class="card-content">{item.content}</p>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .announcements-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    overflow-y: auto;
  }

  .view-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-main);
  }

  .view-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .loading-state {
    padding: 40px;
    text-align: center;
    color: var(--text-muted);
    font-weight: 600;
  }

  .announcements-list {
    display: flex;
    flex-direction: column;
    gap: 18px;
    max-width: 860px;
  }

  .announcement-card {
    background: white;
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--primary);
    border-radius: var(--border-radius);
    padding: 24px;
    box-shadow: var(--shadow-sm);
  }

  .card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .category-chip {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary);
    background: var(--primary-light);
    padding: 2px 8px;
    border-radius: 6px;
    text-transform: uppercase;
  }

  .card-header h2 {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-main);
    margin-top: 6px;
  }

  .date-chip {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
  }

  .card-content {
    font-size: 0.88rem;
    color: var(--text-main);
    line-height: 1.6;
  }
</style>
