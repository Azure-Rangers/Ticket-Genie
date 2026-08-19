<script>
  import { searchQuery, isCreateModalOpen, ticketMetrics } from '../lib/stores/tickets.js';
  import { userStore, loginAs, logout, isSuperAdmin, isAdmin } from '../lib/stores/auth.js';

  let showRoleDropdown = false;

  function handleRoleSelect(roleType) {
    loginAs(roleType);
    showRoleDropdown = false;
  }

  function handleLogout() {
    logout();
    showRoleDropdown = false;
  }
</script>

<header class="header">
  <div class="search-bar">
    <i class="ph-bold ph-magnifying-glass search-icon"></i>
    <input 
      type="text" 
      placeholder="Search tickets by ID, category, or title..." 
      bind:value={$searchQuery}
    />
  </div>

  <div class="header-actions">
    <!-- Azure AD Authenticated Badge -->
    <div class="azure-badge">
      <i class="ph-bold ph-shield-check icon"></i>
      <span>Azure AD: <code>Bearer Token</code></span>
    </div>

    <!-- Quick Create Ticket Button -->
    <button class="btn-create" on:click={() => $isCreateModalOpen = true}>
      <i class="ph-bold ph-plus"></i>
      <span>Create Ticket</span>
    </button>

    <!-- Workspace & Role Dropdown -->
    <div class="role-switcher">
      <button class="btn-role" on:click={() => showRoleDropdown = !showRoleDropdown}>
        <i class="ph-duotone ph-user-gear"></i>
        <span>{$userStore?.role || 'Portal Workspace'}</span>
        <i class="ph-bold ph-caret-down"></i>
      </button>

      {#if showRoleDropdown}
        <div class="dropdown-menu animate-fade">
          <div class="dropdown-header">Switch Workspace</div>
          <button class="dropdown-item" class:active={$userStore?.role === 'Employee'} on:click={() => handleRoleSelect('Employee')}>
            <i class="ph-duotone ph-user"></i> Employee Portal (NM)
          </button>
          <button class="dropdown-item" class:active={$userStore?.role === 'Admin'} on:click={() => handleRoleSelect('Admin')}>
            <i class="ph-duotone ph-shield-check"></i> Ticketer / Admin (AV)
          </button>
          <button class="dropdown-item" class:active={$userStore?.role === 'SuperAdmin'} on:click={() => handleRoleSelect('SuperAdmin')}>
            <i class="ph-duotone ph-crown"></i> SuperAdmin Governance (SS)
          </button>
          
          <div class="dropdown-divider"></div>

          <button class="dropdown-item logout-item" on:click={handleLogout}>
            <i class="ph-bold ph-sign-out"></i> Log Out / Portal Select
          </button>
        </div>
      {/if}
    </div>
  </div>
</header>

<style>
  .header {
    height: 70px;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    z-index: 10;
  }

  .search-bar {
    position: relative;
    width: 380px;
  }

  .search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    font-size: 1.05rem;
  }

  .search-bar input {
    width: 100%;
    padding: 10px 14px 10px 40px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: #f8fafc;
    font-size: 0.85rem;
    color: var(--text-main);
    transition: all 0.2s;
  }

  .search-bar input:focus {
    outline: none;
    border-color: var(--primary);
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .azure-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f1f5f9;
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 0.78rem;
    color: #475569;
  }

  .azure-badge .icon {
    color: var(--success);
  }

  .azure-badge code {
    background: #e0e7ff;
    color: #3730a3;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-weight: 600;
  }

  .btn-create {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--primary);
    color: #ffffff;
    border: none;
    padding: 9px 16px;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
  }

  .btn-create:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
  }

  .role-switcher {
    position: relative;
  }

  .btn-role {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f8fafc;
    border: 1px solid var(--border-color);
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 0.83rem;
    font-weight: 600;
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-role:hover {
    border-color: var(--primary);
    background: #ffffff;
  }

  .dropdown-menu {
    position: absolute;
    right: 0;
    top: calc(100% + 8px);
    width: 240px;
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    box-shadow: var(--shadow-lg);
    padding: 8px;
    z-index: 50;
  }

  .dropdown-header {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    padding: 6px 10px;
    letter-spacing: 0.5px;
  }

  .dropdown-divider {
    height: 1px;
    background: var(--border-color);
    margin: 6px 0;
  }

  .dropdown-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: transparent;
    border: none;
    border-radius: 8px;
    font-size: 0.82rem;
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
  }

  .dropdown-item:hover {
    background: var(--primary-light);
    color: var(--primary);
  }

  .dropdown-item.active {
    font-weight: 600;
    background: var(--primary-light);
    color: var(--primary);
  }

  .logout-item {
    color: #dc2626;
  }

  .logout-item:hover {
    background: #fef2f2;
    color: #dc2626;
  }
</style>
