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

                const inPagesDir = window.location.pathname.includes('/pages/');
                if (selectedRole === 'Management') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Management User', role: 'Management', email: 'management@ticketgenie.com' }));
                    window.location.href = inPagesDir ? 'management-portal.html' : 'pages/management-portal.html';
                } else if (selectedRole === 'Employee') {
                    localStorage.setItem('portalUser', JSON.stringify({ name: 'Employee User', role: 'Employee', email: 'employee@ticketgenie.com' }));
                    window.location.href = inPagesDir ? '../index.html' : 'index.html';
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
========================================================= */
function initializeMyTickets() {
    const table = document.querySelector(".tickets-table");
    if (!table) return;

    renderTickets();

    const searchInput = document.getElementById("ticketSearch");
    if (searchInput) {
        searchInput.addEventListener("input", renderTickets);
    }

    const filters = document.querySelectorAll(".ticket-filter");
    filters.forEach(filter => {
        filter.addEventListener("change", renderTickets);
    });
}

async function renderTickets() {
    const table = document.querySelector(".tickets-table");
    if (!table) return;

    const searchInput = document.getElementById("ticketSearch");
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";

    const statusFilter = document.getElementById("ticketStatusFilter");
    const priorityFilter = document.getElementById("ticketPriorityFilter");

    const statusValue = statusFilter ? statusFilter.value : "all";
    const priorityValue = priorityFilter ? priorityFilter.value : "all";

    let tickets = await apiFetchTickets({
        search: searchTerm,
        status: statusValue,
        priority: priorityValue
    });

    if (searchTerm) {
        tickets = tickets.filter(ticket => {
            const title = (ticket.title || ticket.subject || "").toLowerCase();
            const id = (ticket.id || "").toLowerCase();
            const category = (ticket.category || "").toLowerCase();
            return title.includes(searchTerm) || id.includes(searchTerm) || category.includes(searchTerm);
        });
    }

    if (statusValue && statusValue !== "all") {
        tickets = tickets.filter(ticket => String(ticket.status).toLowerCase() === statusValue.toLowerCase());
    }

    if (priorityValue && priorityValue !== "all") {
        tickets = tickets.filter(ticket => String(ticket.priority).toLowerCase() === priorityValue.toLowerCase());
    }

    tickets.sort((a, b) => {
        const dateA = new Date(a.createdAt || a.created_at || 0);
        const dateB = new Date(b.createdAt || b.created_at || 0);
        return dateB - dateA;
    });

    const header = table.querySelector(".table-header");
    table.innerHTML = "";
    if (header) { table.appendChild(header); }

    tickets.forEach(ticket => {
        const row = createTicketRow(ticket);
        table.appendChild(row);
    });

    if (tickets.length === 0) {
        const empty = document.createElement("div");
        empty.className = "ticket-empty-state";
        empty.innerHTML = `
            <i class="fa-regular fa-folder-open"></i>
            <strong>No tickets found</strong>
            <span>Try changing your search or filters.</span>
        `;
        table.appendChild(empty);
    }

    await updateTicketOverview();
}

function createTicketRow(ticket) {
    const row = document.createElement("div");
    row.className = "table-row ticket-clickable";
    const icon = getTicketIcon(ticket.category);
    const updated = formatTicketDate(ticket.createdAt || ticket.created_at);

    row.innerHTML = `
        <div class="request-info">
            <div class="request-icon"><i class="${icon}"></i></div>
            <div>
                <strong>${escapeHTML(ticket.title || ticket.subject || "Request")}</strong>
                <span>#${escapeHTML(ticket.id)}</span>
            </div>
        </div>
        <span>${escapeHTML(ticket.category || "General")}</span>
        <span class="status ${getStatusClass(ticket.status)}">${escapeHTML(ticket.status || "Open")}</span>
        <span class="priority ${String(ticket.priority || "Medium").toLowerCase().replace(/\s+/g, "-")}">${escapeHTML(ticket.priority || "Medium")}</span>
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
        "Human Resources": "fa-solid fa-users",
        "Employee Services": "fa-solid fa-user",
        "Time Off": "fa-solid fa-calendar-check",
        "Access & Permissions": "fa-solid fa-lock",
        "Other": "fa-solid fa-file-lines"
    };
    return (icons[category] || "fa-solid fa-file-lines");
}

function getStatusClass(status) {
    return String(status || "open").toLowerCase().replace(/\s+/g, "-");
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
    const open = tickets.filter(ticket => String(ticket.status).toLowerCase() === "open").length;
    const inProgress = tickets.filter(ticket => ["in progress", "pending", "in-progress"].includes(String(ticket.status).toLowerCase())).length;
    const resolved = tickets.filter(ticket => String(ticket.status).toLowerCase() === "resolved").length;

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
    const modal = document.createElement("div");
    modal.className = "ticket-modal";
    modal.innerHTML = `
        <div class="ticket-modal-content">
            <button class="ticket-modal-close" type="button" aria-label="Close ticket details">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <p class="eyebrow">TICKET #${escapeHTML(ticket.id)}</p>
            <h2>${escapeHTML(ticket.title)}</h2>
            <div class="ticket-detail-grid">
                <div><span>Category</span><strong>${escapeHTML(ticket.category)}</strong></div>
                <div><span>Priority</span><strong class="priority ${ticket.priority.toLowerCase().replace(/\s+/g, "-")}">${escapeHTML(ticket.priority)}</strong></div>
                <div><span>Status</span><strong class="status ${getStatusClass(ticket.status)}">${escapeHTML(ticket.status)}</strong></div>
                <div><span>Preferred Date</span><strong>${ticket.date ? formatPreferredDate(ticket.date) : "Not specified"}</strong></div>
            </div>
            <div class="ticket-description">
                <span>Description</span>
                <p>${escapeHTML(ticket.description)}</p>
            </div>
            <div class="ticket-modal-footer">
                <span>Created ${formatTicketDate(ticket.createdAt)}</span>
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

    function sendGenieMessage() {
        if (!genieInput) return;
        const message = genieInput.value.trim();
        if (!message) return;

        addGenieMessage(message, "user");
        genieInput.value = "";

        const thinking = addGenieThinking();
        setTimeout(() => {
            if (thinking) thinking.remove();
            const response = getGenieResponse(message);
            addGenieMessage(response, "agent");
        }, 700);
    }

    if (genieSendButton) genieSendButton.addEventListener("click", sendGenieMessage);
    if (genieInput) {
        genieInput.addEventListener("keydown", event => {
            if (event.key === "Enter") { event.preventDefault(); sendGenieMessage(); }
        });
    }

    const suggestions = document.querySelectorAll(".genie-suggestion");
    suggestions.forEach(suggestion => {
        suggestion.addEventListener("click", () => {
            const message = suggestion.textContent.trim();
            if (!message) return;
            addGenieMessage(message, "user");
            const thinking = addGenieThinking();
            setTimeout(() => {
                if (thinking) thinking.remove();
                const response = getGenieResponse(message);
                addGenieMessage(response, "agent");
            }, 700);
        });
    });

    document.addEventListener("click", event => {
        if (!genieChat.classList.contains("open")) return;
        const clickedInside = genieChat.contains(event.target);
        const clickedButton = genieButton && genieButton.contains(event.target);
        const clickedNav = genieNav && genieNav.contains(event.target);
        if (!clickedInside && !clickedButton && !clickedNav) closeGenie();
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
    return String(value)
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

    if (!searchInput) return;

    function searchArticles() {
        const searchTerm = searchInput.value.toLowerCase().trim();
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
    searchInput.addEventListener("keydown", event => {
        if (event.key === "Enter") { event.preventDefault(); searchArticles(); }
    });

    categories.forEach(category => {
        category.addEventListener("click", () => {
            const selectedCategory = category.dataset.category;
            articles.forEach(article => {
                const articleCategory = article.dataset.category;
                if (articleCategory === selectedCategory) {
                    article.style.display = "flex";
                } else {
                    article.style.display = "none";
                }
            });
            searchInput.value = selectedCategory;
        });
    });
}

/* =========================================================
   SIDEBAR TOGGLE
========================================================= */
function initializeSidebarToggle() {
    const topbarToggle = document.getElementById('sidebarToggle');
    const brandToggle = document.getElementById('brandMenuToggle');

    function toggleSidebar(e) {
        if (e) e.stopPropagation();
        document.body.classList.toggle('sidebar-closed');
    }

    // Attach to the topbar button (to reopen)
    if (topbarToggle) topbarToggle.addEventListener('click', toggleSidebar);
    
    // Attach to the inside sidebar button (to close)
    if (brandToggle) brandToggle.addEventListener('click', toggleSidebar);
}

/* =========================================================
   ENHANCED FILE UPLOAD
========================================================= */
function initializeFileUploads() {
    // Grab every upload area across all tabs
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        const fileInput = area.querySelector('input[type="file"]');
        const browseBtn = area.querySelector('.browse-button');
        // The div right after the upload-area is where we display selected files
        const fileListContainer = area.nextElementSibling; 
        
        // DataTransfer object lets us manipulate the file list (add/remove) programmatically
        let dataTransfer = new DataTransfer();

        // 1. Click to browse
        if (browseBtn) {
            browseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.click();
            });
        }

        // 2. Drag & Drop Visuals
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('drag-over');
        });

        area.addEventListener('dragleave', () => {
            area.classList.remove('drag-over');
        });

        // 3. Handle Dropped Files
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                handleFiles(e.dataTransfer.files);
            }
        });

        // 4. Handle Browsed Files
        if (fileInput) {
            fileInput.addEventListener('change', () => {
                if (fileInput.files.length > 0) {
                    handleFiles(fileInput.files);
                }
            });
        }

        // Add files to our DataTransfer and update the UI
        function handleFiles(files) {
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            fileInput.files = dataTransfer.files; // Update the actual hidden input
            renderFileList();
        }

        // Build the HTML for the attached files
        function renderFileList() {
            if (!fileListContainer) return;
            fileListContainer.innerHTML = '';
            if (dataTransfer.files.length === 0) return;
            
            const list = document.createElement('div');
            list.className = 'file-list';
            
            Array.from(dataTransfer.files).forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                // Pick a nice icon based on the file type
                let iconClass = 'fa-file';
                if (file.type.includes('image')) iconClass = 'fa-file-image';
                else if (file.type.includes('pdf')) iconClass = 'fa-file-pdf';
                else if (file.type.includes('word')) iconClass = 'fa-file-word';
                else if (file.type.includes('video')) iconClass = 'fa-file-video';

                fileItem.innerHTML = `
                    <div class="file-item-info">
                        <i class="fa-regular ${iconClass}"></i>
                        <span>${file.name}</span>
                    </div>
                    <button type="button" class="file-remove-btn" data-index="${index}" aria-label="Remove file">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                `;
                list.appendChild(fileItem);
            });
            
            fileListContainer.appendChild(list);
            
            // Attach event listeners to the new "remove" buttons
            const removeBtns = list.querySelectorAll('.file-remove-btn');
            removeBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    const indexToRemove = parseInt(this.getAttribute('data-index'), 10);
                    removeFile(indexToRemove);
                });
            });
        }

        // Rebuild the DataTransfer object without the removed file
        function removeFile(index) {
            const dt = new DataTransfer();
            const files = dataTransfer.files;
            for (let i = 0; i < files.length; i++) {
                if (i !== index) {
                    dt.items.add(files[i]);
                }
            }
            dataTransfer = dt;
            fileInput.files = dataTransfer.files;
            renderFileList();
        }
    });
}
/* =========================================================
   DARK MODE TOGGLE
========================================================= */
function initializeDarkMode() {
    const toggleBtn = document.getElementById('darkModeToggle');
    const darkIcon = document.getElementById('darkModeIcon');
    
    // Check local storage for saved preference on page load
    const savedTheme = localStorage.getItem('ticketGenieTheme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (darkIcon) {
            darkIcon.classList.remove('fa-moon');
            darkIcon.classList.add('fa-sun');
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            
            // Save preference
            localStorage.setItem('ticketGenieTheme', isDark ? 'dark' : 'light');
            
            // Switch icon between moon and sun
            if (darkIcon) {
                if (isDark) {
                    darkIcon.classList.remove('fa-moon');
                    darkIcon.classList.add('fa-sun');
                } else {
                    darkIcon.classList.remove('fa-sun');
                    darkIcon.classList.add('fa-moon');
                }
            }
        });
    }
}

/* =========================================================
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

