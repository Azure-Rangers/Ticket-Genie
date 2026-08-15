/* =========================================================
   EMPLOYEE NM PORTAL - UNIFIED SHARED COMPONENTS
   Matches exact CSS classes in frontend/css/style.css
   ========================================================= */

function getEmployeePages() {
  return [
    { href: "index.html", title: "Help & Support" },
    { href: "new-request.html", title: "New Support Request" },
    { href: "my-tickets.html", title: "My Tickets" },
    { href: "leave-calendar.html", title: "Leave Calendar" },
    { href: "knowledge-base.html", title: "Knowledge Base" },
    { href: "chat-history.html", title: "Chat History" },
    { href: "announcements.html", title: "Announcements" },
    { href: "notifications.html", title: "Notifications" },
    { href: "profile.html", title: "Profile & Credentials" }
  ];
}

function getEmployeeCurrentFilename() {
  return window.location.pathname.split("/").pop() || "index.html";
}

function renderEmployeeNMSidebar() {
  const sidebarContainer = document.getElementById("shared-sidebar");
  if (!sidebarContainer) return;

  const currentFile = getEmployeeCurrentFilename();

  sidebarContainer.innerHTML = `
    <aside class="sidebar">
      <div class="brand" style="position: relative; justify-content: space-between; width: 100%; padding-right: 15px;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div class="brand-icon">
            <i class="fa-solid fa-ticket"></i>
          </div>
          <div>
            <h2>TicketGenie</h2>
            <span>Employee Portal</span>
          </div>
        </div>
        <button id="brandMenuToggle" class="brand-menu-toggle" aria-label="Toggle Pages">
          <i class="fa-solid fa-bars"></i>
        </button>
      </div>

      <nav class="navigation">
        <div class="nav-title">WORKSPACE</div>
        <a href="index.html" class="nav-item ${currentFile === 'index.html' ? 'active' : ''}">
          <i class="fa-solid fa-house"></i><span>Help & Support</span>
        </a>
        <a href="my-tickets.html" class="nav-item ${currentFile === 'my-tickets.html' ? 'active' : ''}">
          <i class="fa-solid fa-ticket"></i><span>My Tickets</span>
        </a>
        <a href="new-request.html" class="nav-item ${currentFile === 'new-request.html' ? 'active' : ''}">
          <i class="fa-solid fa-plus"></i><span>New Request</span>
        </a>
        <a href="chat-history.html" class="nav-item ${currentFile === 'chat-history.html' ? 'active' : ''}">
          <i class="fa-regular fa-comments"></i><span>Chat History</span>
        </a>

        <div class="nav-title">TIME OFF & COMPANY</div>
        <a href="leave-calendar.html" class="nav-item ${currentFile === 'leave-calendar.html' ? 'active' : ''}">
          <i class="fa-solid fa-calendar-days"></i><span>Leave Calendar</span>
        </a>
        <a href="announcements.html" class="nav-item ${currentFile === 'announcements.html' ? 'active' : ''}">
          <i class="fa-solid fa-bullhorn"></i><span>Announcements</span>
        </a>

        <div class="nav-title">RESOURCES</div>
        <a href="knowledge-base.html" class="nav-item ${currentFile === 'knowledge-base.html' ? 'active' : ''}">
          <i class="fa-solid fa-book-open"></i><span>Knowledge Base</span>
        </a>
        <a href="notifications.html" class="nav-item ${currentFile === 'notifications.html' ? 'active' : ''}">
          <i class="fa-solid fa-bell"></i><span>Notifications</span><span class="notification-count">3</span>
        </a>
        <a href="profile.html" class="nav-item ${currentFile === 'profile.html' ? 'active' : ''}">
          <i class="fa-solid fa-user-gear"></i><span>Profile & Credentials</span>
        </a>
      </nav>

      <div class="sidebar-bottom">
        <div class="system-status">
          <div class="status-dot"></div>
          <div><strong>All systems operational</strong><small>TicketGenie is online</small></div>
        </div>
      </div>
    </aside>
  `;
}

function renderEmployeeNMTopNav() {
  const topNavContainer = document.getElementById("shared-topnav");
  if (!topNavContainer) return;

  const currentFile = getEmployeeCurrentFilename();
  const pages = getEmployeePages();
  const activePage = pages.find(p => p.href === currentFile) || pages[0];

  topNavContainer.innerHTML = `
    <header class="topbar">
      <div class="header-left" style="display: flex; align-items: center; gap: 20px;">
        <button class="icon-button" id="sidebarToggle" type="button" aria-label="Toggle Sidebar">
          <i class="fa-solid fa-bars"></i>
        </button>
        <div class="page-title">
          <h1>${activePage.title}</h1>
        </div>
      </div>

      <div class="topbar-actions">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" placeholder="Search..." id="globalSearch">
          <span class="shortcut">⌘ K</span>
        </div>
        <button class="icon-button" id="darkModeToggle" type="button" aria-label="Toggle Dark Mode">
          <i class="fa-solid fa-moon" id="darkModeIcon"></i>
        </button>
        <button class="icon-button" type="button">
          <i class="fa-regular fa-bell"></i><span class="notification-dot"></span>
        </button>
        <div class="profile">
          <button class="profile-button" id="profileDropdownTrigger" aria-haspopup="menu" aria-expanded="false">
            <div class="avatar">NM</div>
            <div class="profile-info"><strong>Nishita</strong><span id="currentRoleDisplay">Employee</span></div>
            <i class="fa-solid fa-chevron-down"></i>
          </button>
        </div>
      </div>
    </header>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  renderEmployeeNMSidebar();
  renderEmployeeNMTopNav();
});
