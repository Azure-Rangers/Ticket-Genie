<script>
  import { onMount } from 'svelte';
  import { checkAuthGuard, userStore } from '../lib/stores/auth.js';
  import { tickets, filteredTickets, statusFilter, priorityFilter, selectedTicket, changeTicketStatus } from '../lib/stores/tickets.js';
  import StatusBadge from '../components/StatusBadge.svelte';
  import TicketCard from '../components/TicketCard.svelte';

  import { apiExportTicketPDF, apiExportCalendar } from '../lib/api.js';

  onMount(() => {
    checkAuthGuard('ticketer');
  });

  let commentText = '';
  
  $: activeComments = $selectedTicket?.comments || [
    {
      sender: $selectedTicket?.requester || 'Requester',
      role: 'Requester',
      text: $selectedTicket?.description || 'Support request created.',
      time: $selectedTicket?.created_at || 'Recently'
    },
    ...($selectedTicket?.classification_reason ? [{
      sender: 'TicketGenie AI Assistant',
      role: 'System',
      text: `AI Auto-Classification (${Math.round(($selectedTicket.classification_confidence || 0.94) * 100)}% confidence): ${$selectedTicket.classification_reason}`,
      time: 'Auto-Triaged'
    }] : [])
  ];

  async function addComment() {
    if (!commentText.trim() || !$selectedTicket) return;
    const newComment = {
      sender: $userStore?.name || 'Admin User',
      role: $userStore?.role || 'Ticketer',
      text: commentText,
      time: 'Just now'
    };
    try {
      await apiUpdateTicket($selectedTicket.id, { notes: commentText });
    } catch (e) {
      console.warn("Notice updating notes:", e);
    }
    const currentComments = $selectedTicket.comments || [];
    $selectedTicket = {
      ...$selectedTicket,
      comments: [...currentComments, newComment]
    };
    commentText = '';
  }

  function handleStatusSelect(status) {
    if ($selectedTicket) {
      changeTicketStatus($selectedTicket.id, status);
      $selectedTicket = { ...$selectedTicket, status };
    }
  }
</script>

<div class="inbox-view animate-fade">
  <div class="inbox-header">
    <div>
      <h1 class="view-title">Triage Inbox</h1>
      <p class="view-subtitle">Filter, inspect, assign, and resolve incoming service tickets</p>
    </div>

    <!-- Filter Control Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <label for="inbox-status-filter"><i class="ph-bold ph-funnel"></i> Status:</label>
        <select id="inbox-status-filter" bind:value={$statusFilter}>
          <option value="all">All Statuses</option>
          <option value="Open">Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Resolved">Resolved</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="inbox-priority-filter">Priority:</label>
        <select id="inbox-priority-filter" bind:value={$priorityFilter}>
          <option value="all">All Priorities</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>
    </div>
  </div>

  <div class="inbox-layout">
    <!-- Ticket List Column -->
    <div class="ticket-list-col">
      {#if $filteredTickets.length === 0}
        <div class="empty-inbox">
          <i class="ph-duotone ph-tray"></i>
          <p>No tickets match the selected filters</p>
        </div>
      {:else}
        {#each $filteredTickets as ticket}
          <TicketCard {ticket} />
        {/each}
      {/if}
    </div>

    <!-- Selected Ticket Detail Inspector -->
    <div class="ticket-detail-pane">
      {#if $selectedTicket}
        <div class="detail-card animate-fade">
          <div class="detail-header">
            <div>
              <span class="detail-id">{$selectedTicket.id}</span>
              <h2 class="detail-title">{$selectedTicket.title}</h2>
            </div>
            <div class="header-right-group">
              <StatusBadge status={$selectedTicket.status} type="status" />
              <div class="action-btn-group">
                <button class="btn-action-export" on:click={() => apiExportTicketPDF($selectedTicket.id)} title="Download Ticket PDF Summary">
                  <i class="ph-bold ph-file-pdf"></i> Download PDF
                </button>
                <button class="btn-action-calendar" on:click={() => apiExportCalendar()} title="Export to iCal Calendar">
                  <i class="ph-bold ph-calendar-plus"></i> iCal
                </button>
              </div>
            </div>
          </div>

          <div class="meta-row">
            <div class="meta-block">
              <span class="meta-label">Requester</span>
              <span class="meta-val"><i class="ph-bold ph-user"></i> {$selectedTicket.requester || 'Employee User'}</span>
            </div>
            <div class="meta-block">
              <span class="meta-label">Category</span>
              <span class="meta-val"><i class="ph-bold ph-tag"></i> {$selectedTicket.category || 'IT & Infrastructure'}</span>
            </div>
            <div class="meta-block">
              <span class="meta-label">Priority</span>
              <StatusBadge status={$selectedTicket.priority || 'Medium'} type="priority" />
            </div>
          </div>

          <div class="description-box">
            <h4>Issue Description</h4>
            <p>{$selectedTicket.description || 'No detailed description provided for this request.'}</p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="status-actions">
            <span>Change Status:</span>
            <button 
              class="btn-status open" 
              class:active={$selectedTicket.status === 'Open'} 
              on:click={() => handleStatusSelect('Open')}
            >
              Open
            </button>
            <button 
              class="btn-status progress" 
              class:active={$selectedTicket.status === 'In Progress'} 
              on:click={() => handleStatusSelect('In Progress')}
            >
              In Progress
            </button>
            <button 
              class="btn-status resolve" 
              class:active={$selectedTicket.status === 'Resolved'} 
              on:click={() => handleStatusSelect('Resolved')}
            >
              Resolved
            </button>
          </div>

          <!-- Conversation Thread -->
          <div class="comments-section">
            <h4>Conversation Thread ({activeComments.length})</h4>
            <div class="comments-list">
              {#each activeComments as c}
                <div class="comment-item" class:system-comment={c.role === 'System'}>
                  <div class="comment-header">
                    <span class="comment-sender">{c.sender} <span class="role-tag">({c.role})</span></span>
                    <span class="comment-time">{c.time}</span>
                  </div>
                  <p class="comment-text">{c.text}</p>
                </div>
              {/each}
            </div>

            <div class="comment-input-box">
              <input 
                type="text" 
                placeholder="Type a response or resolution note..." 
                bind:value={commentText}
                on:keydown={(e) => e.key === 'Enter' && addComment()}
              />
              <button on:click={addComment}><i class="ph-bold ph-paper-plane-right"></i></button>
            </div>
          </div>
        </div>
      {:else}
        <div class="no-selection">
          <i class="ph-duotone ph-cursor-click"></i>
          <h3>Select a ticket from the queue</h3>
          <p>Click any ticket on the left to view details, update status, or add notes</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .inbox-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 100%;
    overflow: hidden;
  }

  .inbox-header {
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

  .filter-bar {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-main);
  }

  .filter-group select {
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: #ffffff;
    font-size: 0.82rem;
  }

  .inbox-layout {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 24px;
    flex: 1;
    overflow: hidden;
  }

  .ticket-list-col {
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
    padding-right: 6px;
  }

  .empty-inbox {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
  }

  .empty-inbox i {
    font-size: 3rem;
    margin-bottom: 8px;
  }

  .ticket-detail-pane {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    overflow-y: auto;
    box-shadow: var(--shadow-sm);
  }

  .detail-card {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .detail-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  .header-right-group {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
  }

  .action-btn-group {
    display: flex;
    gap: 6px;
  }

  .btn-action-export, .btn-action-calendar {
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: #ffffff;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-main);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: all 0.15s;
  }

  .btn-action-export:hover {
    border-color: #ef4444;
    color: #ef4444;
    background: #fef2f2;
  }

  .btn-action-calendar:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  .detail-id {
    font-family: monospace;
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--primary);
    background: var(--primary-light);
    padding: 2px 8px;
    border-radius: 6px;
  }

  .detail-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    margin-top: 6px;
  }

  .meta-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    background: #f8fafc;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
  }

  .meta-block {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .meta-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
  }

  .meta-val {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .description-box h4 {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 6px;
  }

  .description-box p {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
  }

  .status-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 14px 0;
    border-top: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
  }

  .btn-status {
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid var(--border-color);
    background: #ffffff;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn-status.open.active { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
  .btn-status.progress.active { background: #fffbeb; color: #d97706; border-color: #fde68a; }
  .btn-status.resolve.active { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }

  .comments-section h4 {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .comments-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 240px;
    overflow-y: auto;
    margin-bottom: 12px;
  }

  .comment-item {
    background: #f8fafc;
    border-radius: 10px;
    padding: 12px 14px;
    border: 1px solid var(--border-color);
  }

  .comment-item.system-comment {
    background: #f5f3ff;
    border-color: #ddd6fe;
  }

  .comment-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    margin-bottom: 4px;
  }

  .comment-sender {
    font-weight: 700;
    color: var(--text-main);
  }

  .role-tag {
    font-weight: 400;
    color: var(--text-muted);
  }

  .comment-time {
    color: var(--text-muted);
    font-size: 0.72rem;
  }

  .comment-text {
    font-size: 0.82rem;
    color: var(--text-main);
    line-height: 1.4;
  }

  .comment-input-box {
    display: flex;
    gap: 8px;
  }

  .comment-input-box input {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    font-size: 0.83rem;
  }

  .comment-input-box button {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0 16px;
    border-radius: 10px;
    cursor: pointer;
  }

  .no-selection {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--text-muted);
    padding: 40px;
  }

  .no-selection i {
    font-size: 3.5rem;
    margin-bottom: 12px;
    color: #cbd5e1;
  }

  .no-selection h3 {
    font-size: 1.1rem;
    color: var(--text-main);
    margin-bottom: 4px;
  }

  .no-selection p {
    font-size: 0.85rem;
  }
</style>
