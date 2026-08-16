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

function getCurrentRequesterId() {
    try {
        const user = JSON.parse(localStorage.getItem("portalUser") || "{}");
        return user.email || user.id || "nm@company.com";
    } catch (err) {
        return "nm@company.com";
    }
}

async function apiFetchTickets(params = {}) {
    try {
        const query = new URLSearchParams();
        if (params.search) query.append("search", params.search);
        if (params.status && params.status !== "all") query.append("status", params.status);
        if (params.priority && params.priority !== "all") query.append("priority", params.priority);
        if (params.requesterId) query.append("requester_id", params.requesterId);

        const url = query.toString() ? `${API_BASE_URL}/tickets?${query.toString()}` : `${API_BASE_URL}/tickets`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        return Array.isArray(data) ? data : (data.tickets || []);
    } catch (err) {
        console.warn("Backend API not reachable; no server tickets can be displayed:", err);
    }
    return [];
}

async function apiCreateTicket(ticketPayload) {
    let res;
    try {
        res = await fetch(`${API_BASE_URL}/tickets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticketPayload)
        });
    } catch (err) {
        throw new Error("Unable to reach TicketGenie. Please check the connection and try again.");
    }

    if (!res.ok) {
        let detail = `Ticket submission failed (${res.status}).`;
        try {
            const errorBody = await res.json();
            if (typeof errorBody.detail === "string") detail = errorBody.detail;
            if (Array.isArray(errorBody.detail)) {
                detail = errorBody.detail.map(item => item.msg).filter(Boolean).join(" ") || detail;
            }
        } catch (err) {
            // Keep the status-based message when the server did not return JSON.
        }
        throw new Error(detail);
    }

    return await res.json();
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
    const formConfigs = {
        newTicketForm: { title: "ticketSubject", category: "ticketCategory", description: "ticketDescription", preferredDate: "preferredDate", file: "fileUpload", anonymous: false },
        anonTicketForm: { title: "anonTicketSubject", category: "anonTicketCategory", description: "anonTicketDescription", file: "anonFileUpload", anonymous: true },
        leaveTicketForm: { title: "leaveType", category: "leaveType", description: "leaveDescription", preferredDate: "leaveEndDate", file: "leaveFileUpload", anonymous: false, leave: true, departmentOverride: "Upper Management" }
    };

    Object.entries(formConfigs).forEach(([formId, config]) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const titleElement = document.getElementById(config.title);
        const categoryElement = document.getElementById(config.category);
        const descriptionElement = document.getElementById(config.description);
        const submitBtn = event.target.querySelector('.submit-request-button');
        const originalSubmitContent = submitBtn?.innerHTML;

        const title = titleElement ? titleElement.value.trim() : "New Request";
        const category = categoryElement ? categoryElement.value : "General";
        const description = descriptionElement ? descriptionElement.value.trim() : "";

        if (!title || !category || !description) {
            showFormError("Please fill out all required fields.");
            return;
        }
        if (title.length < 3 || description.length < 10) {
            showFormError("The subject must be at least 3 characters and the description at least 10 characters.");
            return;
        }

        const oldError = document.querySelector(".form-error-message");
        if (oldError) oldError.style.display = "none";

        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
            submitBtn.classList.add('loading');
        }

        try {
            let finalDescription = description;
            if (config.leave) {
                const startDate = document.getElementById("leaveStartDate")?.value || "";
                const endDate = document.getElementById("leaveEndDate")?.value || "";
                finalDescription = `Leave dates: ${startDate} to ${endDate}. ${description}`;
            }
            const files = Array.from(document.getElementById(config.file)?.files || []);
            const newTicket = await apiCreateTicket({
                title,
                category,
                description: finalDescription,
                preferredDate: config.preferredDate ? (document.getElementById(config.preferredDate)?.value || null) : null,
                is_anonymous: config.anonymous,
                attachment: files.length ? files.map(file => file.name).join(", ") : null,
                requester_id: getCurrentRequesterId(),
                // Deterministic, fixed to this one static tab - never derived
                // from chatbot/GPT output. Makes the backend skip normal AI
                // classification for Leave Management (see
                // services/ticket_service.py's department_override handling)
                // so it always routes to Upper Management.
                ...(config.departmentOverride ? { department_override: config.departmentOverride } : {})
            });

            showSuccessMessage(newTicket);
            setTimeout(() => { window.location.href = "my-tickets.html"; }, 1500);
        } catch (err) {
            showFormError(err.message || "Unable to submit the request. Please try again.");
            if (submitBtn) {
                submitBtn.innerHTML = originalSubmitContent;
                submitBtn.classList.remove('loading');
            }
        }
        });
    });
}

function renderMyTickets(tickets) {
    const list = document.getElementById("myTicketsList");
    if (!list) return;

    if (!tickets.length) {
        list.innerHTML = '<div class="table-row"><div class="request-info"><div><strong>No tickets found</strong><span>Your submitted requests will appear here.</span></div></div></div>';
        return;
    }

    list.innerHTML = tickets.map(ticket => `
        <div class="table-row ticket-clickable" data-ticket-id="${escapeHTML(ticket.id)}">
            <div class="request-info">
                <div class="request-icon"><i class="fa-solid fa-file-lines"></i></div>
                <div><strong>${escapeHTML(ticket.title)}</strong><span>#${escapeHTML(ticket.id)}</span></div>
            </div>
            <div>${escapeHTML(ticket.department || ticket.category)}</div>
            <div><span class="status ${escapeHTML(String(ticket.status || "open").toLowerCase().replaceAll(" ", "-"))}">${escapeHTML(ticket.status)}</span></div>
            <div><span class="priority ${escapeHTML(String(ticket.priority || "medium").toLowerCase())}">${escapeHTML(ticket.priority)}</span></div>
            <div>${escapeHTML(ticket.date || "")}</div>
        </div>
    `).join("");

    list.querySelectorAll(".ticket-clickable").forEach(row => {
        row.addEventListener("click", () => {
            window.location.href = `chat-history.html?ticket=${encodeURIComponent(row.dataset.ticketId)}`;
        });
    });
}

async function initializeMyTickets() {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    list.innerHTML = '<div class="table-row"><div>Loading tickets...</div></div>';
    const tickets = await apiFetchTickets({ requesterId: getCurrentRequesterId() });
    renderMyTickets(tickets);
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
    initializeProfileDropdown();
    initializeNewRequestForm();
    initializeMyTickets();
    applyPendingGenieDraft();

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

async function apiUpdateTicket(ticketId, ticketUpdate) {
    try {
        const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticketUpdate)
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to update ticket:", err);
    }
    return null;
}

async function apiFetchAnnouncements() {
    try {
        const res = await fetch(`${API_BASE_URL}/announcements`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to fetch announcements:", err);
    }
    return [];
}

async function apiCreateAnnouncement(payload) {
    try {
        const res = await fetch(`${API_BASE_URL}/announcements`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to create announcement:", err);
    }
    return null;
}

async function apiDeleteAnnouncement(ancId) {
    try {
        const res = await fetch(`${API_BASE_URL}/announcements/${ancId}`, { method: "DELETE" });
        return res.ok;
    } catch (err) {
        console.error("Failed to delete announcement:", err);
    }
    return false;
}

async function apiFetchNotifications() {
    try {
        const res = await fetch(`${API_BASE_URL}/notifications`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to fetch notifications:", err);
    }
    return [];
}

async function apiMarkNotificationRead(notifId) {
    try {
        const res = await fetch(`${API_BASE_URL}/notifications/${notifId}/read`, { method: "PUT" });
        return res.ok;
    } catch (err) {
        console.error("Failed to mark notification read:", err);
    }
    return false;
}

async function apiFetchOnboarding() {
    try {
        const res = await fetch(`${API_BASE_URL}/onboarding`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to fetch onboarding records:", err);
    }
    return [];
}

async function apiCreateOnboarding(payload) {
    try {
        const res = await fetch(`${API_BASE_URL}/onboarding`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to create onboarding record:", err);
    }
    return null;
}

async function apiUpdateOnboardingStatus(recId, status) {
    try {
        const res = await fetch(`${API_BASE_URL}/onboarding/${recId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status })
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to update onboarding record:", err);
    }
    return null;
}

async function apiFetchUserProfile() {
    try {
        const res = await fetch(`${API_BASE_URL}/users/profile`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to fetch user profile:", err);
    }
    return { name: "Nishita", email: "nishita@ticketgenie.com", role: "Employee", department: "HR & Operations", phone: "+1 (555) 019-2834" };
}

async function apiUpdateUserProfile(payload) {
    try {
        const res = await fetch(`${API_BASE_URL}/users/profile`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to update user profile:", err);
    }
    return null;
}

/* =========================================================
   GENIE CHATBOT (real backend integration)
   Talks to the actual chatbot endpoint (POST /api/chatbot/message,
   backend/api/chatbot.py) using the real ChatRequest/ChatResponse
   contract (backend/models/chatbot.py) - not a local/static responder.
   ========================================================= */
const GENIE_STATE_KEY = "genieChatState";
const GENIE_PENDING_DRAFT_KEY = "geniePendingDraft";
const GENIE_DRAFTING_INTENTS = ["create_ticket", "support_issue", "leave_management"];

function loadGenieState() {
    try {
        const raw = sessionStorage.getItem(GENIE_STATE_KEY);
        if (!raw) return { history: [], draft: null, active_intent: null, active_request_type: null };
        const parsed = JSON.parse(raw);
        return {
            history: Array.isArray(parsed.history) ? parsed.history : [],
            draft: parsed.draft || null,
            active_intent: parsed.active_intent || null,
            active_request_type: parsed.active_request_type || null,
        };
    } catch (err) {
        return { history: [], draft: null, active_intent: null, active_request_type: null };
    }
}

function saveGenieState(state) {
    sessionStorage.setItem(GENIE_STATE_KEY, JSON.stringify(state));
}

function getCurrentUserRole() {
    try {
        const user = JSON.parse(localStorage.getItem("portalUser") || "{}");
        return user.role || "Employee";
    } catch (err) {
        return "Employee";
    }
}

async function apiChatbotMessage(message, state) {
    const payload = {
        message,
        role: getCurrentUserRole(),
        history: state.history,
        draft: state.draft,
        active_intent: state.active_intent,
        active_request_type: state.active_request_type,
    };
    try {
        const res = await fetch(`${API_BASE_URL}/chatbot/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("Failed to reach the chatbot service:", err);
    }
    return {
        message: "I'm having trouble reaching the assistant service right now. Please try again in a moment.",
        intent: "general",
        suggestions: []
    };
}

/* Fold a completed turn into the persisted conversation state. A
   ticket-drafting flow stays "active" (so the next message is treated as
   a continuation) only while it's still collecting fields - once the
   draft is ready_for_review it's handed off to the actual form and the
   chat is free to start a new topic. */
function advanceGenieState(state, userMessage, response) {
    state.history.push({ role: "user", message: userMessage });
    state.history.push({ role: "assistant", message: response.message || "" });

    const stillDrafting = GENIE_DRAFTING_INTENTS.includes(response.intent) && !response.ready_for_review;
    state.active_intent = stillDrafting ? response.intent : null;
    state.active_request_type = stillDrafting ? (response.request_type || null) : null;
    state.draft = stillDrafting ? (response.ticket_draft || null) : null;

    saveGenieState(state);
}

function renderGenieUserMessage(container, text) {
    const userDiv = document.createElement("div");
    userDiv.className = "genie-message user-message";
    userDiv.style.display = "flex";
    userDiv.style.justifyContent = "flex-end";
    userDiv.style.marginBottom = "12px";
    userDiv.innerHTML = `<div class="genie-bubble" style="background:#4f46e5; color:white; border-radius:12px; padding:10px 14px;">${escapeHTML(text)}</div>`;
    container.appendChild(userDiv);
}

function renderGenieBotMessage(container, text, suggestions) {
    const botDiv = document.createElement("div");
    botDiv.className = "genie-message";
    botDiv.style.marginBottom = "12px";
    const suggestionsHtml = (suggestions && suggestions.length)
        ? `<div class="genie-suggestions">${suggestions.map(s => `<button class="genie-suggestion" type="button">${escapeHTML(s)}</button>`).join("")}</div>`
        : "";
    botDiv.innerHTML = `
        <div class="genie-message-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
        <div class="genie-bubble">${escapeHTML(text)}</div>
        ${suggestionsHtml}
    `;
    container.appendChild(botDiv);
}

/* Redraw the drawer from persisted history so a conversation survives
   navigating to a different page (e.g. when a draft becomes ready and we
   move to new-request.html to prefill the right form). */
function renderGenieHistory(container, state) {
    if (!container || !state.history.length) return;
    container.innerHTML = "";
    state.history.forEach(turn => {
        if (turn.role === "user") {
            renderGenieUserMessage(container, turn.message);
        } else {
            renderGenieBotMessage(container, turn.message, null);
        }
    });
}

/* =========================================================
   REQUEST FORM PREFILL (from a ready_for_review chatbot draft)
   Only ever fills field values and switches tabs - never submits.
   ========================================================= */
const GENIE_REQUEST_TYPE_TABS = {
    standard: "standardRequestTab",
    anonymous: "anonymousRequestTab",
    leave_management: "leaveRequestTab",
};

function switchRequestTab(tabTarget) {
    const btn = document.querySelector(`.tab-btn[data-target="${tabTarget}"]`);
    const content = document.getElementById(tabTarget);
    if (!btn || !content) return false;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    content.classList.add("active");
    return true;
}

function setFieldValue(id, value) {
    if (!value) return;
    const el = document.getElementById(id);
    if (el) el.value = value;
}

function prefillRequestForm(requestType, draft) {
    if (!draft) return;
    const tabTarget = GENIE_REQUEST_TYPE_TABS[requestType];
    if (!tabTarget || !switchRequestTab(tabTarget)) return;

    if (requestType === "standard") {
        setFieldValue("ticketSubject", draft.title);
        setFieldValue("ticketCategory", draft.category);
        setFieldValue("ticketDescription", draft.description);
        setFieldValue("preferredDate", draft.preferredDate);
    } else if (requestType === "anonymous") {
        setFieldValue("anonTicketSubject", draft.title);
        setFieldValue("anonTicketCategory", draft.category);
        setFieldValue("anonTicketDescription", draft.description);
    } else if (requestType === "leave_management") {
        setFieldValue("leaveType", draft.category);
        setFieldValue("leaveDescription", draft.description);
        // KNOWN BACKEND LIMITATION: the chatbot draft only carries a single
        // preferredDate (models.chatbot.TicketDraft), while this form has
        // separate start/end date fields. We treat preferredDate as the
        // start date (the existing chatbot<->form compatibility choice)
        // and deliberately leave leaveEndDate for the user to confirm
        // rather than fabricating it - the full range the user typed is
        // still visible in the prefilled description for review.
        setFieldValue("leaveStartDate", draft.preferredDate);
    }

    const card = document.querySelector(".request-form-card");
    if (card) card.scrollIntoView({ behavior: "smooth", block: "start" });
}

function applyPendingGenieDraft() {
    const raw = sessionStorage.getItem(GENIE_PENDING_DRAFT_KEY);
    if (!raw) return;
    sessionStorage.removeItem(GENIE_PENDING_DRAFT_KEY);
    try {
        const pending = JSON.parse(raw);
        prefillRequestForm(pending.request_type, pending.draft);
    } catch (err) {
        // Malformed/stale pending draft - nothing to prefill.
    }
}

/* When a draft is ready_for_review, hand it to the correct existing form.
   If we're already on the New Request page, prefill in place; otherwise
   stash it and navigate there (the page reload picks it up via
   applyPendingGenieDraft()). Never auto-submits. */
function openReadyDraft(response) {
    if (!response.request_type || !response.ticket_draft) return;
    const onNewRequestPage = !!document.getElementById("newTicketForm");
    if (onNewRequestPage) {
        prefillRequestForm(response.request_type, response.ticket_draft);
        return;
    }
    sessionStorage.setItem(
        GENIE_PENDING_DRAFT_KEY,
        JSON.stringify({ request_type: response.request_type, draft: response.ticket_draft })
    );
    setTimeout(() => { window.location.href = "new-request.html"; }, 900);
}

/* Deterministic (not GPT-driven) route handling for navigation-style
   replies (intent=navigation, or a fallback action like "browse the
   Knowledge Base" / "view My Tickets"). Ticket-status/knowledge/general
   replies never open a request form. */
function handleGenieAction(action) {
    if (!action || !action.target) return;
    if (action.type !== "navigate" && action.type !== "lookup_ticket") return;
    setTimeout(() => { window.location.href = action.target; }, 900);
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/* Initialize Floating Genie Drawer globally if present on page */
document.addEventListener("DOMContentLoaded", () => {
    const genieBtn = document.getElementById("genieButton");
    const genieChat = document.getElementById("genieChat");
    const closeGenieBtn = document.getElementById("closeGenieButton");
    const genieSendBtn = document.getElementById("genieSendButton");
    const genieInput = document.getElementById("genieInput");
    const genieMessages = document.getElementById("genieMessages");
    // "Need help writing your request?" button on new-request.html.
    const openGenieFromRequestBtn = document.getElementById("openGenieFromRequest");

    if (!genieBtn || !genieChat) return;

    const openGenie = () => genieChat.classList.add("open");

    genieBtn.addEventListener("click", () => genieChat.classList.toggle("open"));

    if (closeGenieBtn) {
        closeGenieBtn.addEventListener("click", () => genieChat.classList.remove("open"));
    }
    if (openGenieFromRequestBtn) {
        openGenieFromRequestBtn.addEventListener("click", openGenie);
    }

    let genieState = loadGenieState();
    renderGenieHistory(genieMessages, genieState);

    async function sendGenieMsg() {
        if (!genieInput || !genieMessages) return;
        const msg = genieInput.value.trim();
        if (!msg) return;

        renderGenieUserMessage(genieMessages, msg);
        genieInput.value = "";
        genieInput.disabled = true;
        genieMessages.scrollTop = genieMessages.scrollHeight;

        const response = await apiChatbotMessage(msg, genieState);
        advanceGenieState(genieState, msg, response);

        renderGenieBotMessage(genieMessages, response.message, response.suggestions);
        genieMessages.scrollTop = genieMessages.scrollHeight;
        genieInput.disabled = false;
        genieInput.focus();

        if (response.ready_for_review) {
            openReadyDraft(response);
        } else {
            handleGenieAction(response.action);
        }
    }

    if (genieSendBtn) {
        genieSendBtn.addEventListener("click", sendGenieMsg);
    }
    if (genieInput) {
        genieInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendGenieMsg();
        });
    }
    // Both the static initial suggestions in the HTML and any rendered
    // from a chatbot response use this same class - wire them all via
    // delegation so clicking one sends it as the next message.
    if (genieMessages) {
        genieMessages.addEventListener("click", (e) => {
            const btn = e.target.closest(".genie-suggestion");
            if (!btn || !genieInput) return;
            genieInput.value = btn.textContent.trim();
            sendGenieMsg();
        });
    }
});

