/* =========================================================
   TICKETGENIE - MAIN JAVASCRIPT & API CLIENT
   ========================================================= */

const API_BASE_URL = "/api";
const STORAGE_KEY = "ticketGenieTickets";

/* =========================================================
   BACKEND API CLIENT & STORAGE FALLBACK
   ========================================================= */
function getTickets() {
    const tickets = localStorage.getItem(STORAGE_KEY);
    if (!tickets) {
        const defaultTickets = [
            { id: "HD-1024", title: "Payroll Issue", category: "Payroll", priority: "High", status: "In Progress", description: "Having an issue with my latest paycheck.", date: "2026-08-08", createdAt: "2026-08-08T10:00:00" },
            { id: "HD-1025", title: "Benefits Question", category: "Benefits", priority: "Medium", status: "Open", description: "I have a question about my benefits.", date: "2026-08-07", createdAt: "2026-08-07T10:00:00" },
            { id: "HD-1026", title: "Laptop Request", category: "IT Support", priority: "Low", status: "Resolved", description: "Requesting a replacement laptop.", date: "2026-08-05", createdAt: "2026-08-05T10:00:00" },
            { id: "HD-1027", title: "PTO Request", category: "Time Off", priority: "Medium", status: "Pending", description: "Requesting PTO.", date: "2026-08-04", createdAt: "2026-08-04T10:00:00" },
            { id: "HD-1028", title: "Expense Reimbursement", category: "Payroll", priority: "Low", status: "Resolved", description: "Submitting an expense reimbursement.", date: "2026-08-02", createdAt: "2026-08-02T10:00:00" }
        ];
        return defaultTickets;
    }
    try {
        return JSON.parse(tickets);
    } catch (e) {
        return [];
    }
}

function saveTickets(tickets) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
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

async function apiFetchTickets(params = {}) {
    try {
        const query = new URLSearchParams();
        if (params.search) query.append("search", params.search);
        if (params.status && params.status !== "all") query.append("status", params.status);
        if (params.priority && params.priority !== "all") query.append("priority", params.priority);

        const url = query.toString() ? `${API_BASE_URL}/tickets?${query.toString()}` : `${API_BASE_URL}/tickets`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        return Array.isArray(data) ? data : (data.tickets || []);
    } catch (err) {
        console.warn("Backend API not reachable, using local storage tickets:", err);
    }
    return getTickets();
}

async function apiCreateTicket(ticketPayload) {
    try {
        const res = await fetch(`${API_BASE_URL}/tickets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticketPayload)
        });
        if (res.ok) {
            return await res.json();
        }
    } catch (err) {
        console.warn("Backend API POST failed, creating ticket locally:", err);
    }
    const tickets = getTickets();
    const newTicket = {
        id: generateTicketId(),
        title: ticketPayload.subject || ticketPayload.title,
        category: ticketPayload.category,
        priority: ticketPayload.priority || "Medium",
        status: "Open",
        description: ticketPayload.description,
        date: ticketPayload.date || "",
        createdAt: new Date().toISOString()
    };
    tickets.unshift(newTicket);
    saveTickets(tickets);
    return newTicket;
}

/* =========================================================
   PROFILE DROPDOWN MENU & TOP RIGHT PAGE SWITCHING
   ========================================================= */
function initializeProfileDropdown() {
    const profileBtn = document.getElementById('profileDropdownTrigger');
    const profileMenu = document.getElementById('profileDropdownMenu');
    const roleButtons = document.querySelectorAll('.role-switch-btn');
    const currentRoleDisplay = document.getElementById('currentRoleDisplay');

    if (profileBtn && profileMenu) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isShowing = profileMenu.classList.toggle('show');
            profileBtn.setAttribute('aria-expanded', isShowing);
        });

        document.addEventListener('click', (e) => {
            if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
                profileMenu.classList.remove('show');
                profileBtn.setAttribute('aria-expanded', 'false');
            }
        });

        roleButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const selectedRole = btn.getAttribute('data-role') || btn.dataset.role;
                roleButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (currentRoleDisplay) {
                    currentRoleDisplay.textContent = selectedRole;
                }

                profileMenu.classList.remove('show');
                profileBtn.setAttribute('aria-expanded', 'false');

                const currentPath = window.location.pathname;
                if (selectedRole === 'Management') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Management User', role: 'Management', email: 'management@ticketgenie.com' }));
                    if (currentPath.includes('/employee_NM/')) {
                        window.location.href = '../admin_AV/admin_dashboard.html';
                    } else if (currentPath.includes('/admin_AV/')) {
                        window.location.href = 'admin_dashboard.html';
                    } else if (currentPath.includes('/pages/')) {
                        window.location.href = 'management-portal.html';
                    } else {
                        window.location.href = 'admin_AV/admin_dashboard.html';
                    }
                } else if (selectedRole === 'Employee') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Employee User', role: 'Employee', email: 'employee@ticketgenie.com' }));
                    if (currentPath.includes('/admin_AV/')) {
                        window.location.href = '../employee_NM/index.html';
                    } else if (currentPath.includes('/pages/')) {
                        window.location.href = '../employee_NM/index.html';
                    } else if (currentPath.includes('/employee_NM/')) {
                        window.location.href = 'index.html';
                    } else {
                        window.location.href = 'employee_NM/index.html';
                    }
                }
            });
        });
    }
}

/* =========================================================
   NEW REQUEST FORM
   ========================================================= */
function initializeNewRequestForm() {
    const form = document.querySelector(".request-form-card form");
    if (!form) return;

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const titleElement = document.getElementById("ticketSubject") || document.getElementById("anonTicketSubject") || document.getElementById("leaveType");
        const categoryElement = document.getElementById("ticketCategory") || document.getElementById("anonTicketCategory") || document.getElementById("leaveType");
        const descriptionElement = document.getElementById("ticketDescription") || document.getElementById("anonTicketDescription") || document.getElementById("leaveDescription");
        
        const submitBtn = event.target.querySelector('.submit-request-button');

        const title = titleElement ? titleElement.value.trim() : "New Request";
        const category = categoryElement ? categoryElement.value : "General";
        const description = descriptionElement ? descriptionElement.value.trim() : "";

        if (!title || !category || !description) { 
            showFormError("Please fill out all required fields."); 
            return; 
        }

        const oldError = document.querySelector(".form-error-message");
        if (oldError) oldError.style.display = "none";

        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
            submitBtn.classList.add('loading');
        }

        const newTicket = await apiCreateTicket({
            title: title,
            subject: title,
            category: category,
            priority: "Medium",
            description: description,
            date: ""
        });

        showSuccessMessage(newTicket);

        setTimeout(() => { window.location.href = "my-tickets.html"; }, 1500);
    });
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
   MY TICKETS
   TICKET TO CHAT HISTORY NAVIGATION
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const clickableRows = document.querySelectorAll(".ticket-clickable");

    clickableRows.forEach(row => {
        row.addEventListener("click", () => {
            const ticketId = row.getAttribute("data-ticket-id");
            if (!ticketId) return;

            // Redirect to your chat-history.html page with the ticket query parameter
            window.location.href = `chat-history.html?ticket=${ticketId}`;
        });
    });
});

/* =========================================================
   P0 FEATURE API EXTENSIONS (ReAct, Document Export, Exec Actions, Comments)
   ========================================================= */

async function apiRunReAct(message, role = "Super Admin") {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/react`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, role }),
        });
        return await res.json();
    } catch (err) {
        console.error("ReAct agent execution failed:", err);
        return { reply: "ReAct Agent Engine execution failed. Check backend connection." };
    }
}

async function apiRunExecAction(command) {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/exec-agent`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command }),
        });
        return await res.json();
    } catch (err) {
        console.error("Executive action failed:", err);
        return { executive_response: "Executive command execution failed." };
    }
}

function getExportUrl(ticketId, format = "pdf") {
    return `${API_BASE_URL}/tickets/${ticketId}/export?format=${format}`;
}

async function apiGetComments(ticketId) {
    try {
        const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`);
        if (!res.ok) return [];
        return await res.json();
    } catch (err) {
        return [];
    }
}

async function apiPostComment(ticketId, message, senderRole = "Employee") {
    try {
        const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, sender_role: senderRole }),
        });
        return await res.json();
    } catch (err) {
        console.error("Failed to post comment:", err);
        return null;
    }
}

async function apiIngestKnowledge(category, title, content) {
    try {
        const res = await fetch(`${API_BASE_URL}/knowledge/ingest`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category, title, content }),
        });
        return await res.json();
    } catch (err) {
        console.error("Failed to ingest knowledge:", err);
        return { success: false };
    }
}
