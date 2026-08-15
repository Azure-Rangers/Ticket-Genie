/* =========================================================
   EMPLOYEE NM PORTAL - AUTO-INITIALIZING UNIFIED COMPONENTS
   ========================================================= */

function injectEmployeeNMComponentStyles() {
  if (document.getElementById("component-styles-employee-nm")) return;
  const style = document.createElement("style");
  style.id = "component-styles-employee-nm";
  style.textContent = `
    .sidebar { width: 260px; background-color: #1c2b23; color: #d1d5db; display: flex; flex-direction: column; flex-shrink: 0; justify-content: space-between; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .sidebar-header { padding: 24px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .brand-badge { background: #16a34a; color: white; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    .sidebar-header h2 { color: #ffffff; font-size: 1.15rem; margin: 0; }
    .sidebar-header span { font-size: 0.7rem; color: #86efac; text-transform: uppercase; letter-spacing: 1px; }
    .nav-section { padding: 16px; }
    .nav-title { font-size: 0.7rem; color: #4ade80; text-transform: uppercase; font-weight: bold; margin-bottom: 12px; letter-spacing: 1px; padding-left: 8px; }
    .nav-link { display: flex; align-items: center; gap: 12px; padding: 12px 16px; color: #cbd5e1; text-decoration: none; border-radius: 8px; font-size: 0.88rem; margin-bottom: 4px; transition: all 0.2s; }
    .nav-link:hover, .nav-link.active { background-color: rgba(255,255,255,0.1); color: #ffffff; font-weight: 600; }
    .sidebar-footer { padding: 20px 24px; font-size: 0.75rem; color: #86efac; border-top: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 8px; height: 8px; background-color: #16a34a; border-radius: 50%; }

    .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px; border-bottom: 1px solid #e2e8f0; background: white; width: 100%; box-sizing: border-box; }
    .page-title-header h1 { font-size: 1.4rem; color: #0f172a; margin: 0; }
    .page-title-header p { font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0; }
    .nav-actions { display: flex; align-items: center; gap: 16px; }
    .search-small { display: flex; align-items: center; background: #f1f5f9; padding: 8px 16px; border-radius: 8px; width: 280px; }
    .search-small input { border: none; background: transparent; outline: none; margin-left: 8px; font-size: 0.85rem; width: 100%; }
    .switch-role-btn { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: #f0fdf4; color: #16a34a; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 600; }
    .user-profile { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; }
    .avatar { width: 34px; height: 34px; background: #f0fdf4; color: #16a34a; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 0.9rem; }
    .user-name { font-weight: 600; color: #0f172a; font-size: 0.85rem; }
    .user-role { font-size: 0.72rem; color: #64748b; }
  `;
  document.head.appendChild(style);
}

function getEmployeeTabs() {
  return [
    { id: "index.html", title: "Help & Support", subtitle: "Employee Self-Service Support Portal", label: "Employee Home", icon: "ph-house", href: "index.html" },
    { id: "new-request.html", title: "New Support Request", subtitle: "Submit IT or HR Helpdesk Request", label: "New Support Request", icon: "ph-plus-circle", href: "new-request.html" },
    { id: "my-tickets.html", title: "My Tickets", subtitle: "Track Your Active Support Requests", label: "My Tickets", icon: "ph-ticket", href: "my-tickets.html" },
    { id: "leave-calendar.html", title: "Leave Calendar", subtitle: "Company Time Off & Holiday Events", label: "Leave Calendar", icon: "ph-calendar", href: "leave-calendar.html" },
    { id: "knowledge-base.html", title: "Knowledge Base", subtitle: "Company Policies & Self-Service Guides", label: "Knowledge Base", icon: "ph-book-open", href: "knowledge-base.html" },
    { id: "chat-history.html", title: "Genie Assistant Chat", subtitle: "Workplace AI Support Conversations", label: "Genie Assistant Chat", icon: "ph-chats-teardrop", href: "chat-history.html" },
    { id: "announcements.html", title: "Announcements", subtitle: "Company News & System Maintenance Notices", label: "Announcements", icon: "ph-megaphone", href: "announcements.html" },
    { id: "notifications.html", title: "Notifications", subtitle: "Ticket Status Updates & System Alerts", label: "Notifications", icon: "ph-bell", href: "notifications.html" },
    { id: "profile.html", title: "Profile & Credentials", subtitle: "User Details & Security Settings", label: "Profile", icon: "ph-user", href: "profile.html" },
  ];
}

function getEmployeeFilename() {
  return window.location.pathname.split("/").pop() || "index.html";
}

function renderEmployeeNMSidebar() {
  injectEmployeeNMComponentStyles();
  const sidebarContainer = document.getElementById("shared-sidebar");
  if (!sidebarContainer) return;

  const currentFile = getEmployeeFilename();
  const tabs = getEmployeeTabs();

  const navHtml = tabs.map(tab => `
    <a href="${tab.href}" class="nav-link ${currentFile === tab.href ? 'active' : ''}">
      <i class="ph-bold ${tab.icon}"></i>
      <span>${tab.label}</span>
    </a>
  `).join("");

  sidebarContainer.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="sidebar-header">
          <div class="brand-badge"><i class="ph-fill ph-user"></i></div>
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
        <div class="status-dot"></div>
        <span>Employee NM Online</span>
      </div>
    </aside>
  `;
}

function renderEmployeeNMTopNav() {
  injectEmployeeNMComponentStyles();
  const topNavContainer = document.getElementById("shared-topnav");
  if (!topNavContainer) return;

  const currentFile = getEmployeeFilename();
  const tabs = getEmployeeTabs();
  const activeTab = tabs.find(t => t.href === currentFile) || tabs[0];
  const user = JSON.parse(localStorage.getItem("portalUser") || '{"name":"Employee NM","role":"Employee"}');

  topNavContainer.innerHTML = `
    <header class="top-nav">
      <div class="page-title-header">
        <h1>${activeTab.title}</h1>
        <p>${activeTab.subtitle}</p>
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
          <div class="avatar"><i class="ph-bold ph-user"></i></div>
          <div>
            <div class="user-name">${user.name || "Employee NM"}</div>
            <div class="user-role">${user.role || "Staff Member"}</div>
          </div>
        </div>
      </div>
    </header>
  `;
}

// Auto-run on DOMReady without requiring parameters
document.addEventListener("DOMContentLoaded", () => {
  renderEmployeeNMSidebar();
  renderEmployeeNMTopNav();
});
