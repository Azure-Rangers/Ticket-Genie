<script>
  let notifications = [
    { id: 1, title: 'Ticket HD-8021 Resolved', time: '10 mins ago', type: 'ticket', message: 'Your support ticket regarding VPN Token Access has been marked as Resolved by IT Support.', read: false },
    { id: 2, title: 'Leave Request Approved', time: '1 hour ago', type: 'leave', message: 'Your PTO request for 2026-09-01 has been authorized by Management.', read: false },
    { id: 3, title: 'Security Advisory', time: 'Yesterday', type: 'system', message: 'Please ensure your Azure AD password meets 2026 multi-factor guidelines.', read: true }
  ];

  function markAllRead() {
    notifications = notifications.map(n => ({ ...n, read: true }));
  }
</script>

<div class="notifications-view animate-fade">
  <div class="view-header">
    <div>
      <h1 class="view-title"><i class="ph-bold ph-bell"></i> System Notifications</h1>
      <p class="view-subtitle">Real-time alerts, ticket status changes, and policy notifications</p>
    </div>
    <button class="btn-read-all" on:click={markAllRead}>
      <i class="ph-bold ph-checks"></i> Mark All as Read
    </button>
  </div>

  <div class="notifications-list">
    {#each notifications as item}
      <div class="notification-item" class:unread={!item.read}>
        <div class="notif-icon">
          {#if item.type === 'ticket'}
            <i class="ph-fill ph-ticket"></i>
          {:else if item.type === 'leave'}
            <i class="ph-fill ph-calendar-check"></i>
          {:else}
            <i class="ph-fill ph-shield-warning"></i>
          {/if}
        </div>
        <div class="notif-body">
          <div class="notif-header">
            <h4>{item.title}</h4>
            <span class="notif-time">{item.time}</span>
          </div>
          <p>{item.message}</p>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .notifications-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    overflow-y: auto;
  }

  .view-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
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

  .btn-read-all {
    padding: 10px 18px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: white;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .notifications-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 800px;
  }

  .notification-item {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 18px;
    display: flex;
    gap: 16px;
    box-shadow: var(--shadow-sm);
  }

  .notification-item.unread {
    border-left: 4px solid var(--primary);
    background: #f8fafc;
  }

  .notif-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--primary-light);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
  }

  .notif-body {
    flex: 1;
  }

  .notif-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .notif-header h4 {
    font-size: 0.95rem;
    font-weight: 700;
  }

  .notif-time {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .notif-body p {
    font-size: 0.85rem;
    color: var(--text-main);
  }
</style>
