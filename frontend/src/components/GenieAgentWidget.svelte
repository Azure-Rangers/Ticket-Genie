<script>
  import { activeTab, genieDraftStore } from '../lib/stores/tickets.js';
  import { userStore } from '../lib/stores/auth.js';
  import { apiGenieChat } from '../lib/api.js';

  let isOpen = false;
  let userMessage = '';
  let isSending = false;

  let history = [];
  let draft = null;
  let activeIntent = null;
  let activeRequestType = null;

  const GENIE_DRAFTING_INTENTS = ['create_ticket', 'support_issue', 'leave_management'];

  let messages = [
    {
      sender: 'Genie AI',
      isBot: true,
      text: 'Hi there! I am Genie, your AI support agent. How can I help you today?'
    }
  ];

  let suggestions = ['Check my tickets', 'VPN Setup Guide', 'Leave Balance Policy', 'IT Support Request'];

  function toggleChat() {
    isOpen = !isOpen;
  }

  async function sendMessage(textToSend = null) {
    const text = textToSend || userMessage.trim();
    if (!text || isSending) return;

    // Add User Message
    messages = [...messages, { sender: $userStore?.name || 'You', isBot: false, text }];
    userMessage = '';
    isSending = true;

    try {
      const state = {
        role: $userStore?.role || 'Employee',
        history,
        draft,
        active_intent: activeIntent,
        active_request_type: activeRequestType
      };

      const res = await apiGenieChat(text, state);

      // Advance chat turn history
      history = [
        ...history,
        { role: 'user', message: text },
        { role: 'assistant', message: res.reply || res.message || '' }
      ];

      // Update active drafting state
      const stillDrafting = res.intent && GENIE_DRAFTING_INTENTS.includes(res.intent) && !res.ready_for_review;
      activeIntent = stillDrafting ? res.intent : null;
      activeRequestType = stillDrafting ? res.request_type : null;
      draft = stillDrafting ? (res.ticket_draft || null) : null;

      messages = [
        ...messages,
        { sender: 'Genie AI', isBot: true, text: res.reply || 'Request triaged successfully.' }
      ];
      if (res.suggestions && res.suggestions.length > 0) {
        suggestions = res.suggestions;
      }

      // 1. Automatic Navigation Handling
      if (res.action && res.action.type === 'navigate') {
        const target = (res.action.target || '').toLowerCase();
        if (target.includes('my-tickets') || target.includes('inbox')) {
          $activeTab = 'inbox';
        } else if (target.includes('new-request') || target.includes('submit-ticket')) {
          $activeTab = 'create-ticket';
        } else if (target.includes('knowledge')) {
          $activeTab = 'knowledge';
        } else if (target.includes('analytics')) {
          $activeTab = 'analytics';
        } else if (target.includes('settings') || target.includes('rbac')) {
          $activeTab = 'settings';
        }
      }

      // 2. Automatic Ticket Autofill & Review Handling
      if (res.ticket_draft || res.ready_for_review) {
        if (res.ticket_draft) {
          // res.request_type is a sibling field on the chat response, not
          // part of ticket_draft itself (models.chatbot.TicketDraft has no
          // request_type - see its docstring), so it must be merged in
          // here or CreateTicketView has no way to know which tab/form
          // this draft belongs to and silently falls back to Standard.
          genieDraftStore.set({ ...res.ticket_draft, request_type: res.request_type });
        }
        if (res.ready_for_review) {
          $activeTab = 'create-ticket';
        }
      }
    } catch (err) {
      messages = [
        ...messages,
        { sender: 'Genie AI', isBot: true, text: 'I am experiencing network trouble connecting to the AI engine.' }
      ];
    } finally {
      isSending = false;
    }
  }
</script>

<!-- Floating AI Assistant Launcher Button -->
<div class="genie-container">
  <button class="genie-button" on:click={toggleChat} title="Open AI TicketGenie Assistant">
    <i class="ph-fill ph-sparkle"></i>
    <span>Genie AI</span>
  </button>
</div>

<!-- Floating AI Assistant Chat Drawer -->
{#if isOpen}
  <div class="genie-chat open animate-fade">
    <div class="genie-chat-header">
      <div class="genie-header-info">
        <div class="genie-avatar">
          <i class="ph-fill ph-ticket"></i>
        </div>
        <div>
          <h4>TicketGenie AI Assistant</h4>
          <span class="status-indicator"><span class="genie-status-dot"></span> Active Engine</span>
        </div>
      </div>
      <button class="genie-close" on:click={toggleChat}><i class="ph-bold ph-x"></i></button>
    </div>

    <!-- Messages Container -->
    <div class="genie-messages">
      {#each messages as msg}
        <div class="genie-message" class:genie-message-user={!msg.isBot}>
          {#if msg.isBot}
            <div class="genie-message-avatar"><i class="ph-fill ph-ticket"></i></div>
          {/if}
          <div class="genie-bubble">{msg.text}</div>
        </div>
      {/each}

      {#if isSending}
        <div class="genie-message">
          <div class="genie-message-avatar"><i class="ph-fill ph-ticket"></i></div>
          <div class="genie-bubble typing"><i class="ph-bold ph-spinner animate-spin"></i> Genie is thinking...</div>
        </div>
      {/if}
    </div>

    <!-- Suggestions Bar -->
    {#if suggestions.length > 0 && !isSending}
      <div class="genie-suggestions">
        {#each suggestions as sug}
          <button class="genie-suggestion" on:click={() => sendMessage(sug)}>{sug}</button>
        {/each}
      </div>
    {/if}

    <!-- Input Bar -->
    <div class="genie-input-area">
      <input 
        type="text" 
        placeholder="Ask Genie AI a question..." 
        bind:value={userMessage} 
        on:keydown={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button on:click={() => sendMessage()} disabled={isSending}>
        <i class="ph-bold ph-paper-plane-right"></i>
      </button>
    </div>

    <div class="genie-disclaimer">
      Powered by Azure OpenAI & ReAct Agent Loop
    </div>
  </div>
{/if}

<style>
  .genie-container {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 1000;
  }

  .genie-button {
    height: 48px;
    padding: 0 20px;
    border: none;
    border-radius: 24px;
    background: #2b1b38;
    color: white;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.92rem;
    font-weight: 700;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .genie-button:hover {
    background: #4f46e5;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
  }

  .genie-button i {
    font-size: 1.2rem;
    color: #facc15;
  }

  .genie-chat {
    position: fixed;
    right: 28px;
    bottom: 88px;
    width: 380px;
    height: 520px;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: 0 20px 45px rgba(43, 27, 54, 0.25);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 999;
  }

  .genie-chat-header {
    height: 68px;
    padding: 0 18px;
    background: #2b1b38;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  .genie-header-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .genie-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #facc15;
    font-size: 1.2rem;
  }

  .genie-header-info h4 {
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0;
  }

  .status-indicator {
    font-size: 0.72rem;
    color: #a5b4fc;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .genie-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 6px rgba(16, 185, 129, 0.8);
  }

  .genie-close {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: #9ca3af;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .genie-close:hover {
    color: white;
    background: rgba(255, 255, 255, 0.15);
  }

  .genie-messages {
    flex: 1;
    overflow-y: auto;
    padding: 18px 16px;
    background: #f8fafc;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .genie-message {
    display: flex;
    gap: 10px;
  }

  .genie-message-avatar {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: #e0e7ff;
    color: #4f46e5;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 0.9rem;
  }

  .genie-bubble {
    max-width: 270px;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 4px 12px 12px 12px;
    padding: 10px 14px;
    color: var(--text-main);
    font-size: 0.85rem;
    line-height: 1.45;
    box-shadow: var(--shadow-sm);
  }

  .genie-bubble.typing {
    color: var(--text-muted);
    font-style: italic;
  }

  .genie-message-user {
    justify-content: flex-end;
  }

  .genie-message-user .genie-bubble {
    background: #4f46e5;
    color: white;
    border-color: #4f46e5;
    border-radius: 12px 4px 12px 12px;
  }

  .genie-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 0 16px 10px;
    background: #f8fafc;
  }

  .genie-suggestion {
    border: 1px solid #c7d2fe;
    background: white;
    color: #4f46e5;
    border-radius: 16px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }

  .genie-suggestion:hover {
    background: #eef2ff;
    border-color: #818cf8;
  }

  .genie-input-area {
    padding: 12px 16px;
    border-top: 1px solid var(--border-color);
    background: white;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .genie-input-area input {
    flex: 1;
    height: 38px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0 12px;
    font-size: 0.85rem;
    outline: none;
  }

  .genie-input-area input:focus {
    border-color: var(--primary);
  }

  .genie-input-area button {
    width: 38px;
    height: 38px;
    flex-shrink: 0;
    border: none;
    border-radius: 8px;
    background: var(--primary);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }

  .genie-input-area button:hover {
    background: var(--primary-hover);
  }

  .genie-disclaimer {
    padding: 6px 12px 10px;
    background: white;
    color: var(--text-muted);
    text-align: center;
    font-size: 0.68rem;
  }
</style>
