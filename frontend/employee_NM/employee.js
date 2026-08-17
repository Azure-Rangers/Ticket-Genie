/* =========================================================
   TICKETGENIE EMPLOYEE PORTAL MODULE
   Dedicated handlers for Employee Requests, Tickets Grid, and Threads
   ========================================================= */

const STORAGE_KEY = "ticketGenieTickets";
let loadedMyTicketsMap = {};

function getTickets() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY) || localStorage.getItem("employee_tickets");
        if (stored) return JSON.parse(stored);
    } catch (e) {}
    return [
        { id: "HD-1024", title: "Payroll Issue", category: "Payroll", priority: "High", status: "In Progress", department: "HR Team", description: "Having an issue with my latest paycheck.", date: "2026-08-08", createdAt: "2026-08-08T10:00:00" },
        { id: "HD-1025", title: "Benefits Question", category: "Benefits", priority: "Medium", status: "Open", department: "HR Team", description: "I have a question about my benefits.", date: "2026-08-07", createdAt: "2026-08-07T10:00:00" },
        { id: "HD-1026", title: "Laptop Request", category: "IT Support", priority: "Low", status: "Resolved", department: "IT Team", description: "Requesting a replacement laptop.", date: "2026-08-05", createdAt: "2026-08-05T10:00:00" },
        { id: "HD-1027", title: "PTO Request", category: "Time Off", priority: "Medium", status: "Pending", department: "HR Team", description: "Requesting PTO.", date: "2026-08-04", createdAt: "2026-08-04T10:00:00" }
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

function mapDepartmentName(val) {
    if (!val || val === "Auto") return null;
    const lower = val.toLowerCase();
    if (lower.includes("it")) return "IT Team";
    if (lower.includes("hr") || lower.includes("workplace")) return "HR Team";
    if (lower.includes("account")) return "Accounting Team";
    if (lower.includes("upper") || lower.includes("admin")) return "Upper Management";
    return "IT Team";
}

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

async function initializeMyTickets() {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    list.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b;">Loading tickets...</div>';
    
    let tickets = [];
    try {
        const fetchFn = window.apiFetchTickets || apiFetchTickets;
        tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    } catch (e) {
        console.warn("apiFetchTickets notice in initializeMyTickets:", e);
    }

    if (!tickets || tickets.length === 0) {
        tickets = getTickets();
    }

    renderMyTickets(tickets);
}

function renderMyTickets(tickets) {
    const list = document.getElementById("myTicketsList");
    if (!list) return;
    if (!tickets || tickets.length === 0) {
        list.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b;">No support requests found.</div>';
        return;
    }
    loadedMyTicketsMap = {};
    list.innerHTML = tickets.map(t => {
        loadedMyTicketsMap[t.id] = t;
        const stClass = (t.status || "Open").toLowerCase().replaceAll(" ", "-");
        const prClass = (t.priority || "Medium").toLowerCase();
        const dateStr = t.date || (t.createdAt ? t.createdAt.split("T")[0] : "Today");
        const deptStr = t.department || t.category || "IT Support";

        return `
            <div class="tickets-table-row" style="display: grid; grid-template-columns: 2.2fr 1.6fr 1fr 1fr 1fr 110px; gap: 16px; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e1e6e2; font-size: 13px; transition: background 0.15s; cursor: pointer;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'" onclick="window.location.href='ticket-detail.html?id=${encodeURIComponent(t.id)}'">
                <div>
                    <strong style="color: #1e293b; font-size: 14px;">${escapeHTML(t.title || "Untitled")}</strong>
                    <div style="font-size: 12px; color: #64748b; margin-top: 2px;">#${escapeHTML(t.id)}</div>
                </div>
                <div><span style="font-weight: 500; color: #334155;">${escapeHTML(deptStr)}</span></div>
                <div><span class="badge priority-${prClass}" style="padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">${escapeHTML(t.priority || "Medium")}</span></div>
                <div><span class="badge status-${stClass}" style="padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">${escapeHTML(t.status || "Open")}</span></div>
                <div style="color: #64748b;">${escapeHTML(dateStr)}</div>
                <div style="text-align: right;">
                    <button type="button" style="background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; border-radius: 6px; padding: 6px 12px; font-size: 12px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;" onclick="event.stopPropagation(); window.location.href='ticket-detail.html?id=${encodeURIComponent(t.id)}'">
                        <i class="fa-regular fa-comments"></i> Chat
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

async function loadTicketDetailPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get("id") || "HD-1024";

    const fetchFn = window.apiFetchTickets || (async () => getTickets());
    let tickets = await fetchFn({ requesterId: getCurrentRequesterId() });
    let ticket = (tickets || []).find(t => String(t.id) === String(ticketId)) || getTickets()[0];

    const container = document.getElementById("ticketDetailContainer");
    if (!container) return;

    container.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 28px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 style="font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">${escapeHTML(ticket.title)}</h1>
                    <span style="font-size: 13px; color: #64748b;">Ticket ID: <strong>#${escapeHTML(ticket.id)}</strong></span>
                </div>
                <div style="display: flex; gap: 10px;">
                    <a href="${window.getExportUrl ? getExportUrl(ticket.id, 'pdf') : '#'}" target="_blank" style="padding: 8px 14px; background: #ef4444; color: white; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;"><i class="fa-solid fa-file-pdf"></i> Export PDF</a>
                    <a href="${window.getExportUrl ? getExportUrl(ticket.id, 'docx') : '#'}" target="_blank" style="padding: 8px 14px; background: #2563eb; color: white; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;"><i class="fa-solid fa-file-word"></i> Export DOCX</a>
                </div>
            </div>

            <div style="display: flex; gap: 16px; font-size: 13px; color: #475569; margin-bottom: 20px; flex-wrap: wrap; background: #f8fafc; padding: 12px 16px; border-radius: 8px;">
                <div><strong>Category:</strong> ${escapeHTML(ticket.category || ticket.department || "IT Support")}</div>
                <div><strong>Priority:</strong> <span class="badge priority-${(ticket.priority||'Medium').toLowerCase()}">${escapeHTML(ticket.priority || "Medium")}</span></div>
                <div><strong>Status:</strong> <span class="badge status-${(ticket.status||'Open').toLowerCase().replaceAll(' ','-')}">${escapeHTML(ticket.status || "Open")}</span></div>
                <div><strong>Date:</strong> ${escapeHTML(ticket.date || "Today")}</div>
            </div>

            <div style="font-size: 14px; color: #334155; line-height: 1.6; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                <strong>Issue Description:</strong>
                <p style="margin-top: 6px;">${escapeHTML(ticket.description || "No description provided.")}</p>
            </div>
        </div>

        <!-- Threaded Chat Section -->
        <div style="background: white; border-radius: 12px; padding: 28px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h2 style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 20px; display: flex; align-items: center; gap: 8px;"><i class="fa-regular fa-comments"></i> Support Conversation Thread</h2>
            <div id="ticketCommentsThread" style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; max-height: 400px; overflow-y: auto; padding-right: 8px;">
                <div style="text-align: center; color: #94a3b8; font-size: 13px;">Loading conversation...</div>
            </div>

            <div style="display: flex; gap: 12px;">
                <input type="text" id="replyMessageInput" placeholder="Type a message or response to support..." style="flex: 1; padding: 12px 16px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px;">
                <button type="button" onclick="sendTicketReply('${escapeHTML(ticket.id)}')" style="background: #4f46e5; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;"><i class="fa-solid fa-paper-plane"></i> Send</button>
            </div>
        </div>
    `;

    await renderTicketCommentsThread(ticketId);
}

async function renderTicketCommentsThread(ticketId) {
    const threadContainer = document.getElementById("ticketCommentsThread");
    if (!threadContainer) return;
    const getCommentsFn = window.apiGetComments || (async () => []);
    const comments = await getCommentsFn(ticketId);

    if (!comments || comments.length === 0) {
        threadContainer.innerHTML = `
            <div style="text-align: center; color: #64748b; font-size: 13px; padding: 24px; background: #f8fafc; border-radius: 8px;">
                No messages from support yet. Use the field below to send an update.
            </div>
        `;
        return;
    }

    threadContainer.innerHTML = comments.map(c => `
        <div style="background: ${c.sender_role === 'Employee' ? '#f0fdf4' : '#eef2ff'}; border-left: 4px solid ${c.sender_role === 'Employee' ? '#16a34a' : '#4f46e5'}; padding: 14px 18px; border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 6px;">
                <strong>${escapeHTML(c.sender_role || "Support")}</strong>
                <span>${escapeHTML(c.createdAt ? c.createdAt.substring(0, 16).replace("T", " ") : "Today")}</span>
            </div>
            <div style="font-size: 14px; color: #1e293b; line-height: 1.5;">${escapeHTML(c.message)}</div>
        </div>
    `).join("");

    threadContainer.scrollTop = threadContainer.scrollHeight;
}

async function submitStandardTicket(event) {
    if (event) event.preventDefault();

    const titleEl = document.getElementById("standardSubject") || document.getElementById("ticketTitle");
    const deptEl = document.getElementById("standardDepartment") || document.getElementById("ticketDepartment");
    const priorityEl = document.getElementById("ticketPriority");
    const descEl = document.getElementById("standardDescription") || document.getElementById("ticketDescription");

    const titleStr = titleEl ? titleEl.value.trim() : "";
    let descStr = descEl ? descEl.value.trim() : "";

    if (!titleStr) {
        showNotification("Please enter a title for your support request.", "error");
        return;
    }

    if (descStr.length < 10) {
        descStr = (descStr + " (Detailed support request submitted via employee portal)").trim();
    }

    const rawDept = deptEl ? deptEl.value : "Auto";
    const mappedDept = mapDepartmentName(rawDept);

    const payload = {
        title: titleStr.length < 3 ? titleStr + " (Ticket)" : titleStr,
        description: descStr,
        category: rawDept !== "Auto" ? rawDept : "IT Support",
        priority: priorityEl ? priorityEl.value : "Medium",
        department: mappedDept,
        requester_id: getCurrentRequesterId()
    };

    try {
        const createFn = window.apiCreateTicket || apiCreateTicket;
        const result = await createFn(payload);

        const existing = getTickets();
        const newTicket = result || {
            id: generateTicketId(),
            title: payload.title,
            department: mappedDept || "IT Team",
            category: payload.category,
            priority: payload.priority,
            description: payload.description,
            status: "Open",
            date: new Date().toISOString().split("T")[0],
            createdAt: new Date().toISOString()
        };
        existing.unshift(newTicket);
        saveTickets(existing);

        showNotification("Ticket submitted successfully!", "success");
        if (typeof showSuccessMessage === 'function') showSuccessMessage(newTicket);

        setTimeout(() => { window.location.href = "my-tickets.html"; }, 1200);
    } catch (err) {
        console.error("submitStandardTicket failed:", err);
        showNotification("Failed to submit ticket. Please check your connection.", "error");
    }
}

async function submitLeaveTicket(event) {
    if (event) event.preventDefault();
    const leaveForm = document.querySelector("#leaveTabContent form");
    const leaveType = leaveForm ? leaveForm.querySelector("select")?.value : "Paid Time Off (PTO)";
    const handover = leaveForm ? leaveForm.querySelectorAll("input[type='text']")[0]?.value : "";
    const startDate = leaveForm ? leaveForm.querySelectorAll("input[type='date']")[0]?.value : "";
    const endDate = leaveForm ? leaveForm.querySelectorAll("input[type='date']")[1]?.value : "";
    const notes = leaveForm ? leaveForm.querySelector("textarea")?.value : "";

    const payload = {
        title: `Leave Request: ${leaveType}`,
        department: "HR Team",
        category: "Time Off",
        priority: "Medium",
        description: `Leave Type: ${leaveType}\nStart Date: ${startDate || 'N/A'}\nEnd Date: ${endDate || 'N/A'}\nCoverage Lead: ${handover || 'N/A'}\nNotes: ${notes || 'Detailed PTO submission'}`,
        requester_id: getCurrentRequesterId()
    };

    try {
        const createFn = window.apiCreateTicket || apiCreateTicket;
        const result = await createFn(payload);

        const existing = getTickets();
        const newTicket = result || {
            id: generateTicketId(),
            title: payload.title,
            department: payload.department,
            category: payload.category,
            priority: payload.priority,
            description: payload.description,
            status: "Open",
            date: new Date().toISOString().split("T")[0],
            createdAt: new Date().toISOString()
        };
        existing.unshift(newTicket);
        saveTickets(existing);

        showNotification("Leave request submitted successfully!", "success");
        if (typeof showSuccessMessage === 'function') showSuccessMessage(newTicket);
        setTimeout(() => { window.location.href = "my-tickets.html"; }, 1200);
    } catch (err) {
        console.error("submitLeaveTicket failed:", err);
        showNotification("Failed to submit leave request.", "error");
    }
}

async function submitAnonymousTicket(event) {
    if (event) event.preventDefault();
    const anonForm = document.querySelector("#anonymousTabContent form");
    const category = anonForm ? anonForm.querySelector("select")?.value : "Confidential";
    const msg = anonForm ? anonForm.querySelector("textarea")?.value : "";

    const payload = {
        title: `Confidential Report: ${category}`,
        department: "Upper Management",
        category: category,
        priority: "High",
        description: (msg && msg.length >= 10) ? msg : (msg + " (Confidential anonymous workplace submission)").trim(),
        is_anonymous: true,
        requester_id: "anonymous@ticketgenie.com"
    };

    try {
        const createFn = window.apiCreateTicket || apiCreateTicket;
        const result = await createFn(payload);

        const existing = getTickets();
        const newTicket = result || {
            id: generateTicketId(),
            title: payload.title,
            department: payload.department,
            category: payload.category,
            priority: payload.priority,
            description: payload.description,
            status: "Open",
            date: new Date().toISOString().split("T")[0],
            createdAt: new Date().toISOString()
        };
        existing.unshift(newTicket);
        saveTickets(existing);

        showNotification("Anonymous report submitted confidentially!", "success");
        if (typeof showSuccessMessage === 'function') showSuccessMessage(newTicket);
        setTimeout(() => { window.location.href = "my-tickets.html"; }, 1200);
    } catch (err) {
        console.error("submitAnonymousTicket failed:", err);
        showNotification("Failed to submit confidential report.", "error");
    }
}

async function sendTicketReply(ticketId) {
    const replyInput = document.getElementById("replyMessageInput");
    if (!replyInput) return;
    const msg = replyInput.value.trim();
    if (!msg) return;

    replyInput.value = "";
    const postFn = window.apiPostComment || apiPostComment;
    await postFn(ticketId, msg, "Employee");
    await renderTicketCommentsThread(ticketId);
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("myTicketsList")) {
        initializeMyTickets();
    }
    if (document.querySelector(".table-container table tbody")) {
        loadDashboardTickets();
    }
    if (document.getElementById("ticketDetailContainer")) {
        loadTicketDetailPage();
    }
});

Object.assign(window, {
    STORAGE_KEY,
    getTickets,
    saveTickets,
    generateTicketId,
    getCurrentRequesterId,
    loadDashboardTickets,
    initializeMyTickets,
    renderMyTickets,
    loadTicketDetailPage,
    submitStandardTicket,
    submitLeaveTicket,
    submitAnonymousTicket,
    sendTicketReply
});
