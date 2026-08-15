/* =========================================================
   ADMIN AV PORTAL - SHARED UI COMPONENTS & EMBEDDED STYLES
   ========================================================= */

function injectAdminAVComponentStyles() {
  if (document.getElementById("component-styles-admin-av")) return;
  const style = document.createElement("style");
  style.id = "component-styles-admin-av";
  style.textContent = `
    .sidebar { width: 260px; background-color: #2b1b36; color: #d1d5db; display: flex; flex-direction: column; flex-shrink: 0; justify-content: space-between; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .sidebar-header { padding: 24px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .brand-badge { background: #4f46e5; color: white; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    .sidebar-header h2 { color: #ffffff; font-size: 1.15rem; margin: 0; }
    .sidebar-header span { font-size: 0.7rem; color: #a5b4fc; text-transform: uppercase; letter-spacing: 1px; }
    .nav-section { padding: 16px; }
    .nav-title { font-size: 0.7rem; color: #818cf8; text-transform: uppercase; font-weight: bold; margin-bottom: 12px; letter-spacing: 1px; padding-left: 8px; }
    .nav-link { display: flex; align-items: center; gap: 12px; padding: 12px 16px; color: #cbd5e1; text-decoration: none; border-radius: 8px; font-size: 0.88rem; margin-bottom: 4px; transition: all 0.2s; }
    .nav-link:hover, .nav-link.active { background-color: rgba(255,255,255,0.1); color: #ffffff; font-weight: 600; }
    .sidebar-footer { padding: 20px 24px; font-size: 0.75rem; color: #a5b4fc; border-top: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; }

    .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px; border-bottom: 1px solid #e2e8f0; background: white; width: 100%; box-sizing: border-box; }
    .page-title-header h1 { font-size: 1.4rem; color: #0f172a; margin: 0; }
    .page-title-header p { font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0; }
    .nav-actions { display: flex; align-items: center; gap: 16px; }
    .search-small { display: flex; align-items: center; background: #f1f5f9; padding: 8px 16px; border-radius: 8px; width: 280px; }
    .search-small input { border: none; background: transparent; outline: none; margin-left: 8px; font-size: 0.85rem; width: 100%; }
    .switch-role-btn { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: #eef2ff; color: #4f46e5; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 600; }
    .user-profile { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; }
    .avatar { width: 34px; height: 34px; background: #eef2ff; color: #4f46e5; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 0.9rem; }
    .user-name { font-weight: 600; color: #0f172a; font-size: 0.85rem; }
    .user-role { font-size: 0.72rem; color: #64748b; }
  `;
  document.head.appendChild(style);
}

function renderAdminAVSidebar(activeTab = "dashboard") {
  injectAdminAVComponentStyles();
  const sidebarContainer = document.getElementById("shared-sidebar");
  if (!sidebarContainer) return;

  const tabs = [
    { id: "dashboard", label: "Operations Dashboard", icon: "ph-layout", href: "admin_dashboard.html" },
    { id: "inbox", label: "Triage Inbox", icon: "ph-tray", href: "inbox.html" },
    { id: "submit-ticket", label: "Create Ticket", icon: "ph-plus-circle", href: "submit-ticket.html" },
    { id: "announcements", label: "Announcements", icon: "ph-megaphone", href: "announcements.html" },
    { id: "knowledge", label: "Knowledge Base", icon: "ph-book-bookmark", href: "knowledge-base.html" },
    { id: "analytics", label: "Analytics", icon: "ph-chart-pie", href: "analytics.html" },
    { id: "archive", label: "Archive", icon: "ph-archive", href: "archive.html" },
    { id: "settings", label: "Settings", icon: "ph-gear", href: "settings.html" },
  ];

  const navHtml = tabs.map(tab => `
    <a href="${tab.href}" class="nav-link ${activeTab === tab.id ? 'active' : ''}">
      <i class="ph-bold ${tab.icon}"></i>
      <span>${tab.label}</span>
    </a>
  `).join("");

  sidebarContainer.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="sidebar-header">
          <div class="brand-badge" style="background:#4f46e5;"><i class="ph-fill ph-shield-check"></i></div>
          <div>
            <h2>TicketGenie</h2>
            <span>Admin AV Portal</span>
          </div>
        </div>
        
        <div class="nav-section">
          <div class="nav-title">Admin Operations</div>
          ${navHtml}
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="status-dot"></div>
        <span>Admin AV Logged In</span>
      </div>
    </aside>
  `;
}

function renderAdminAVTopNav(pageTitle = "Dashboard", subtitle = "HelpDesk Operations") {
  injectAdminAVComponentStyles();
  const topNavContainer = document.getElementById("shared-topnav");
  if (!topNavContainer) return;

  const user = JSON.parse(localStorage.getItem("portalUser") || '{"name":"Admin AV","role":"IT / Operations"}');

  topNavContainer.innerHTML = `
    <header class="top-nav">
      <div class="page-title-header">
        <h1>${pageTitle}</h1>
        <p>${subtitle}</p>
      </div>
      
      <div class="nav-actions">
        <div class="search-small">
          <i class="ph-bold ph-magnifying-glass"></i>
          <input type="text" placeholder="Search tickets..." />
        </div>
        
        <a href="../index.html" class="switch-role-btn">
          <i class="ph-bold ph-user-switch"></i> Switch Role
        </a>
        
        <div class="user-profile">
          <div class="avatar"><i class="ph-bold ph-shield-check"></i></div>
          <div>
            <div class="user-name">${user.name || "Admin AV"}</div>
            <div class="user-role">${user.role || "Operations Admin"}</div>
          </div>
        </div>
      </div>
    </header>
  `;
}

function initAdminAVComponents(activeTab, title, subtitle) {
  document.addEventListener("DOMContentLoaded", () => {
    renderAdminAVSidebar(activeTab);
    renderAdminAVTopNav(title, subtitle);
  });
}
