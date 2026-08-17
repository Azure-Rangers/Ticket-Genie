console.log("[Script Log] TicketGenie main script.js loaded successfully!");

/* =========================================================
   AUTO-LOAD DEPENDENCIES & TELEMETRY
   ========================================================= */
(function autoLoadDependencies() {
    if (!window.apiFetchAnnouncements) {
        const scriptElement = document.querySelector('script[src*="script.js"]');
        const basePath = scriptElement ? scriptElement.src.replace("script.js", "") : "/js/";
        const apiScript = document.createElement("script");
        apiScript.src = basePath + "api.js";
        document.head.appendChild(apiScript);
    }
})();

(function autoLoadTelemetry() {
    if (window.TicketGenieTelemetry) return;
    const script = document.createElement("script");
    const scriptElement = document.querySelector('script[src*="script.js"]');
    const basePath = scriptElement ? scriptElement.src.replace("script.js", "") : "/js/";
    script.src = basePath + "telemetry.js";
    script.async = true;
    document.head.appendChild(script);
})();

/* =========================================================
   LOCAL STORAGE FALLBACK & IDENTIFIER HELPERS
   ========================================================= */
const STORAGE_KEY = "ticketGenieTickets";

function getTickets() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY) || localStorage.getItem("employee_tickets");
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed) && parsed.length > 0) return parsed;
        }
    } catch (e) {}

    return [
        { id: "HD-1024", title: "Payroll Issue", category: "Payroll", priority: "High", status: "In Progress", description: "Having an issue with my latest paycheck.", date: "2026-08-08", createdAt: "2026-08-08T10:00:00" },
        { id: "HD-1025", title: "Benefits Question", category: "Benefits", priority: "Medium", status: "Open", description: "I have a question about my benefits.", date: "2026-08-07", createdAt: "2026-08-07T10:00:00" },
        { id: "HD-1026", title: "Laptop Request", category: "IT Support", priority: "Low", status: "Resolved", description: "Requesting a replacement laptop.", date: "2026-08-05", createdAt: "2026-08-05T10:00:00" },
        { id: "HD-1027", title: "PTO Request", category: "Time Off", priority: "Medium", status: "Pending", description: "Requesting PTO.", date: "2026-08-04", createdAt: "2026-08-04T10:00:00" },
        { id: "HD-1028", title: "Expense Reimbursement", category: "Payroll", priority: "Low", status: "Resolved", description: "Submitting an expense reimbursement.", date: "2026-08-02", createdAt: "2026-08-02T10:00:00" }
    ];
}

function saveTickets(tickets) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
        localStorage.setItem("employee_tickets", JSON.stringify(tickets));
    } catch (e) {}
}

function generateTicketId() {
    const tickets = getTickets();
    let highestNumber = 1028;
    tickets.forEach(ticket => {
        const number = parseInt(String(ticket.id).replace("HD-", ""), 10);
        if (!isNaN(number) && number > highestNumber) {
            highestNumber = number;
        }
    });
    return `HD-${highestNumber + 1}`;
}

function getCurrentRequesterId() {
    try {
        const user = JSON.parse(localStorage.getItem("portalUser") || "{}");
        return user.email || user.id || "nm@company.com";
    } catch (e) {
        return "nm@company.com";
    }
}

function escapeHTML(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showNotification(message, type = "info") {
    console.log(`[Notification - ${type}] ${message}`);
    let toast = document.getElementById("globalToastNotification");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "globalToastNotification";
        toast.style.cssText = "position: fixed; bottom: 24px; right: 24px; z-index: 9999; background: #1e293b; color: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); font-size: 14px; transition: opacity 0.3s ease;";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = "1";
    setTimeout(() => { toast.style.opacity = "0"; }, 3500);
}

function showFormError(message) {
    const error = document.getElementById("formErrorMessage");
    if (!error) return;
    error.textContent = message;
    error.style.display = "block";
    error.scrollIntoView({ behavior: "smooth", block: "center" });
}

function showSuccessMessage(ticket) {
    let success = document.getElementById("ticketSuccessMessage");
    if (!success) {
        success = document.createElement("div");
        success.id = "ticketSuccessMessage";
        success.className = "ticket-success-message";
        document.body.appendChild(success);
    }

    success.innerHTML = `
        <div class="success-icon"><i class="fa-solid fa-check"></i></div>
        <div>
            <strong>Request submitted successfully</strong>
            <span>Ticket #${escapeHTML(ticket.id)} has been created.</span>
        </div>
    `;

    requestAnimationFrame(() => { success.classList.add("show"); });
    setTimeout(() => { success.classList.remove("show"); }, 3000);
}

/* =========================================================
   GLOBAL DARK MODE & HAMBURGER SIDEBAR TOGGLES
   ========================================================= */
function initDarkMode() {
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme === "dark";
    if (isDark) {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.remove("dark-mode");
    }

    const darkToggle = document.getElementById("myCustomDarkToggle") || document.getElementById("darkModeToggle");
    if (darkToggle) {
        darkToggle.setAttribute("aria-checked", isDark ? "true" : "false");
    }
}

function initSidebarToggle() {
    const sidebar = document.querySelector(".sidebar");
    const savedState = localStorage.getItem("sidebar_collapsed");
    if (sidebar && savedState === "true") {
        sidebar.classList.add("collapsed");
    }
}

function handleSignOut(event) {
    if (event) event.preventDefault();
    localStorage.removeItem("portalUser");
    window.location.href = "../index.html";
}

/* =========================================================
   MODAL CHAT & TICKET CHAT UTILITIES
   ========================================================= */
let currentOpenTicketId = null;
let loadedMyTicketsMap = {};

async function openTicketChatModal(ticketId, ticketObj = null) {
    const modal = document.getElementById("ticketModal");
    if (!modal) return;

    currentOpenTicketId = ticketId;

    let ticket = ticketObj || loadedMyTicketsMap[ticketId];
    if (!ticket) {
        try {
            const fetchFn = window.apiFetchTickets || apiFetchTickets;
            const res = await fetchFn({ search: ticketId });
            if (res && res.length > 0) ticket = res[0];
        } catch (e) {}
    }

    const modalTitle = document.getElementById("modalTicketTitle");
    const modalId = document.getElementById("modalTicketId");
    const modalStatus = document.getElementById("modalTicketStatus");
    const modalCategory = document.getElementById("modalTicketCategory");
    const modalPriority = document.getElementById("modalTicketPriority");
    const modalDate = document.getElementById("modalTicketDate");
    const modalDesc = document.getElementById("modalTicketDescription");

    if (modalTitle) modalTitle.textContent = ticket ? ticket.title : `Ticket #${ticketId}`;
    if (modalId) modalId.textContent = `#${ticketId}`;

    if (modalStatus) {
        const st = ticket ? (ticket.status || "Open") : "Open";
        modalStatus.textContent = st;
        modalStatus.className = `status ${st.toLowerCase().replaceAll(" ", "-")}`;
    }

    if (modalCategory) modalCategory.textContent = ticket ? (ticket.department || ticket.category || "General") : "General";

    if (modalPriority) {
        const pr = ticket ? (ticket.priority || "Medium") : "Medium";
        modalPriority.textContent = pr;
        modalPriority.className = `priority ${pr.toLowerCase()}`;
    }

    if (modalDate) modalDate.textContent = ticket ? (ticket.date || (ticket.createdAt ? ticket.createdAt.split("T")[0] : "Today")) : "Today";
    if (modalDesc) modalDesc.textContent = ticket ? (ticket.description || "No description provided.") : "No description provided.";

    await renderModalComments(ticketId);

    modal.style.display = "flex";
    requestAnimationFrame(() => modal.classList.add("show"));

    const threadContainer = document.getElementById("modalChatThread");
    if (threadContainer) threadContainer.scrollTop = threadContainer.scrollHeight;
}

async function renderModalComments(ticketId) {
    const threadContainer = document.getElementById("modalChatThread");
    if (!threadContainer) return;

    const getCommentsFn = window.apiGetComments || (async () => []);
    const comments = await getCommentsFn(ticketId);

    if (!comments || comments.length === 0) {
        threadContainer.innerHTML = `
            <div style="text-align: center; color: #8a7896; font-size: 12px; padding: 20px; background: #faf7fc; border-radius: 8px;">
                <i class="fa-regular fa-comments" style="font-size: 1.5rem; margin-bottom: 6px; display: block; color: #b4a2c0;"></i>
                No messages from HR yet. Type below to send a message to support.
            </div>
        `;
        return;
    }

    threadContainer.innerHTML = comments.map(c => {
        const isEmployee = (c.sender_role || "").toLowerCase() === "employee";
        const senderRoleText = c.sender_role || (isEmployee ? "Employee" : "HR Support");
        const timeText = c.createdAt ? c.createdAt.replace("T", " ").substring(0, 16) : "Just now";

        if (isEmployee) {
            return `
                <div class="chat-msg-bubble-wrapper employee-msg">
                    <div class="chat-msg-header">
                        <span class="chat-msg-time">${escapeHTML(timeText)}</span>
                        <span>You (${escapeHTML(senderRoleText)})</span>
                    </div>
                    <div class="chat-bubble-content">
                        ${escapeHTML(c.message)}
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="chat-msg-bubble-wrapper hr-msg">
                    <div class="chat-msg-header">
                        <span class="chat-msg-badge"><i class="fa-solid fa-user-shield"></i> ${escapeHTML(senderRoleText)}</span>
                        <span class="chat-msg-time">${escapeHTML(timeText)}</span>
                    </div>
                    <div class="chat-bubble-content">
                        ${escapeHTML(c.message)}
                    </div>
                </div>
            `;
        }
    }).join("");

    threadContainer.scrollTop = threadContainer.scrollHeight;
}

function closeTicketChatModal() {
    const modal = document.getElementById("ticketModal");
    if (!modal) return;
    modal.classList.remove("show");
    setTimeout(() => { modal.style.display = "none"; }, 200);
}

async function submitModalComment() {
    const chatInput = document.getElementById("modalChatInput");
    if (!chatInput || !currentOpenTicketId) return;
    const msg = chatInput.value.trim();
    if (!msg) return;

    chatInput.value = "";
    
    const postFn = window.apiPostComment || (async () => null);
    await postFn(currentOpenTicketId, msg, "Employee");
    await renderModalComments(currentOpenTicketId);
}

async function initializeMyTickets() {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    list.innerHTML = '<div class="table-row"><div>Loading tickets...</div></div>';
    const fetchFn = window.apiFetchTickets || (async () => getTickets());
    const tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    renderMyTickets(tickets);
}

function renderMyTickets(tickets) {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    if (!tickets || tickets.length === 0) {
        list.innerHTML = '<div class="table-row"><div>No tickets found.</div></div>';
        return;
    }
    loadedMyTicketsMap = {};
    list.innerHTML = tickets.map(t => {
        loadedMyTicketsMap[t.id] = t;
        const stClass = (t.status || "Open").toLowerCase().replaceAll(" ", "-");
        const prClass = (t.priority || "Medium").toLowerCase();
        return `
            <div class="table-row" onclick="openTicketChatModal('${escapeHTML(t.id)}')">
                <div><strong>#${escapeHTML(t.id)}</strong></div>
                <div>${escapeHTML(t.title || "Untitled")}</div>
                <div><span class="badge status-${stClass}">${escapeHTML(t.status || "Open")}</span></div>
                <div><span class="badge priority-${prClass}">${escapeHTML(t.priority || "Medium")}</span></div>
                <div>${escapeHTML(t.date || "Today")}</div>
            </div>
        `;
    }).join("");
}

/* =========================================================
   EMPLOYEE PORTAL SPECIFIC LOADERS
   ========================================================= */
async function loadDashboardTickets() {
    const tableBody = document.querySelector(".table-container table tbody");
    if (!tableBody) return;
    const fetchFn = window.apiFetchTickets || (async () => getTickets());
    let tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    if (!tickets || tickets.length === 0) tickets = getTickets();

    tableBody.innerHTML = tickets.slice(0, 5).map(t => `
        <tr onclick="window.location.href='ticket-detail.html?id=${encodeURIComponent(t.id)}'" style="cursor: pointer;">
            <td><strong>#${escapeHTML(t.id)}</strong></td>
            <td>${escapeHTML(t.title || "Untitled")}</td>
            <td>${escapeHTML(t.department || t.category || "General")}</td>
            <td><span class="status-pill status-${(t.status || "Open").toLowerCase().replaceAll(" ", "-")}">${escapeHTML(t.status || "Open")}</span></td>
            <td><span class="priority-pill priority-${(t.priority || "Medium").toLowerCase()}">${escapeHTML(t.priority || "Medium")}</span></td>
            <td>${escapeHTML(t.date || "Today")}</td>
        </tr>
    `).join("");
}

async function loadMyTicketsPage() {
    const tableBody = document.querySelector(".table-container table tbody");
    if (!tableBody) return;
    const fetchFn = window.apiFetchTickets || (async () => getTickets());
    let tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    if (!tickets || tickets.length === 0) tickets = getTickets();

    tableBody.innerHTML = tickets.map(t => `
        <tr onclick="window.location.href='ticket-detail.html?id=${encodeURIComponent(t.id)}'" style="cursor: pointer;">
            <td><strong>#${escapeHTML(t.id)}</strong></td>
            <td>${escapeHTML(t.title || "Untitled")}</td>
            <td>${escapeHTML(t.department || t.category || "General")}</td>
            <td><span class="status-pill status-${(t.status || "Open").toLowerCase().replaceAll(" ", "-")}">${escapeHTML(t.status || "Open")}</span></td>
            <td><span class="priority-pill priority-${(t.priority || "Medium").toLowerCase()}">${escapeHTML(t.priority || "Medium")}</span></td>
            <td>${escapeHTML(t.date || "Today")}</td>
        </tr>
    `).join("");
}

async function loadTicketDetailPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get("id") || "HD-1024";

    const fetchFn = window.apiFetchTickets || (async () => getTickets());
    let tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    let ticket = (tickets || []).find(t => String(t.id) === String(ticketId)) || getTickets()[0];

    const titleEl = document.getElementById("ticketDetailTitle");
    const idEl = document.getElementById("ticketDetailId");
    const statusEl = document.getElementById("ticketDetailStatus");
    const priorityEl = document.getElementById("ticketDetailPriority");
    const descEl = document.getElementById("ticketDetailDescription");

    if (titleEl) titleEl.textContent = ticket.title || "Ticket Detail";
    if (idEl) idEl.textContent = `#${ticket.id}`;
    if (statusEl) {
        statusEl.textContent = ticket.status || "Open";
        statusEl.className = `status-pill status-${(ticket.status || "Open").toLowerCase().replaceAll(" ", "-")}`;
    }
    if (priorityEl) {
        priorityEl.textContent = ticket.priority || "Medium";
        priorityEl.className = `priority-pill priority-${(ticket.priority || "Medium").toLowerCase()}`;
    }
    if (descEl) descEl.textContent = ticket.description || "No description provided.";

    const getCommentsFn = window.apiGetComments || (async () => []);
    const comments = await getCommentsFn(ticketId);
    const threadContainer = document.getElementById("ticketCommentsThread");
    if (threadContainer && comments && comments.length > 0) {
        threadContainer.innerHTML = comments.map(c => `
            <div class="comment-bubble ${c.sender_role === "Employee" ? "user-bubble" : "support-bubble"}">
                <div class="comment-header">
                    <strong>${escapeHTML(c.sender_role || "Support")}</strong>
                    <small>${escapeHTML(c.createdAt ? c.createdAt.substring(0, 10) : "Today")}</small>
                </div>
                <div class="comment-body">${escapeHTML(c.message)}</div>
            </div>
        `).join("");
    }
}

async function submitStandardTicket(event) {
    if (event) event.preventDefault();
    const titleEl = document.getElementById("ticketTitle");
    const deptEl = document.getElementById("ticketDepartment");
    const priorityEl = document.getElementById("ticketPriority");
    const descEl = document.getElementById("ticketDescription");

    const payload = {
        title: titleEl ? titleEl.value.trim() : "New Support Request",
        department: deptEl ? deptEl.value : "IT Support",
        priority: priorityEl ? priorityEl.value : "Medium",
        description: descEl ? descEl.value.trim() : "",
        requester_id: getCurrentRequesterId()
    };

    const createFn = window.apiCreateTicket || apiCreateTicket;
    const result = await createFn(payload);
    showNotification("Ticket submitted successfully!", "success");
    setTimeout(() => { window.location.href = "my-tickets.html"; }, 1000);
}

async function sendTicketReply(ticketId) {
    const replyInput = document.getElementById("replyMessageInput");
    if (!replyInput) return;
    const msg = replyInput.value.trim();
    if (!msg) return;

    replyInput.value = "";
    const postFn = window.apiPostComment || apiPostComment;
    await postFn(ticketId, msg, "Employee");
    await loadTicketDetailPage();
}

/* =========================================================
   GLOBAL INITIALIZER LISTENERS
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    initDarkMode();
    initSidebarToggle();

    // Floating Genie Chat Drawer events
    const genieBtn = document.getElementById("genieButton");
    const genieChat = document.getElementById("genieChat");
    const closeGenieBtn = document.getElementById("closeGenieButton");
    const genieSendBtn = document.getElementById("genieSendButton");
    const genieInput = document.getElementById("genieInput");

    if (genieBtn && genieChat) {
        genieBtn.addEventListener("click", () => { genieChat.classList.toggle("open"); });
    }
    if (closeGenieBtn && genieChat) {
        closeGenieBtn.addEventListener("click", () => { genieChat.classList.remove("open"); });
    }

    async function sendGenieMsg() {
        if (!genieInput) return;
        const genieMessages = document.getElementById("genieMessages");
        const msg = genieInput.value.trim();
        if (!msg || !genieMessages) return;

        const userDiv = document.createElement("div");
        userDiv.className = "genie-message user-message";
        userDiv.style.cssText = "display:flex; justify-content:flex-end; margin-bottom:12px;";
        userDiv.innerHTML = `<div class="genie-bubble" style="background:#4f46e5; color:white; border-radius:12px; padding:10px 14px;">${escapeHTML(msg)}</div>`;
        genieMessages.appendChild(userDiv);

        genieInput.value = "";
        genieMessages.scrollTop = genieMessages.scrollHeight;

        const chatFn = window.apiGenieChat || apiGenieChat;
        const res = await chatFn(msg);

        const botDiv = document.createElement("div");
        botDiv.className = "genie-message";
        botDiv.style.marginBottom = "12px";
        botDiv.innerHTML = `
            <div class="genie-message-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
            <div class="genie-bubble">${escapeHTML(res.reply)}</div>
        `;
        genieMessages.appendChild(botDiv);
        genieMessages.scrollTop = genieMessages.scrollHeight;
    }

    if (genieSendBtn) genieSendBtn.addEventListener("click", sendGenieMsg);
    if (genieInput) {
        genieInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendGenieMsg();
        });
    }
});

// Bind all global utilities to window
Object.assign(window, {
    STORAGE_KEY,
    getTickets,
    saveTickets,
    generateTicketId,
    getCurrentRequesterId,
    escapeHTML,
    showNotification,
    showFormError,
    showSuccessMessage,
    initDarkMode,
    initSidebarToggle,
    handleSignOut,
    openTicketChatModal,
    renderModalComments,
    closeTicketChatModal,
    submitModalComment,
    initializeMyTickets,
    renderMyTickets,
    loadDashboardTickets,
    loadMyTicketsPage,
    loadTicketDetailPage,
    submitStandardTicket,
    sendTicketReply
});
