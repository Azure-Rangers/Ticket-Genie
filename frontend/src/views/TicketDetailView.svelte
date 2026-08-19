<script>
  import { onMount } from 'svelte';
  import { selectedTicket, activeTab, changeTicketStatus } from '../lib/stores/tickets.js';
  import { userStore, isTicketer } from '../lib/stores/auth.js';
  import StatusBadge from '../components/StatusBadge.svelte';
  import { apiFetchComments, apiPostComment, apiExportTicketPDF, apiExportTicketDOCX, apiExportCalendar } from '../lib/api.js';

  let comments = [];
  let loadingComments = false;
  let replyMessage = '';
  let sendingReply = false;
  let errorMsg = '';

  $: ticket = $selectedTicket;

  $: systemAiMessage = (ticket?.classification_reason || ticket?.reason) ? {
    sender_id: 'AI Genie',
    sender_role: 'System',
    message: `AI Auto-Classification (${Math.round((ticket.classification_confidence || ticket.confidence || 0.94) * 100)}% confidence): ${ticket.classification_reason || ticket.reason}`,
    createdAt: 'Auto-Triaged'
  } : null;

  $: currentOid = ($userStore?.objectId || $userStore?.azure_object_id || $userStore?.oid || '').toLowerCase().trim();
  $: currentEmail = ($userStore?.email || '').toLowerCase().trim();
  $: ticketReq = (ticket?.requester_id || ticket?.user_id || '').toLowerCase().trim();
  $: isCreator = !!(ticketReq && (
    (currentOid && ticketReq === currentOid) ||
    (currentEmail && ticketReq === currentEmail)
  ));

  $: displayComments = systemAiMessage 
    ? [systemAiMessage, ...comments.filter(c => c.sender_role !== 'System')] 
    : comments;

  onMount(async () => {
    if (ticket && ticket.id) {
      await loadComments();
    }
  });

  async function loadComments() {
    if (!ticket || !ticket.id) return;
    loadingComments = true;
    try {
      const fetched = await apiFetchComments(ticket.id);
      if (Array.isArray(fetched)) {
        comments = fetched;
      }
    } catch (err) {
      console.warn("Failed to load comments:", err);
    } finally {
      loadingComments = false;
    }
  }

  async function handleSendReply() {
    if (!replyMessage.trim() || !ticket) return;
    sendingReply = true;
    errorMsg = '';
    const text = replyMessage.trim();

    try {
      const createdComment = await apiPostComment(ticket.id, text);
      replyMessage = '';
      if (createdComment && createdComment.id) {
        comments = [...comments, createdComment];
      } else {
        comments = [
          ...comments,
          {
            sender_id: $userStore?.name || 'User',
            sender_role: $userStore?.role || 'Employee',
            message: text,
            createdAt: 'Just now'
          }
        ];
      }
    } catch (err) {
      console.error("Failed to post comment:", err);
      // Fallback local update
      comments = [
        ...comments,
        {
          sender_id: $userStore?.name || 'User',
          sender_role: $userStore?.role || 'Employee',
          message: text,
          createdAt: 'Just now'
        }
      ];
      replyMessage = '';
    } finally {
      sendingReply = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendReply();
    }
  }

  function goBack() {
    $activeTab = 'dashboard';
  }

  function downloadDocx(ticketId) {
    if (!ticketId) return;
    window.open(`/api/tickets/${encodeURIComponent(ticketId)}/export?format=docx`, '_blank');
  }

  function handleStatusChange(newStatus) {
    if (ticket) {
      changeTicketStatus(ticket.id, newStatus);
      ticket = { ...ticket, status: newStatus };
      $selectedTicket = ticket;
    }
  }
</script>

<div class="ticket-detail-page animate-fade">
  <!-- Back Button & Page Header -->
  <div class="detail-nav-header">
    <button class="btn-back" on:click={goBack}>
      <i class="ph-bold ph-arrow-left"></i> Back to My Tickets
    </button>
  </div>

  {#if !ticket}
    <div class="empty-state-card">
      <i class="ph-duotone ph-ticket empty-icon"></i>
      <h2>No Ticket Selected</h2>
      <p>Please select a ticket from your dashboard or requests list to view details.</p>
      <button class="btn-primary" on:click={goBack}>Return to Dashboard</button>
    </div>
  {:else}
    <div class="detail-layout">
      <!-- Top Card: Ticket Summary & Metadata -->
      <div class="summary-card">
        <div class="card-header-row">
          <div>
            <div class="id-badge">#{ticket.id}</div>
            <h1 class="ticket-title">{ticket.title}</h1>
          </div>

          <div class="export-actions">
            <button class="btn-export pdf" on:click={() => apiExportTicketPDF(ticket.id)}>
              <i class="ph-bold ph-file-pdf"></i> Export PDF
            </button>
            <button class="btn-export docx" on:click={() => apiExportTicketDOCX(ticket.id)}>
              <i class="ph-bold ph-file-doc"></i> Export DOCX
            </button>
            <button class="btn-export ical" on:click={() => apiExportCalendar()}>
              <i class="ph-bold ph-calendar-plus"></i> iCal
            </button>
          </div>
        </div>

        <div class="meta-strip">
          <div class="meta-item">
            <span class="meta-label">Category</span>
            <span class="meta-val"><i class="ph-bold ph-tag"></i> {ticket.category || ticket.department || 'IT Support'}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Priority</span>
            <StatusBadge status={ticket.priority || 'Medium'} type="priority" />
          </div>
          <div class="meta-item">
            <span class="meta-label">Status</span>
            <StatusBadge status={ticket.status || 'Open'} type="status" />
          </div>
          <div class="meta-item">
            <span class="meta-label">Created Date</span>
            <span class="meta-val"><i class="ph-bold ph-calendar"></i> {ticket.date || ticket.createdAt || 'Today'}</span>
          </div>
        </div>

        <div class="description-section">
          <h3><i class="ph-bold ph-align-left"></i> Issue Description</h3>
          <p class="desc-body">{ticket.description || 'No additional description provided.'}</p>
        </div>

        {#if isTicketer($userStore)}
          <div class="status-change-bar">
            <span>Update Ticket Status:</span>
            <button 
              class="btn-status open" 
              class:active={ticket.status === 'Open'} 
              on:click={() => handleStatusChange('Open')}
            >
              Open
            </button>
            <button 
              class="btn-status progress" 
              class:active={ticket.status === 'In Progress'} 
              on:click={() => handleStatusChange('In Progress')}
            >
              In Progress
            </button>
            {#if !isCreator}
              <button 
                class="btn-status resolve" 
                class:active={ticket.status === 'Resolved'} 
                on:click={() => handleStatusChange('Resolved')}
              >
                Resolved
              </button>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Bottom Card: Support Conversation Thread -->
      <div class="thread-card">
        <div class="thread-header">
          <h2><i class="ph-duotone ph-chats text-primary"></i> Support Conversation Thread ({displayComments.length})</h2>
          <p>Direct communication channel with IT, HR, and Support Agents</p>
        </div>

        <div class="thread-messages-list">
          {#if loadingComments}
            <div class="loading-state">
              <i class="ph-bold ph-spinner animate-spin"></i> Loading conversation thread...
            </div>
          {:else if displayComments.length === 0}
            <div class="empty-thread">
              <i class="ph-duotone ph-chat-circle-dots"></i>
              <p>No messages yet in this conversation thread.</p>
            </div>
          {:else}
            {#each displayComments as c}
              <div 
                class="message-bubble" 
                class:user-bubble={c.sender_role === 'Employee' || c.sender_role === 'Requester'} 
                class:support-bubble={c.sender_role !== 'Employee' && c.sender_role !== 'Requester' && c.sender_role !== 'System'}
                class:system-bubble={c.sender_role === 'System'}
              >
                <div class="bubble-header">
                  <span class="sender-name">
                    {c.sender_id || c.sender || 'User'} 
                    <span class="role-tag">({c.sender_role || 'Employee'})</span>
                  </span>
                  <span class="msg-time">{c.createdAt || c.time || 'Recently'}</span>
                </div>
                <div class="bubble-text">{c.message || c.text || ''}</div>
              </div>
            {/each}
          {/if}
        </div>

        <div class="reply-box">
          <input 
            type="text" 
            placeholder="Type a message or response to support..." 
            bind:value={replyMessage}
            on:keydown={handleKeydown}
          />
          <button class="btn-send" on:click={handleSendReply} disabled={sendingReply || !replyMessage.trim()}>
            {#if sendingReply}
              <i class="ph-bold ph-spinner animate-spin"></i> Sending...
            {:else}
              <i class="ph-bold ph-paper-plane-right"></i> Send Message
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .ticket-detail-page {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 100%;
    overflow-y: auto;
    width: 100%;
    box-sizing: border-box;
  }

  .detail-nav-header {
    display: flex;
    align-items: center;
  }

  .btn-back {
    background: #ffffff;
    border: 1px solid var(--border-color);
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-main);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.15s;
  }

  .btn-back:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: #f8fafc;
  }

  .empty-state-card {
    background: white;
    border-radius: 16px;
    padding: 60px 20px;
    text-align: center;
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .empty-icon {
    font-size: 3.5rem;
    color: #cbd5e1;
  }

  .detail-layout {
    display: flex;
    flex-direction: column;
    gap: 24px;
    max-width: 960px;
    width: 100%;
  }

  .summary-card, .thread-card {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 28px;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .card-header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }

  .id-badge {
    font-family: monospace;
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--primary);
    background: var(--primary-light);
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 6px;
  }

  .ticket-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-main);
  }

  .export-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn-export {
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: #ffffff;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
  }

  .btn-export.pdf { color: #dc2626; border-color: #fca5a5; background: #fef2f2; }
  .btn-export.pdf:hover { background: #dc2626; color: white; }

  .btn-export.docx { color: #2563eb; border-color: #bfdbfe; background: #eff6ff; }
  .btn-export.docx:hover { background: #2563eb; color: white; }

  .btn-export.ical { color: #059669; border-color: #a7f3d0; background: #ecfdf5; }
  .btn-export.ical:hover { background: #059669; color: white; }

  .meta-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    background: #f8fafc;
    padding: 16px 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }

  .meta-item {
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
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .description-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 8px;
    border-top: 1px solid #f1f5f9;
  }

  .description-section h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .desc-body {
    font-size: 0.9rem;
    color: var(--text-main);
    line-height: 1.6;
    background: #ffffff;
    white-space: pre-wrap;
  }

  .status-change-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-top: 14px;
    border-top: 1px solid #f1f5f9;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .btn-status {
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid var(--border-color);
    background: #ffffff;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn-status.open.active { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
  .btn-status.progress.active { background: #fffbeb; color: #d97706; border-color: #fde68a; }
  .btn-status.resolve.active { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }

  .thread-header h2 {
    font-size: 1.15rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-main);
  }

  .thread-header p {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .thread-messages-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-height: 420px;
    overflow-y: auto;
    padding-right: 6px;
    margin: 10px 0;
  }

  .message-bubble {
    background: #f8fafc;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .message-bubble.user-bubble {
    background: #f0fdf4;
    border-color: #bbf7d0;
  }

  .message-bubble.support-bubble {
    background: #eff6ff;
    border-color: #bfdbfe;
  }

  .message-bubble.system-bubble {
    background: #f5f3ff;
    border-color: #ddd6fe;
  }

  .bubble-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.8rem;
  }

  .sender-name {
    font-weight: 700;
    color: var(--text-main);
  }

  .role-tag {
    font-weight: 500;
    color: var(--text-muted);
  }

  .msg-time {
    font-size: 0.75rem;
    color: var(--text-muted);
  }

  .bubble-text {
    font-size: 0.88rem;
    color: var(--text-main);
    line-height: 1.5;
  }

  .reply-box {
    display: flex;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid var(--border-color);
  }

  .reply-box input {
    flex: 1;
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    font-size: 0.88rem;
  }

  .reply-box input:focus {
    outline: none;
    border-color: var(--primary);
  }

  .btn-send {
    padding: 12px 22px;
    border-radius: 10px;
    border: none;
    background: var(--primary);
    color: #ffffff;
    font-weight: 600;
    font-size: 0.88rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .btn-send:hover {
    background: var(--primary-hover);
  }

  .btn-send:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
