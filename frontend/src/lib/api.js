const API_BASE_URL = "/api";

function getAuthHeaders() {
  let idToken = "";
  try {
    const stored = sessionStorage.getItem("portalUser") || sessionStorage.getItem("azureUser");
    if (stored) {
      const parsed = JSON.parse(stored);
      idToken = parsed.idToken || parsed.id_token || "";
    }
  } catch (e) {}

  const headers = { "Content-Type": "application/json" };
  if (idToken) {
    headers["Authorization"] = `Bearer ${idToken}`;
  }
  return headers;
}

/** ==================== TICKETS API ==================== */

export async function apiFetchTickets(params = {}) {
  try {
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.status && params.status !== "all") query.append("status", params.status);
    if (params.priority && params.priority !== "all") query.append("priority", params.priority);
    if (params.department) query.append("department", params.department);
    if (params.adminView) query.append("admin_view", "true");

    const res = await fetch(`${API_BASE_URL}/tickets?${query.toString()}`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data)) return data;
    }
  } catch (err) {
    console.warn("apiFetchTickets failed:", err);
  }
  return [];
}

export async function apiCreateTicket(payload) {
  const res = await fetch(`${API_BASE_URL}/tickets`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    let detail = `Ticket creation failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch (e) {}
    throw new Error(detail);
  }
  return await res.json();
}

export async function apiUpdateTicket(ticketId, updateData) {
  const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  if (!res.ok) {
    throw new Error(`Failed to update ticket (${res.status})`);
  }
  return await res.json();
}

export async function apiDeleteTicket(ticketId) {
  const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}`, {
    method: "DELETE",
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error(`Failed to delete ticket (${res.status})`);
  return await res.json();
}

export async function apiFetchComments(ticketId) {
  try {
    const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}/comments`, {
      headers: getAuthHeaders()
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("apiFetchComments failed:", err);
  }
  return [];
}

export async function apiPostComment(ticketId, message) {
  const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}/comments`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error("Failed to post comment");
  return await res.json();
}

/** ==================== EXPORT & CALENDAR API ==================== */

export async function apiExportTicketPDF(ticketId) {
  if (!ticketId) return;
  try {
    const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}/export?format=pdf`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`Failed to export PDF (${res.status})`);
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `Ticket_${ticketId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);
  } catch (err) {
    console.error("apiExportTicketPDF error:", err);
    alert(err.message || "Failed to download PDF.");
  }
}

export async function apiExportTicketDOCX(ticketId) {
  if (!ticketId) return;
  try {
    const res = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}/export?format=docx`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`Failed to export DOCX (${res.status})`);
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `Ticket_${ticketId}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);
  } catch (err) {
    console.error("apiExportTicketDOCX error:", err);
    alert(err.message || "Failed to download DOCX.");
  }
}

export async function apiExportCalendar() {
  try {
    const res = await fetch(`${API_BASE_URL}/calendar/export.ics`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`Failed to export calendar (${res.status})`);
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = "TicketGenie_Leave_Calendar.ics";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);
  } catch (err) {
    console.error("apiExportCalendar error:", err);
    alert(err.message || "Failed to download iCal calendar.");
  }
}

/** ==================== KNOWLEDGE BASE API ==================== */

export async function apiSearchKB(queryStr) {
  try {
    const res = await fetch(`/api/knowledge/search?q=${encodeURIComponent(queryStr)}`, {
      headers: getAuthHeaders()
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("apiSearchKB failed:", err);
  }
  return { query: queryStr, answer: "No matching knowledge base policy found.", verified: false };
}

export async function apiIngestPolicy(policyPayload) {
  const res = await fetch("/api/knowledge/ingest", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(policyPayload)
  });
  if (!res.ok) throw new Error(`Policy ingestion failed (${res.status})`);
  return await res.json();
}

/** ==================== ADMIN & RBAC API ==================== */

export async function apiFetchDepartments() {
  try {
    const res = await fetch("/api/admin/departments", { headers: getAuthHeaders() });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("apiFetchDepartments failed:", err);
  }
  return [];
}

export async function apiFetchDepartmentUsers(departmentName = null) {
  try {
    const query = departmentName ? `?department_name=${encodeURIComponent(departmentName)}` : "";
    const res = await fetch(`/api/admin/departments/users${query}`, { headers: getAuthHeaders() });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("apiFetchDepartmentUsers failed:", err);
  }
  return [];
}

export async function apiAssignDepartmentUser(payload) {
  const res = await fetch("/api/admin/departments/users", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Role assignment failed (${res.status})`);
  return await res.json();
}

export async function apiRemoveDepartmentUser(departmentName, azureObjectId) {
  const res = await fetch(`/api/admin/departments/users?department_name=${encodeURIComponent(departmentName)}&azure_object_id=${encodeURIComponent(azureObjectId)}`, {
    method: "DELETE",
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error(`Failed to remove department user mapping (${res.status})`);
  return await res.json();
}

export async function apiCreateDepartment(name, queueName, description = "") {
  const res = await fetch("/api/admin/departments", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ name, queue_name: queueName, description })
  });
  if (!res.ok) throw new Error(`Department creation failed (${res.status})`);
  return await res.json();
}

/** ==================== AI GENIE AGENT API ==================== */

export async function apiGenieChat(message, state = {}) {
  try {
    const payload = {
      message,
      role: state.role || "Employee",
      history: state.history || [],
      draft: state.draft || null,
      active_intent: state.active_intent || state.activeIntent || null,
      active_request_type: state.active_request_type || state.activeRequestType || null
    };

    const res = await fetch("/api/chatbot/message", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      return {
        reply: data.message || "I am Genie, your AI helpdesk assistant.",
        message: data.message || "I am Genie, your AI helpdesk assistant.",
        suggestions: data.suggestions || ["Ask a question", "Help me create a ticket", "Check my ticket status"],
        action: data.action || null,
        ticket_draft: data.ticket_draft || null,
        request_type: data.request_type || null,
        missing_fields: data.missing_fields || [],
        ready_for_review: data.ready_for_review || false,
        intent: data.intent || null
      };
    }
  } catch (e) {
    console.warn("api/chatbot/message call error, falling back to /api/genie/chat:", e);
  }

  try {
    const res = await fetch("/api/genie/chat", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ message })
    });
    if (res.ok) {
      const data = await res.json();
      return {
        reply: data.reply || data.message || "I am Genie, your AI helpdesk assistant.",
        message: data.reply || data.message || "I am Genie, your AI helpdesk assistant.",
        suggestions: data.suggestions || ["Check my tickets", "IT Help"],
        action: data.action || null,
        ticket_draft: data.ticket_draft || null,
        request_type: data.request_type || null,
        missing_fields: data.missing_fields || [],
        ready_for_review: data.ready_for_review || false,
        intent: data.intent || null
      };
    }
  } catch (err) {
    console.error("apiGenieChat fallback failed:", err);
  }

  return {
    reply: "I am Genie, your AI support agent. I can assist you with ticket status, IT troubleshooting, and corporate policies.",
    message: "I am Genie, your AI support agent. I can assist you with ticket status, IT troubleshooting, and corporate policies.",
    suggestions: ["Check my tickets", "IT Help", "Time Off Policy"],
    action: null,
    ticket_draft: null,
    request_type: null,
    missing_fields: [],
    ready_for_review: false,
    intent: null
  };
}

/** ==================== USER PROFILE & ANNOUNCEMENTS ==================== */

export async function apiFetchAnnouncements() {
  try {
    const res = await fetch(`${API_BASE_URL}/announcements`, { headers: getAuthHeaders() });
    if (res.ok) return await res.json();
  } catch (err) {
    console.error("apiFetchAnnouncements failed:", err);
  }
  return [];
}

export async function apiCreateAnnouncement(payload) {
  const res = await fetch(`${API_BASE_URL}/announcements`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    let detail = `Unable to create announcement (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch (e) {}
    throw new Error(detail);
  }
  return await res.json();
}

export async function apiCheckAnnouncementMatch(title, description = "") {
  const res = await fetch(`${API_BASE_URL}/announcements/match`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ title, description })
  });
  if (!res.ok) throw new Error(`Announcement check failed (${res.status})`);
  return await res.json();
}

export async function apiFetchUserProfile() {
  try {
    const res = await fetch(`${API_BASE_URL}/users/profile`, { headers: getAuthHeaders() });
    if (res.ok) return await res.json();
  } catch (err) {
    console.error("apiFetchUserProfile failed:", err);
  }
  return { name: "User", email: "user@ticketgenie.com", role: "Employee", department: "Operations" };
}
