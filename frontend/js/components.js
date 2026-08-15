/* =========================================================
   TICKETGENIE - SHARED UI COMPONENTS & LAYOUT ENGINE
   ========================================================= */

function renderSidebar(activeTab = "dashboard") {
  const sidebarContainer = document.getElementById("shared-sidebar");
  if (!sidebarContainer) return;

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: "ph-layout", href: "index.html" },
    { id: "inbox", label: "Inbox & Leave Queue", icon: "ph-tray", href: "inbox.html" },
    { id: "departments", label: "Departments & RBAC", icon: "ph-buildings", href: "departments.html" },
    { id: "knowledge", label: "Knowledge Base", icon: "ph-book-bookmark", href: "knowledge-base.html" },
    { id: "analytics", label: "HR Analytics", icon: "ph-chart-line-up", href: "analytics.html" },
    { id: "settings", label: "System Settings", icon: "ph-gear-six", href: "settings.html" },
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
          <div class="brand-badge"><i class="ph-fill ph-ticket"></i></div>
          <div>
            <h2>TicketGenie</h2>
            <span>Super Admin & Ops</span>
          </div>
        </div>
        
        <div class="nav-section">
          <div class="nav-title">Management Tools</div>
          ${navHtml}
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="status-dot"></div>
        <span>Azure OpenTelemetry Live</span>
      </div>
    </aside>
  `;
}

function renderTopNav(pageTitle = "Dashboard", subtitle = "Super Admin Control Center") {
  const topNavContainer = document.getElementById("shared-topnav");
  if (!topNavContainer) return;

  const user = JSON.parse(localStorage.getItem("portalUser") || '{"name":"SuperAdmin SS","role":"Super Admin"}');

  topNavContainer.innerHTML = `
    <header class="top-nav">
      <div class="page-title-header">
        <h1>${pageTitle}</h1>
        <p>${subtitle}</p>
      </div>
      
      <div class="nav-actions">
        <div class="search-small">
          <i class="ph-bold ph-magnifying-glass"></i>
          <input type="text" id="globalSearchInput" placeholder="Search tickets, departments, SQL..." onkeyup="handleGlobalSearch(event)" />
        </div>
        
        <a href="../index.html" class="switch-role-btn" title="Switch Portal Role">
          <i class="ph-bold ph-user-switch"></i> Switch Role
        </a>
        
        <div class="user-profile">
          <div class="avatar"><i class="ph-bold ph-crown"></i></div>
          <div>
            <div class="user-name">${user.name || "SuperAdmin SS"}</div>
            <div class="user-role">${user.role || "Super Admin"}</div>
          </div>
        </div>
      </div>
    </header>
  `;
}

function initSharedComponents(activeTab, title, subtitle) {
  document.addEventListener("DOMContentLoaded", () => {
    renderSidebar(activeTab);
    renderTopNav(title, subtitle);
  });
}
