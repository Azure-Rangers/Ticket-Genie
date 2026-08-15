/* =========================================================
   ADMIN AV PORTAL - SHARED UI COMPONENTS
   ========================================================= */

function renderAdminAVSidebar(activeTab = "dashboard") {
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
          <div class="avatar" style="background:#eef2ff; color:#4f46e5;"><i class="ph-bold ph-shield-check"></i></div>
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
