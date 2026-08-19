<script>
  import { userStore } from '../lib/stores/auth.js';
</script>

<header class="header">
  <div class="header-branding">
    <span class="portal-tag">TicketGenie Service Portal</span>
  </div>

  <div class="header-actions">
    <!-- Azure AD Authenticated Badge -->
    <div class="azure-badge">
      <i class="ph-bold ph-shield-check icon"></i>
      <span>Azure AD: <code>Bearer Token</code></span>
    </div>

    <!-- Authenticated User Profile Badge -->
    <div class="user-profile-badge">
      <i class="ph-duotone ph-user-circle"></i>
      <span>{$userStore?.name || 'Employee User'}</span>
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

  .header-branding {
    display: flex;
    align-items: center;
  }

  .portal-tag {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.01em;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .user-profile-badge {
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
  }

  .user-profile-badge i {
    font-size: 1.2rem;
    color: var(--primary);
  }
</style>
