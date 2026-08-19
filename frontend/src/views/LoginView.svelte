<script>
  import { userStore, azureAuthStatus, loginAs, loginWithAzureAD } from '../lib/stores/auth.js';
  import { onMount } from 'svelte';

  onMount(() => {
    console.log("🔐 [Login Portal] Mounted LoginView screen. Waiting for user authentication...");
  });

  function handleAzureSignIn() {
    console.log("🚀 [Login Portal] Sign In with Azure AD button clicked.");
    loginWithAzureAD();
  }

  function selectPortal(roleType) {
    console.log(`🖱️ [Login Portal] Workspace button clicked: ${roleType}`);
    loginAs(roleType);
  }
</script>

<div class="login-page">
  <div class="login-wrapper animate-fade">
    <div class="login-header">
      <h1><span class="bot-icon"><i class="ph-fill ph-ticket"></i></span> TicketGenie</h1>
      <p>Enterprise Authentication & Workspace Selection</p>
    </div>
    
    <div class="portal-container">
      <!-- Azure AD Status Badge -->
      <div class="azure-status">
        <i class="ph-bold ph-shield-check" style="color: #10b981; font-size: 1rem;"></i>
        <span>Azure AD: <code>{$azureAuthStatus}</code></span>
      </div>

      <!-- Primary Azure AD OAuth Sign In Button -->
      <button class="azure-signin-btn" on:click={handleAzureSignIn}>
        <i class="ph-bold ph-windows-logo"></i>
        <span>Sign In with Azure AD (SSO)</span>
      </button>

      <div class="divider"><span>OR SELECT DEMO WORKSPACE</span></div>

      <!-- Employee Portal Button -->
      <button class="portal-btn" on:click={() => selectPortal('Employee')}>
        <div class="portal-icon icon-employee"><i class="ph-duotone ph-user"></i></div>
        <div class="portal-text">
          <h3>Employee Portal (NM)</h3>
          <p>Submit tickets, search policies, and check request status</p>
        </div>
        <i class="ph-bold ph-caret-right caret"></i>
      </button>

      <!-- Ticketer / Admin (AV) Button -->
      <button class="portal-btn" on:click={() => selectPortal('Admin')}>
        <div class="portal-icon icon-admin"><i class="ph-duotone ph-shield-check"></i></div>
        <div class="portal-text">
          <h3>Ticketer / Admin Portal (AV)</h3>
          <p>Manage triage inbox, process tickets, and handle queue requests</p>
        </div>
        <i class="ph-bold ph-caret-right caret"></i>
      </button>

      <!-- SuperAdmin Governance Portal (SS) Button -->
      <button class="portal-btn" on:click={() => selectPortal('SuperAdmin')}>
        <div class="portal-icon icon-super"><i class="ph-duotone ph-crown"></i></div>
        <div class="portal-text">
          <h3>SuperAdmin Governance Portal (SS)</h3>
          <p>Enterprise control center, RBAC object mapping, and telemetry</p>
        </div>
        <i class="ph-bold ph-caret-right caret"></i>
      </button>
    </div>
  </div>
</div>

<style>
  .login-page {
    width: 100vw;
    height: 100vh;
    background-color: #f4f5f8;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }

  .login-wrapper {
    width: 100%;
    max-width: 520px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
    overflow: hidden;
  }

  .login-header {
    background-color: #2b1b38;
    padding: 36px 24px;
    text-align: center;
    color: white;
  }

  .login-header h1 {
    font-size: 1.6rem;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-weight: 700;
  }

  .login-header p {
    color: #a5b4fc;
    font-size: 0.9rem;
  }

  .bot-icon {
    background: rgba(255,255,255,0.1);
    color: #facc15;
    padding: 6px 10px;
    border-radius: 10px;
    font-size: 1.3rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .portal-container {
    padding: 32px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .azure-signin-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 14px 20px;
    background: #0078d4;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.25);
  }

  .azure-signin-btn:hover {
    background: #005a9e;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0, 120, 212, 0.35);
  }

  .divider {
    text-align: center;
    border-bottom: 1px solid #e2e8f0;
    line-height: 0.1em;
    margin: 12px 0 6px;
  }

  .divider span {
    background: #fff;
    padding: 0 10px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.8px;
  }

  .portal-btn {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
    width: 100%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  }

  .portal-btn:hover {
    border-color: #a5b4fc;
    background: #fefeff;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.1);
  }

  .portal-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.4rem;
    flex-shrink: 0;
  }

  .icon-admin { background: #eef2ff; color: #4f46e5; }
  .icon-employee { background: #f0fdf4; color: #16a34a; }
  .icon-super { background: #fffbeb; color: #b45309; border: 1px solid #fef08a; }

  .portal-text h3 {
    font-size: 1rem;
    color: #111827;
    margin-bottom: 4px;
    font-weight: 600;
  }

  .portal-text p {
    font-size: 0.8rem;
    color: #6b7280;
    line-height: 1.4;
  }

  .caret {
    margin-left: auto;
    color: #9ca3af;
    font-size: 1.2rem;
    transition: transform 0.2s;
  }

  .portal-btn:hover .caret {
    color: #4f46e5;
    transform: translateX(4px);
  }

  .azure-status {
    font-size: 0.78rem;
    color: #334155;
    background: #f8fafc;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    text-align: center;
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
    margin-bottom: 4px;
  }

  .azure-status code {
    font-family: monospace;
    font-weight: 600;
    color: #2563eb;
    background: #eff6ff;
    padding: 2px 6px;
    border-radius: 4px;
  }
</style>
