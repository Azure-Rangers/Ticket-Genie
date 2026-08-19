<script>
  import { onMount } from 'svelte';
  import { apiSearchKB, apiIngestPolicy } from '../lib/api.js';
  import { userStore, isAdmin, isSuperAdmin } from '../lib/stores/auth.js';

  let kbSearch = '';
  let activeCategory = 'All';
  let isAddPolicyOpen = false;

  let newPolicyTitle = '';
  let newPolicyCategory = 'IT & Security';
  let newPolicyContent = '';
  let ingestMessage = '';
  let searchResultAnswer = null;

  $: showAddPolicyBtn = isAdmin($userStore) || isSuperAdmin($userStore);

  const initialArticles = [
    {
      id: 'KB-101',
      title: 'Corporate VPN & Remote Network Setup Guide',
      category: 'IT & Security',
      readTime: '3 min read',
      snippet: 'Step-by-step instructions for installing GlobalProtect VPN client and configuring MFA tokens.'
    },
    {
      id: 'KB-102',
      title: 'Annual Paid Time Off (PTO) & Leave Accrual Policy',
      category: 'HR & Benefits',
      readTime: '5 min read',
      snippet: 'Overview of PTO accumulation rules, carry-over limits, and leave request submission workflows.'
    },
    {
      id: 'KB-103',
      title: 'Hardware Upgrade Eligibility & Procurement Guidelines',
      category: 'Hardware',
      readTime: '4 min read',
      snippet: 'Hardware replacement schedules for laptops, monitors, and peripherals for engineering and design teams.'
    },
    {
      id: 'KB-104',
      title: 'Expense Reimbursement & Corporate Card Usage Policy',
      category: 'Finance',
      readTime: '6 min read',
      snippet: 'Rules regarding eligible travel expenses, receipt submission timelines, and manager approval tiers.'
    }
  ];

  let articles = [...initialArticles];

  async function handleKBSearch() {
    if (!kbSearch.trim()) {
      searchResultAnswer = null;
      return;
    }
    const res = await apiSearchKB(kbSearch);
    if (res && res.answer) {
      searchResultAnswer = res.answer;
    }
  }

  async function submitPolicy() {
    if (!newPolicyTitle.trim() || !newPolicyContent.trim()) return;
    try {
      const res = await apiIngestPolicy({
        title: newPolicyTitle,
        category: newPolicyCategory,
        content: newPolicyContent,
        source: 'Admin Policy Editor'
      });
      ingestMessage = `✅ ${res.message || 'Policy successfully ingested!'}`;
      articles = [
        {
          id: `KB-${Date.now().toString().slice(-3)}`,
          title: newPolicyTitle,
          category: newPolicyCategory,
          readTime: '2 min read',
          snippet: newPolicyContent.slice(0, 100) + '...'
        },
        ...articles
      ];
      setTimeout(() => {
        isAddPolicyOpen = false;
        newPolicyTitle = '';
        newPolicyContent = '';
        ingestMessage = '';
      }, 1500);
    } catch (e) {
      ingestMessage = `⚠️ Ingestion Error: ${e.message}`;
    }
  }

  $: filteredArticles = articles.filter(a => {
    const matchCat = activeCategory === 'All' || a.category === activeCategory;
    const matchSearch = !kbSearch || a.title.toLowerCase().includes(kbSearch.toLowerCase()) || a.snippet.toLowerCase().includes(kbSearch.toLowerCase());
    return matchCat && matchSearch;
  });
</script>

<div class="kb-view animate-fade">
  <div class="kb-hero">
    <div class="hero-top">
      <div>
        <h1>Knowledge Base & Resolution Hub</h1>
        <p>Search corporate policies, IT documentation, and AI-verified resolution guides</p>
      </div>
      {#if showAddPolicyBtn}
        <button class="btn-add-policy" on:click={() => isAddPolicyOpen = true}>
          <i class="ph-bold ph-plus"></i> Add New Policy
        </button>
      {/if}
    </div>

    <div class="hero-search">
      <i class="ph-bold ph-magnifying-glass"></i>
      <input 
        type="text" 
        placeholder="Ask AI or search policies, VPN guides, PTO rules..." 
        bind:value={kbSearch} 
        on:input={handleKBSearch}
      />
    </div>
  </div>

  <!-- AI Knowledge Search Direct Answer Box -->
  {#if searchResultAnswer}
    <div class="ai-answer-box animate-fade">
      <div class="answer-header">
        <i class="ph-duotone ph-sparkle text-purple"></i>
        <h3>AI Resolution Response</h3>
      </div>
      <p>{searchResultAnswer}</p>
    </div>
  {/if}

  <div class="category-tabs">
    {#each ['All', 'IT & Security', 'HR & Benefits', 'Hardware', 'Finance'] as cat}
      <button 
        class="tab-btn" 
        class:active={activeCategory === cat} 
        on:click={() => activeCategory = cat}
      >
        {cat}
      </button>
    {/each}
  </div>

  <div class="articles-grid">
    {#each filteredArticles as article}
      <div class="article-card">
        <div class="card-top">
          <span class="category-tag">{article.category}</span>
          <span class="read-time"><i class="ph-bold ph-clock"></i> {article.readTime}</span>
        </div>
        <h3 class="article-title">{article.title}</h3>
        <p class="article-snippet">{article.snippet}</p>
        <button class="btn-read"><i class="ph-bold ph-arrow-right"></i> Read Full Article</button>
      </div>
    {/each}
  </div>
</div>

<!-- Add Policy Modal -->
{#if isAddPolicyOpen}
  <div class="modal-backdrop" role="button" tabindex="0" on:click={(e) => e.target === e.currentTarget && (isAddPolicyOpen = false)} on:keydown={(e) => e.key === 'Escape' && (isAddPolicyOpen = false)}>
    <div class="modal-card animate-fade">
      <div class="modal-header">
        <h2><i class="ph-duotone ph-file-plus"></i> Add Corporate Policy Article</h2>
        <button class="btn-close" on:click={() => isAddPolicyOpen = false}><i class="ph-bold ph-x"></i></button>
      </div>

      <div class="modal-body">
        {#if ingestMessage}
          <div class="toast-msg">{ingestMessage}</div>
        {/if}

        <div class="form-group">
          <label for="kb-policy-title">Policy Title</label>
          <input id="kb-policy-title" type="text" placeholder="e.g. Remote Work Security Guidelines" bind:value={newPolicyTitle} />
        </div>

        <div class="form-group">
          <label for="kb-policy-category">Category</label>
          <select id="kb-policy-category" bind:value={newPolicyCategory}>
            <option value="IT & Security">IT & Security</option>
            <option value="HR & Benefits">HR & Benefits</option>
            <option value="Hardware">Hardware</option>
            <option value="Finance">Finance</option>
          </select>
        </div>

        <div class="form-group">
          <label for="kb-policy-content">Policy Content & Instructions</label>
          <textarea id="kb-policy-content" rows="5" placeholder="Detailed policy text and resolution steps..." bind:value={newPolicyContent}></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={() => isAddPolicyOpen = false}>Cancel</button>
        <button class="btn-primary" on:click={submitPolicy}>Save & Ingest Policy</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .kb-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    overflow-y: auto;
  }

  .kb-hero {
    background: linear-gradient(135deg, #2b1b38 0%, #4f46e5 100%);
    border-radius: 16px;
    padding: 32px;
    color: white;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: var(--shadow-md);
  }

  .hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .kb-hero h1 {
    font-size: 1.6rem;
    font-weight: 700;
  }

  .kb-hero p {
    color: #c7d2fe;
    font-size: 0.9rem;
    margin-top: 4px;
  }

  .btn-add-policy {
    background: #ffffff;
    color: #4f46e5;
    border: none;
    padding: 10px 16px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
  }

  .btn-add-policy:hover {
    background: #f1f5f9;
  }

  .hero-search {
    position: relative;
    max-width: 580px;
  }

  .hero-search i {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #64748b;
    font-size: 1.1rem;
  }

  .hero-search input {
    width: 100%;
    padding: 12px 16px 12px 42px;
    border-radius: 12px;
    border: none;
    font-size: 0.88rem;
    background: #ffffff;
    color: var(--text-main);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }

  .ai-answer-box {
    background: #ffffff;
    border: 1px solid #c7d2fe;
    border-radius: 14px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
  }

  .answer-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: #4f46e5;
  }

  .ai-answer-box p {
    font-size: 0.88rem;
    color: var(--text-main);
    line-height: 1.5;
  }

  .category-tabs {
    display: flex;
    gap: 10px;
  }

  .tab-btn {
    padding: 8px 16px;
    border-radius: 20px;
    border: 1px solid var(--border-color);
    background: #ffffff;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s;
  }

  .tab-btn:hover {
    border-color: var(--primary);
    color: var(--primary);
  }

  .tab-btn.active {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }

  .articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
  }

  .article-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
  }

  .article-card:hover {
    border-color: #a5b4fc;
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }

  .card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .category-tag {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--primary);
    background: var(--primary-light);
    padding: 3px 10px;
    border-radius: 6px;
  }

  .read-time {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .article-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
  }

  .article-snippet {
    font-size: 0.83rem;
    color: var(--text-muted);
    line-height: 1.45;
  }

  .btn-read {
    margin-top: 4px;
    background: transparent;
    border: none;
    color: var(--primary);
    font-weight: 600;
    font-size: 0.83rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0;
  }

  /* Modal */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-card {
    background: white;
    border-radius: 16px;
    width: 90%;
    max-width: 520px;
    overflow: hidden;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  }

  .modal-header {
    background: #2b1b38;
    color: white;
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h2 {
    font-size: 1.1rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .btn-close {
    background: transparent;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
  }

  .modal-body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .toast-msg {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.82rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .form-group label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-main);
  }

  .form-group input, .form-group select, .form-group textarea {
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    font-size: 0.85rem;
  }

  .modal-footer {
    padding: 16px 24px;
    background: #f8fafc;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  .btn-primary {
    background: var(--primary);
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
  }

  .btn-secondary {
    background: white;
    border: 1px solid var(--border-color);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 0.85rem;
    cursor: pointer;
  }
</style>
