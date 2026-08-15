/* =========================================================
   EMPLOYEE NM PORTAL - SHARED UI COMPONENTS
   ========================================================= */

function renderEmployeeNMSidebar(activeTab = "dashboard") {
  const sidebarContainer = document.getElementById("shared-sidebar");
  if (!sidebarContainer) return;

  const tabs = [
    { id: "dashboard", label: "Employee Home", icon: "ph-house", href: "index.html" },
    { id: "new-request", label: "New Support Request", icon: "ph-plus-circle", href: "new-request.html" },
    { id: "my-tickets", label: "My Tickets", icon: "ph-ticket", href: "my-tickets.html" },
    { id: "leave-calendar", label: "Leave Calendar", icon: "ph-calendar", href: "leave-calendar.html" },
    { id: "knowledge", label: "Knowledge Base", icon: "ph-book-open", href: "knowledge-base.html" },
    { id: "chat-history", label: "Genie Assistant Chat", icon: "ph-chats-teardrop", href: "chat-history.html" },
    { id: "announcements", label: "Announcements", icon: "ph-megaphone", href: "announcements.html" },
    { id: "notifications", label: "Notifications", icon: "ph-bell", href: "notifications.html" },
    { id: "profile", label: "Profile", icon: "ph-user", href: "profile.html" },
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
          <div class="brand-badge" style="background:#16a34a;"><i class="ph-fill ph-user"></i></div>
          <div>
            <h2>TicketGenie</h2>
            <span>Employee Portal</span>
          </div>
        </div>
        
        <div class="nav-section">
          <div class="nav-title">Self-Service Portal</div>
          ${navHtml}
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="status-dot" style="background:#16a34a;"></div>
        <span>Employee NM Online</span>
      </div>
    </aside>
  `;
}

function renderEmployeeNMTopNav(pageTitle = "Home", subtitle = "Self-Service Support") {
  const topNavContainer = document.getElementById("shared-topnav");
  if (!topNavContainer) return;

  const user = JSON.parse(localStorage.getItem("portalUser") || '{"name":"Employee NM","role":"Employee"}');

  topNavContainer.innerHTML = `
    <header class="top-nav">
      <div class="page-title-header">
        <h1>${pageTitle}</h1>
        <p>${subtitle}</p>
      </div>
      
      <div class="nav-actions">
        <div class="search-small">
          <i class="ph-bold ph-magnifying-glass"></i>
          <input type="text" placeholder="Search articles or tickets..." />
        </div>
        
        <a href="../index.html" class="switch-role-btn">
          <i class="ph-bold ph-user-switch"></i> Switch Role
        </a>
        
        <div class="user-profile">
          <div class="avatar" style="background:#f0fdf4; color:#16a34a;"><i class="ph-bold ph-user"></i></div>
          <div>
            <div class="user-name">${user.name || "Employee NM"}</div>
            <div class="user-role">${user.role || "Staff Member"}</div>
          </div>
        </div>
      </div>
    </header>
  `;
}

function initEmployeeNMComponents(activeTab, title, subtitle) {
  document.addEventListener("DOMContentLoaded", () => {
    renderEmployeeNMSidebar(activeTab);
    renderEmployeeNMTopNav(title, subtitle);
  });
}
