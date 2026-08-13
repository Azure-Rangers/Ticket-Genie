/* =========================================================
   TICKETGENIE - MAIN JAVASCRIPT & API CLIENT
   ========================================================= */

const API_BASE_URL = "/api";
const STORAGE_KEY = "ticketGenieTickets";

/* =========================================================
   LOCAL STORAGE & DEFAULT DATA
   ========================================================= */
function getLocalTickets() {
    const tickets = localStorage.getItem(STORAGE_KEY);
    if (!tickets) {
        return [];
    }
    try {
        return JSON.parse(tickets);
    } catch (e) {
        return [];
    }
}

function saveLocalTickets(tickets) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
}

function generateTicketId() {
    const tickets = getLocalTickets();
    let highestNumber = 1000;
    tickets.forEach(ticket => {
        const number = parseInt(String(ticket.id).replace("HD-", ""), 10);
        if (!isNaN(number) && number > highestNumber) {
            highestNumber = number;
        }
    });
    return `HD-${highestNumber + 1}`;
}

/* =========================================================
   BACKEND API CLIENT
   ========================================================= */
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
    return getLocalTickets();
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
    const tickets = getLocalTickets();
    const newTicket = {
        id: generateTicketId(),
        title: ticketPayload.subject || ticketPayload.title,
        category: ticketPayload.category,
        priority: ticketPayload.priority || "Medium",
        status: "Open",
        description: ticketPayload.description,
        date: ticketPayload.preferredDate || "",
        createdAt: new Date().toISOString()
    };
    tickets.unshift(newTicket);
    saveLocalTickets(tickets);
    return newTicket;
}

async function apiSendGenieChat(message) {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        if (res.ok) {
            const data = await res.json();
            if (data && (data.reply || data.response || data.message)) {
                return data.reply || data.response || data.message;
            }
        }
    } catch (err) {
        console.warn("Genie chat API not available, using offline Genie response:", err);
    }
    return getGenieResponse(message);
}

/* =========================================================
   UI INITIALIZERS & COMPONENTS
   ========================================================= */

function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content");

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            mainContent.classList.toggle("expanded");
        });
    }
}

function initializeBrandDropdown() {
    const brandToggleBtn = document.getElementById('brandMenuToggle');
    const brandDropdown = document.getElementById('brandDropdown');

    if (brandToggleBtn && brandDropdown) {
        brandToggleBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            const isShowing = brandDropdown.classList.toggle('show');
            const icon = brandToggleBtn.querySelector('i');
            
            if (icon) {
                if (isShowing) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-chevron-right');
                } else {
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-bars');
                }
            }
        });

        document.addEventListener('click', (event) => {
            if (!brandToggleBtn.contains(event.target) && !brandDropdown.contains(event.target)) {
                brandDropdown.classList.remove('show');
                const icon = brandToggleBtn.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }
}

function initializeProfileDropdown() {
    const trigger = document.getElementById('profileDropdownTrigger');
    const menu = document.getElementById('profileDropdownMenu');
    const display = document.getElementById('currentRoleDisplay');

    if (trigger && menu) {
        trigger.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            menu.classList.toggle('show');
        };

        document.onclick = (e) => {
            if (!trigger.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.remove('show');
            }
        };

        const roleButtons = menu.querySelectorAll('.role-switch-btn');
        roleButtons.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const selectedRole = btn.getAttribute('data-role');
                menu.classList.remove('show');

                const inPagesDir = window.location.pathname.includes('/pages/');
                if (selectedRole === 'Management') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Management User', role: 'Management', email: 'management@ticketgenie.com' }));
                    window.location.href = inPagesDir ? 'management-portal.html' : 'pages/management-portal.html';
                } else if (selectedRole === 'Employee') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Employee User', role: 'Employee', email: 'employee@ticketgenie.com' }));
                    window.location.href = inPagesDir ? '../index.html' : 'index.html';
                }
            };
        });
    }
}

function initializeNewRequestForm() {
    const form = document.getElementById("newTicketForm") || document.querySelector(".request-form-card form");
    if (!form) return;

    const textarea = document.getElementById("ticketDescription");
    const charCount = document.getElementById("characterCount");
    if (textarea && charCount) {
        textarea.addEventListener("input", () => {
            const count = textarea.value.length;
            charCount.textContent = `${count} / 1000`;
        });
    }

    const browseBtn = document.getElementById("browseButton");
    const fileInput = document.getElementById("fileUpload");
    const selectedFilesContainer = document.getElementById("selectedFiles");

    if (browseBtn && fileInput) {
        browseBtn.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", () => {
            if (!selectedFilesContainer) return;
            selectedFilesContainer.innerHTML = "";
            Array.from(fileInput.files).forEach(file => {
                const fileTag = document.createElement("small");
                fileTag.style.display = "inline-block";
                fileTag.style.margin = "4px 6px 0 0";
                fileTag.style.padding = "4px 8px";
                fileTag.style.background = "#e7f0e9";
                fileTag.style.borderRadius = "4px";
                fileTag.style.color = "#527d66";
                fileTag.textContent = file.name;
                selectedFilesContainer.appendChild(fileTag);
            });
        });
    }

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const titleElement = document.getElementById("ticketSubject");
        const categoryElement = document.getElementById("ticketCategory");
        const priorityElement = document.getElementById("ticketPriority");
        const descriptionElement = document.getElementById("ticketDescription");
        const preferredDateElement = document.getElementById("preferredDate");

        const title = titleElement ? titleElement.value.trim() : "";
        const category = categoryElement ? categoryElement.value : "";
        const priority = priorityElement ? priorityElement.value : "Medium";
        const description = descriptionElement ? descriptionElement.value.trim() : "";
        const preferredDate = preferredDateElement ? preferredDateElement.value : "";

        if (!title) { showFormError("Please enter a request title."); if (titleElement) titleElement.focus(); return; }
        if (!category) { showFormError("Please select a category."); if (categoryElement) categoryElement.focus(); return; }
        if (!description) { showFormError("Please provide a description."); if (descriptionElement) descriptionElement.focus(); return; }

        const oldError = document.getElementById("formErrorMessage");
        if (oldError) oldError.style.display = "none";

        const submitBtn = document.getElementById("submitRequestButton");
        if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Submitting...`; }

        const newTicket = await apiCreateTicket({
            subject: title,
            title: title,
            category: category,
            priority: priority,
            description: description,
            preferredDate: preferredDate
        });

        showSuccessMessage(newTicket);
        setTimeout(() => { window.location.href = "my-tickets.html"; }, 2500);
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

    const ticketId = ticket.id ? ticket.id : "Submitted";
    success.innerHTML = `
        <div class="success-icon"><i class="fa-solid fa-check"></i></div>
        <div>
            <strong>Request submitted successfully</strong>
            <span>Ticket #${escapeHTML(ticketId)} has been created.</span>
        </div>
    `;

    requestAnimationFrame(() => { success.classList.add("show"); });
    setTimeout(() => { success.classList.remove("show"); }, 3000);
}

/* =========================================================
   MY TICKETS & OVERVIEW
   ========================================================= */
async function initializeMyTickets() {
    const myTicketsList = document.getElementById("myTicketsList");
    if (!myTicketsList) return;

    await renderTickets();

    const searchInput = document.getElementById("ticketSearch");
    if (searchInput) {
        searchInput.addEventListener("input", () => renderTickets());
    }

    const statusFilter = document.getElementById("ticketStatusFilter");
    const priorityFilter = document.getElementById("ticketPriorityFilter");

    if (statusFilter) statusFilter.addEventListener("change", () => renderTickets());
    if (priorityFilter) priorityFilter.addEventListener("change", () => renderTickets());
}

async function renderTickets() {
    const myTicketsList = document.getElementById("myTicketsList");
    if (!myTicketsList) return;

    const searchInput = document.getElementById("ticketSearch");
    const statusFilter = document.getElementById("ticketStatusFilter");
    const priorityFilter = document.getElementById("ticketPriorityFilter");

    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";
    const status = statusFilter ? statusFilter.value : "all";
    const priority = priorityFilter ? priorityFilter.value : "all";

    const tickets = await apiFetchTickets({ search: searchTerm, status: status, priority: priority });

    const filtered = tickets.filter(t => {
        const matchesSearch = !searchTerm || 
            (t.title && t.title.toLowerCase().includes(searchTerm)) || 
            (t.id && t.id.toLowerCase().includes(searchTerm)) || 
            (t.category && t.category.toLowerCase().includes(searchTerm));
        const matchesStatus = (status === "all") || (t.status === status);
        const matchesPriority = (priority === "all") || (t.priority === priority);
        return matchesSearch && matchesStatus && matchesPriority;
    });

    myTicketsList.innerHTML = "";

    if (filtered.length === 0) {
        myTicketsList.innerHTML = `
            <div class="ticket-empty-state">
                <i class="fa-solid fa-ticket-simple" style="font-size: 28px; margin-bottom: 8px;"></i>
                <strong>No tickets found</strong>
                <p>Try adjusting your search or filters.</p>
            </div>
        `;
        return;
    }

    filtered.forEach(ticket => {
        const row = createTicketRow(ticket);
        myTicketsList.appendChild(row);
    });

    const paginationText = document.getElementById("ticketPaginationText");
    if (paginationText) {
        paginationText.textContent = `Showing ${filtered.length} of ${tickets.length} tickets`;
    }
}

function createTicketRow(ticket) {
    const row = document.createElement("div");
    row.className = "table-row ticket-clickable";
    const icon = getTicketIcon(ticket.category);
    const updated = formatTicketDate(ticket.createdAt || ticket.date);
    const ticketId = ticket.id ? (ticket.id.startsWith("HD-") ? ticket.id : `HD-${ticket.id}`) : "HD-1000";

    row.innerHTML = `
        <div class="request-info">
            <div class="request-icon"><i class="${icon}"></i></div>
            <div>
                <strong>${escapeHTML(ticket.title || ticket.subject || "Support Ticket")}</strong>
                <span>#${escapeHTML(ticketId)}</span>
            </div>
        </div>
        <span>${escapeHTML(ticket.category || "General")}</span>
        <span class="status ${getStatusClass(ticket.status || "Open")}">${escapeHTML(ticket.status || "Open")}</span>
        <span class="priority ${(ticket.priority || "Medium").toLowerCase().replace(/\s+/g, "-")}">${escapeHTML(ticket.priority || "Medium")}</span>
        <span>${updated}</span>
    `;

    row.addEventListener("click", () => { showTicketDetails(ticket); });
    return row;
}

function getTicketIcon(category) {
    const icons = {
        "IT Support": "fa-solid fa-display",
        "IT & Technology": "fa-solid fa-display",
        "Payroll": "fa-solid fa-receipt",
        "Payroll & Benefits": "fa-solid fa-receipt",
        "Benefits": "fa-solid fa-shield-heart",
        "HR": "fa-solid fa-users",
        "Human Resources": "fa-solid fa-users",
        "Employee Services": "fa-solid fa-user",
        "Time Off": "fa-solid fa-calendar-check",
        "Access & Permissions": "fa-solid fa-lock",
        "Other": "fa-solid fa-file-lines"
    };
    return (icons[category] || "fa-solid fa-file-lines");
}

function getStatusClass(status) {
    return String(status).toLowerCase().replace(/\s+/g, "-");
}

function formatTicketDate(dateString) {
    if (!dateString) return "—";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "—";
    const now = new Date();
    const difference = now - date;
    const hours = difference / 3600000;
    if (hours >= 0 && hours < 24) return "Today";
    if (hours >= 24 && hours < 48) return "Yesterday";
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

async function updateTicketOverview() {
    const tickets = await apiFetchTickets();
    const open = tickets.filter(ticket => (ticket.status === "Open" || !ticket.status)).length;
    const inProgress = tickets.filter(ticket => ticket.status === "In Progress" || ticket.status === "Pending").length;
    const resolved = tickets.filter(ticket => ticket.status === "Resolved").length;

    const openCount = document.getElementById("openCount");
    const inProgressCount = document.getElementById("inProgressCount");
    const resolvedCount = document.getElementById("resolvedCount");

    if (openCount) openCount.textContent = open;
    if (inProgressCount) inProgressCount.textContent = inProgress;
    if (resolvedCount) resolvedCount.textContent = resolved;

    const recentTickets = document.getElementById("recentTickets");
    if (recentTickets) {
        recentTickets.innerHTML = "";
        tickets.slice(0, 5).forEach(ticket => {
            const row = createTicketRow(ticket);
            recentTickets.appendChild(row);
        });
    }
}

function showTicketDetails(ticket) {
    const existingModal = document.querySelector(".ticket-modal");
    if (existingModal) existingModal.remove();

    const modal = document.createElement("div");
    modal.className = "ticket-modal";
    const ticketId = ticket.id ? (ticket.id.startsWith("HD-") ? ticket.id : `HD-${ticket.id}`) : "HD-1000";

    modal.innerHTML = `
        <div class="ticket-modal-content">
            <button class="ticket-modal-close" type="button" aria-label="Close ticket details">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <p class="eyebrow">TICKET #${escapeHTML(ticketId)}</p>
            <h2>${escapeHTML(ticket.title || ticket.subject || "Support Ticket")}</h2>
            <div class="ticket-detail-grid">
                <div><span>Category</span><strong>${escapeHTML(ticket.category || "General")}</strong></div>
                <div><span>Priority</span><strong class="priority ${(ticket.priority || "Medium").toLowerCase().replace(/\s+/g, "-")}">${escapeHTML(ticket.priority || "Medium")}</strong></div>
                <div><span>Status</span><strong class="status ${getStatusClass(ticket.status || "Open")}">${escapeHTML(ticket.status || "Open")}</strong></div>
                <div><span>Preferred Date</span><strong>${ticket.date ? formatPreferredDate(ticket.date) : "Not specified"}</strong></div>
            </div>
            <div class="ticket-description">
                <span>Description</span>
                <p>${escapeHTML(ticket.description || "No description provided.")}</p>
            </div>
            <div class="ticket-modal-footer">
                <span>Created ${formatTicketDate(ticket.createdAt || ticket.date)}</span>
                <button class="modal-close-button" type="button">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    requestAnimationFrame(() => { modal.classList.add("show"); });

    const closeModal = () => {
        modal.classList.remove("show");
        setTimeout(() => { modal.remove(); }, 200);
    };

    const closeIcon = modal.querySelector(".ticket-modal-close");
    const closeButton = modal.querySelector(".modal-close-button");

    if (closeIcon) closeIcon.addEventListener("click", closeModal);
    if (closeButton) closeButton.addEventListener("click", closeModal);

    modal.addEventListener("click", event => { if (event.target === modal) closeModal(); });
    document.addEventListener("keydown", function escapeHandler(event) {
        if (event.key === "Escape") {
            closeModal();
            document.removeEventListener("keydown", escapeHandler);
        }
    });
}

function formatPreferredDate(dateString) {
    if (!dateString) return "Not specified";
    const date = new Date(dateString + "T00:00:00");
    if (isNaN(date.getTime())) return dateString;
    return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}

/* =========================================================
   GENIE AI AGENT
   ========================================================= */
function initializeGenie() {
    const genieChat = document.getElementById("genieChat");
    if (!genieChat) return;
    const genieInput = document.getElementById("genieInput");
    const genieSendButton = document.getElementById("genieSendButton");
    const closeButton = document.getElementById("closeGenieButton");
    const genieButton = document.getElementById("genieButton");

    function openGenie() {
        genieChat.classList.add("open");
        if (genieInput) setTimeout(() => { genieInput.focus(); }, 100);
    }

    function closeGenie() {
        genieChat.classList.remove("open");
    }

    if (genieButton) genieButton.addEventListener("click", openGenie);
    if (closeButton) closeButton.addEventListener("click", closeGenie);

    const genieNav = document.querySelector(".genie-nav-link");
    if (genieNav) genieNav.addEventListener("click", event => { event.preventDefault(); openGenie(); });

    const knowledgeGenieButton = document.getElementById("knowledgeGenieButton");
    if (knowledgeGenieButton) knowledgeGenieButton.addEventListener("click", openGenie);

    const openGenieFromRequest = document.getElementById("openGenieFromRequest");
    if (openGenieFromRequest) openGenieFromRequest.addEventListener("click", openGenie);

    async function sendGenieMessage() {
        if (!genieInput) return;
        const message = genieInput.value.trim();
        if (!message) return;

        addGenieMessage(message, "user");
        genieInput.value = "";

        const thinking = addGenieThinking();
        const response = await apiSendGenieChat(message);
        if (thinking) thinking.remove();
        addGenieMessage(response, "agent");
    }

    if (genieSendButton) genieSendButton.addEventListener("click", sendGenieMessage);
    if (genieInput) {
        genieInput.addEventListener("keydown", event => {
            if (event.key === "Enter") { event.preventDefault(); sendGenieMessage(); }
        });
    }

    const suggestions = document.querySelectorAll(".genie-suggestion");
    suggestions.forEach(suggestion => {
        suggestion.addEventListener("click", async () => {
            const message = suggestion.textContent.trim();
            if (!message) return;
            addGenieMessage(message, "user");
            const thinking = addGenieThinking();
            const response = await apiSendGenieChat(message);
            if (thinking) thinking.remove();
            addGenieMessage(response, "agent");
        });
    });

    document.addEventListener("click", event => {
        if (!genieChat.classList.contains("open")) return;
        const clickedInside = genieChat.contains(event.target);
        const clickedButton = genieButton && genieButton.contains(event.target);
        const clickedNav = genieNav && genieNav.contains(event.target);
        const clickedHelp = openGenieFromRequest && openGenieFromRequest.contains(event.target);
        const clickedKGenie = knowledgeGenieButton && knowledgeGenieButton.contains(event.target);
        if (!clickedInside && !clickedButton && !clickedNav && !clickedHelp && !clickedKGenie) closeGenie();
    });
}

function addGenieThinking() {
    const messages = document.getElementById("genieMessages");
    if (!messages) return null;
    const thinking = document.createElement("div");
    thinking.className = "genie-message genie-thinking";
    thinking.innerHTML = `
        <div class="genie-message-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
        <div class="genie-bubble"><span>Genie is thinking...</span></div>
    `;
    messages.appendChild(thinking);
    messages.scrollTop = messages.scrollHeight;
    return thinking;
}

function getGenieResponse(message) {
    const text = message.toLowerCase().trim();
    if (text.includes("hello") || text.includes("hi") || text.includes("hey") || text === "genie") return "Hi! I'm Genie, your AI support agent. I can help you find the right support category, answer common questions, or guide you through creating a request. What do you need help with?";
    if (text.includes("payroll") || text.includes("paycheck") || text.includes("salary") || text.includes("wages") || text.includes("pay")) return "I can help with payroll questions. If you're experiencing an issue with your paycheck, select Payroll when creating a request and include the pay period and a description of the issue.";
    if (text.includes("laptop") || text.includes("computer") || text.includes("wifi") || text.includes("wi-fi") || text.includes("internet") || text.includes("password") || text.includes("login") || text.includes("log in") || text.includes("software") || text.includes("monitor") || text.includes("keyboard") || text.includes("mouse") || text.includes("printer") || text.includes("it help") || text.includes("it issue")) return "This sounds like an IT Support request. If you've already tried basic troubleshooting and still need help, create a new request and select IT & Technology as the category. Be sure to include any error messages or screenshots.";
    if (text.includes("benefit") || text.includes("insurance") || text.includes("health") || text.includes("dental") || text.includes("vision") || text.includes("401k")) return "For benefits questions, the Payroll & Benefits category is usually the best choice. When submitting your request, include the specific benefit or plan you're asking about so the right team can assist you.";
    if (text.includes("pto") || text.includes("vacation") || text.includes("leave") || text.includes("time off") || text.includes("day off")) return "For PTO or leave-related requests, select Time Off as your category when creating a new request. You can also include your preferred date in the request.";
    if (text.includes("access") || text.includes("permission") || text.includes("permissions") || text.includes("account")) return "For access or permission issues, select IT & Technology as your category. Include the system or application you need access to and explain what you're currently unable to access.";
    if (text.includes("ticket") || text.includes("request") || text.includes("submit") || text.includes("create")) return "I can help you create a support request. Select New Request from the sidebar, then provide a clear title, category, priority, description, and preferred date if needed. Once submitted, your request will appear under My Tickets.";
    if (text.includes("my ticket") || text.includes("my tickets") || text.includes("ticket status") || text.includes("check my tickets") || text.includes("status")) return "You can view your submitted requests by selecting My Tickets from the sidebar. There you can search, filter, and select a ticket to view its details.";
    if (text.includes("how long") || text.includes("response") || text.includes("when") || text.includes("wait")) return "The typical response time for a support request is within 1-2 business days. You can check My Tickets to monitor the status of your request.";
    return "I can help with IT & Technology, Payroll & Benefits, Time Off, Employee Services, or creating and tracking a support request. Tell me a little more about what you need help with.";
}

function addGenieMessage(message, sender) {
    const messages = document.getElementById("genieMessages");
    if (!messages) return;
    const messageElement = document.createElement("div");

    if (sender === "user") {
        messageElement.className = "genie-message genie-message-user";
        messageElement.innerHTML = `<div class="genie-bubble">${escapeHTML(message)}</div>`;
    } else {
        messageElement.className = "genie-message";
        messageElement.innerHTML = `
            <div class="genie-message-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
            <div class="genie-bubble">${escapeHTML(message)}</div>
        `;
    }
    messages.appendChild(messageElement);
    messages.scrollTop = messages.scrollHeight;
}

function escapeHTML(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/* =========================================================
   KNOWLEDGE BASE
   ========================================================= */
function initializeKnowledgeBase() {
    const searchInput = document.getElementById("knowledgeSearch");
    const searchButton = document.getElementById("knowledgeSearchButton");
    const articles = document.querySelectorAll(".knowledge-article");
    const categories = document.querySelectorAll(".knowledge-category");

    if (!searchInput && articles.length === 0) return;

    function searchArticles() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";
        articles.forEach(article => {
            const articleText = article.textContent.toLowerCase();
            if (!searchTerm || articleText.includes(searchTerm)) {
                article.style.display = "flex";
            } else {
                article.style.display = "none";
            }
        });
    }

    if (searchButton) searchButton.addEventListener("click", searchArticles);
    if (searchInput) {
        searchInput.addEventListener("keydown", event => {
            if (event.key === "Enter") { event.preventDefault(); searchArticles(); }
        });
    }

    categories.forEach(category => {
        category.addEventListener("click", () => {
            const selectedCategory = category.getAttribute("data-category");
            articles.forEach(article => {
                const articleCategory = article.getAttribute("data-category");
                if (!selectedCategory || articleCategory === selectedCategory) {
                    article.style.display = "flex";
                } else {
                    article.style.display = "none";
                }
            });
            if (searchInput && selectedCategory) searchInput.value = selectedCategory;
        });
    });
}

/* =========================================================
   NOTIFICATIONS
   ========================================================= */
function initializeNotifications() {
    const markAllRead = document.getElementById("markAllRead");
    if (!markAllRead) return;

    markAllRead.addEventListener("click", (e) => {
        e.preventDefault();
        const unreadCards = document.querySelectorAll(".notification-card.unread");
        unreadCards.forEach(card => card.classList.remove("unread"));
        const dots = document.querySelectorAll(".notification-unread-dot");
        dots.forEach(dot => dot.remove());
        const count = document.querySelector(".notification-count");
        if (count) count.textContent = "0";
    });
}

/* =========================================================
   GLOBAL SHORTCUTS
   ========================================================= */
function initializeShortcuts() {
    document.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            const globalSearch = document.getElementById("globalSearch") || document.getElementById("helpSearch") || document.getElementById("ticketSearch") || document.getElementById("knowledgeSearch");
            if (globalSearch) globalSearch.focus();
        }
    });
}

/* =========================================================
   INITIALIZE EVERYTHING
   ========================================================= */
function initApp() {
    initializeSidebarToggle();
    initializeBrandDropdown();
    initializeProfileDropdown();
    initializeNewRequestForm();
    initializeMyTickets();
    initializeGenie();
    initializeKnowledgeBase();
    initializeNotifications();
    initializeShortcuts();
    updateTicketOverview();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
} else {
    initApp();
}
