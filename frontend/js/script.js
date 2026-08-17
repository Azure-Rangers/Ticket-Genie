console.log("[Script Log] TicketGenie main script.js loaded successfully!");

/* =========================================================
   GLOBAL DARK MODE & HAMBURGER SIDEBAR TOGGLES WITH LOGGING & EVENT DELEGATION
   ========================================================= */
function initDarkMode() {
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme === "dark";
    console.log("[Theme Log] Initializing dark mode. Saved theme in localStorage:", savedTheme);

    if (isDark) {
        document.body.classList.add("dark-mode");
    }

    const darkBtns = document.querySelectorAll("#myCustomDarkToggle, #darkModeToggle, .dark-mode-toggle");
    console.log("[Theme Log] Found dark mode toggle button count:", darkBtns.length);

    const activeDark = document.body.classList.contains("dark-mode");
    const moonSvg = document.getElementById("customMoon");
    const sunSvg = document.getElementById("customSun");
    if (moonSvg && sunSvg) {
        moonSvg.style.display = activeDark ? "none" : "inline-block";
        sunSvg.style.display = activeDark ? "inline-block" : "none";
    }
}

function initSidebarToggle() {
    const toggles = document.querySelectorAll("#sidebarToggle, #brandMenuToggle, .sidebar-toggle");
    console.log("[Sidebar Log] Initializing sidebar toggles. Found button count:", toggles.length);
}

// Global Fail-Safe Event Delegation
document.addEventListener("click", function(e) {
    const darkBtn = e.target.closest("#myCustomDarkToggle, #darkModeToggle, .dark-mode-toggle");
    if (darkBtn) {
        e.preventDefault();
        e.stopPropagation();
        document.body.classList.toggle("dark-mode");
        const activeDark = document.body.classList.contains("dark-mode");
        console.log("[Theme Log] Dark mode button clicked via event delegation. Active dark mode:", activeDark);
        localStorage.setItem("theme", activeDark ? "dark" : "light");

        const moonSvg = document.getElementById("customMoon");
        const sunSvg = document.getElementById("customSun");
        if (moonSvg && sunSvg) {
            moonSvg.style.display = activeDark ? "none" : "inline-block";
            sunSvg.style.display = activeDark ? "inline-block" : "none";
        }

        const moonIcon = document.getElementById("moonIcon");
        const sunIcon = document.getElementById("sunIcon");
        if (moonIcon && sunIcon) {
            moonIcon.style.display = activeDark ? "none" : "inline-block";
            sunIcon.style.display = activeDark ? "inline-block" : "none";
        }
        return;
    }

    const sidebarBtn = e.target.closest("#sidebarToggle, #brandMenuToggle, .sidebar-toggle");
    if (sidebarBtn) {
        e.preventDefault();
        e.stopPropagation();
        console.log("[Sidebar Log] Hamburger sidebar button clicked via event delegation.");
        document.body.classList.toggle("sidebar-collapsed");
        document.body.classList.toggle("sidebar-closed");
        
        const sidebar = document.querySelector(".sidebar") || document.getElementById("shared-sidebar");
        if (sidebar) {
            sidebar.classList.toggle("collapsed");
            console.log("[Sidebar Log] Toggled .collapsed class on sidebar element.");
        }
        return;
    }
});

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        initDarkMode();
        initSidebarToggle();
    });
} else {
    initDarkMode();
    initSidebarToggle();
}


document.addEventListener("DOMContentLoaded", () => {
    const clickableRows = document.querySelectorAll(".ticket-clickable");

    clickableRows.forEach(row => {
        row.addEventListener("click", () => {
            const ticketId = row.getAttribute("data-ticket-id");
            if (!ticketId) return;

            window.location.href = `chat-history.html?ticket=${ticketId}`;
        });
    });
});



/* =========================================================
   SIGN OUT HANDLER
========================================================= */
function handleSignOut(event) {
    event.preventDefault();
    if (confirm("Are you sure you want to sign out of TicketGenie Enterprise?")) {
        localStorage.removeItem('portalUser');
        window.location.href = "index.html";
    }
}

/* =========================================================
   INITIALIZE EVERYTHING
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    initializeProfileDropdown(); 
    initializeNewRequestForm();
    initializeMyTickets();
    initializeGenie();
    initializeKnowledgeBase();
    updateTicketOverview();
    initializeSidebarToggle();
    initializeFileUploads();
    initializeDarkMode();
});

function renderMyTickets(tickets) {
    const list = document.getElementById("myTicketsList");
    if (!list) return;

    if (!tickets || tickets.length === 0) {
        list.innerHTML = `
            <div style="padding: 24px; text-align: center; color: #64748b;">
                <strong>No requests found</strong>
                <p style="font-size: 13px; margin-top: 4px;">Your submitted requests will appear here.</p>
            </div>
        `;
        return;
    }

    list.innerHTML = tickets.map(ticket => {
        const id = escapeHTML(ticket.id || "HD-1000");
        const title = escapeHTML(ticket.title || ticket.subject || "Support Request");
        const category = escapeHTML(ticket.department || ticket.category || "HR & Operations");
        const priority = escapeHTML(ticket.priority || "Medium");
        const status = escapeHTML(ticket.status || "Open");
        const dateStr = escapeHTML(ticket.date || (ticket.createdAt ? ticket.createdAt.split("T")[0] : "Recently"));

        const pLower = priority.toLowerCase();
        let priorityBg = "#fef9e7", priorityFg = "#b8860b", priorityBorder = "#fde047";
        if (pLower === "high") { priorityBg = "#fef2f2"; priorityFg = "#ef4444"; priorityBorder = "#fca5a5"; }
        else if (pLower === "low") { priorityBg = "#f0fdf4"; priorityFg = "#10b981"; priorityBorder = "#a7f3d0"; }

        const sLower = status.toLowerCase();
        let statusBg = "#eff6ff", statusFg = "#3b82f6", statusBorder = "#bfdbfe";
        if (sLower === "resolved" || sLower === "closed") { statusBg = "#f0fdf4"; statusFg = "#10b981"; statusBorder = "#a7f3d0"; }
        else if (sLower === "in progress" || sLower === "pending") { statusBg = "#fef9e7"; statusFg = "#b8860b"; statusBorder = "#fde047"; }

        return `
            <div class="ticket-clickable" data-ticket-id="${id}" style="border-bottom: 1px solid #f1f5f9; border-left: 4px solid #d4a359; transition: background 0.1s; cursor: pointer;" onmouseover="this.style.background='#fafaf9'" onmouseout="this.style.background='#ffffff'" onclick="window.location.href='ticket-detail.html?ticket=${encodeURIComponent(id)}'">
                <div style="display: grid; grid-template-columns: 2.2fr 1.6fr 1fr 1fr 1fr 110px; gap: 16px; align-items: center; padding: 16px 20px;">
                    <div style="display: flex; align-items: center; gap: 14px; min-width: 0;">
                        <div style="width: 36px; height: 36px; background: #fef9e7; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #d4a359; font-size: 15px; flex-shrink: 0;"><i class="fa-solid fa-file-lines"></i></div>
                        <div style="min-width: 0;">
                            <strong style="font-size: 14px; color: #0f172a; display: block; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${title}</strong>
                            <span style="font-size: 12px; color: #d4a359; font-weight: 600;">#${id}</span>
                        </div>
                    </div>
                    <div style="font-size: 13px; color: #334155;">
                        <span style="padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; background: ${statusBg}; color: ${statusFg}; border: 1px solid ${statusBorder}; display: inline-block;">${category}</span>
                    </div>
                    <div>
                        <span style="padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; background: ${priorityBg}; color: ${priorityFg}; border: 1px solid ${priorityBorder}; display: inline-block;">${priority}</span>
                    </div>
                    <div style="font-size: 13px; color: #475569; font-weight: 500;">
                        ${status}
                    </div>
                    <div style="font-size: 13px; color: #64748b;">
                        ${dateStr}
                    </div>
                    <div style="text-align: right;">
                        <button type="button" onclick="event.stopPropagation(); window.location.href='ticket-detail.html?ticket=${encodeURIComponent(id)}'" style="background: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.15s;">
                            <i class="fa-regular fa-comments"></i> Chat
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

async function loadDashboardTickets() {
    const container = document.getElementById("recentTicketsContainer");
    let tickets = await apiFetchTickets({ requesterId: getCurrentRequesterId() }); if (!tickets || tickets.length === 0) tickets = getTickets();

    const openCount = tickets.filter(t => (t.status || "").toLowerCase() === "open").length;
    const inProgCount = tickets.filter(t => ["in progress", "pending"].includes((t.status || "").toLowerCase())).length;
    const resolvedCount = tickets.filter(t => ["resolved", "closed"].includes((t.status || "").toLowerCase())).length;

    const elOpen = document.getElementById("countOpen");
    const elInProg = document.getElementById("countInProgress");
    const elResolved = document.getElementById("countResolved");

    if (elOpen) elOpen.textContent = openCount;
    if (elInProg) elInProg.textContent = inProgCount;
    if (elResolved) elResolved.textContent = resolvedCount;

    if (!container) return;

    if (!tickets || tickets.length === 0) {
        container.innerHTML = `
            <div style="padding: 24px; text-align: center; color: #64748b;">
                No recent support requests found.
            </div>
        `;
        return;
    }

    const headerHTML = `
        <div style="display: grid; grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr; gap: 16px; padding: 0 16px 8px 16px; font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; box-sizing: border-box; width: 100%;">
            <div>Request</div>
            <div>Department</div>
            <div>Status</div>
            <div>Priority</div>
            <div>Date</div>
        </div>
    `;

    const rowsHTML = tickets.slice(0, 5).map(t => {
        const id = escapeHTML(t.id || "HD-1000");
        const title = escapeHTML(t.title || t.subject || "Support Request");
        const dept = escapeHTML(t.department || t.category || "General Operations");
        const status = escapeHTML(t.status || "Open");
        const priority = escapeHTML(t.priority || "Medium");
        const dateStr = escapeHTML(t.date || (t.createdAt ? t.createdAt.split("T")[0] : "Recently"));

        return `
            <div class="ticket-clickable" onclick="window.location.href='ticket-detail.html?ticket=${encodeURIComponent(id)}'" style="display: grid; grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr; gap: 16px; align-items: center; padding: 14px 16px; background: #faf7fc; border: 1px solid #e1e6e2; border-radius: 6px; font-size: 13px; box-sizing: border-box; width: 100%; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 12px; min-width: 0;">
                    <div style="width: 32px; height: 32px; background: #fef9e7; color: #b8860b; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"><i class="fa-solid fa-file-lines"></i></div>
                    <div style="min-width: 0;">
                        <strong style="color: #1e293b; display: block; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${title}</strong>
                        <span style="font-size: 11px; color: #64748b;">#${id}</span>
                    </div>
                </div>
                <div style="color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${dept}</div>
                <div><span style="background: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block;">${status}</span></div>
                <div><span style="background: #fef9e7; color: #b8860b; border: 1px solid #fde047; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block;">${priority}</span></div>
                <div style="color: #64748b; white-space: nowrap;">${dateStr}</div>
            </div>
        `;
    }).join("");

    container.innerHTML = headerHTML + rowsHTML;
}

document.addEventListener("DOMContentLoaded", () => {
    initDarkMode();
    initSidebarToggle();
    loadDashboardTickets();
    initializeMyTickets();
});


/* =========================================================
   NEW TICKET FORM SUBMISSIONS
========================================================= */
async function submitStandardTicket(event) {
    if (event) event.preventDefault();
    
    const subjectEl = document.getElementById("standardSubject");
    const deptEl = document.getElementById("standardDepartment");
    const descEl = document.getElementById("standardDescription");
    
    const subject = subjectEl ? subjectEl.value.trim() : "";
    const department = deptEl ? deptEl.value : "IT & Technology";
    const description = descEl ? descEl.value.trim() : "";
    
    if (!subject || !description) {
        showNotification("Please enter a Request Title / Subject and Description before submitting.", "warning");
        return;
    }

    const submitBtn = document.getElementById("submitStandardBtn");
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" style="margin-right:6px;"></i> Submitting...';
    }

    let backendDept = null;
    if (department && department !== "Auto") {
        if (department.includes("HR")) backendDept = "HR Team";
        else if (department.includes("Account")) backendDept = "Accounting Team";
        else if (department.includes("Upper") || department.includes("Admin")) backendDept = "Upper Management";
        else if (department.includes("Workplace")) backendDept = "Workplace Operations Team";
        else backendDept = "IT Team";
    }

    const payload = {
        title: subject,
        description: description,
        category: "IT Support",
        priority: "Medium",
        department: backendDept,
        requester_id: typeof getCurrentRequesterId === 'function' ? getCurrentRequesterId() : "nm@company.com"
    };

    const newTicket = await apiCreateTicket(payload);
    
    // Save locally for fallback rendering
    const tickets = getTickets();
    const existingIndex = tickets.findIndex(t => t.id === newTicket.id);
    if (existingIndex < 0) {
        tickets.unshift(newTicket);
        saveTickets(tickets);
    }

    alert(`Ticket #${newTicket.id || "HD-1029"} submitted successfully!`);
    window.location.href = "my-tickets.html";
}

window.submitStandardTicket = submitStandardTicket;
