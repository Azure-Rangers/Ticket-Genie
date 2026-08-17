/* =========================================================
   TICKETGENIE REST API CLIENT MODULE
   Shared API bindings for Admin, Management, and Employee Portals
   ========================================================= */

const API_BASE_URL = window.API_BASE_URL || "/api";

async function apiFetchTickets(params = {}) {
    try {
        const query = new URLSearchParams();
        if (params.search) query.append("search", params.search);
        if (params.status && params.status !== "all") query.append("status", params.status);
        if (params.priority && params.priority !== "all") query.append("priority", params.priority);
        if (params.requesterId) query.append("requester_id", params.requesterId);

        const res = await fetch(`${API_BASE_URL}/tickets?${query.toString()}`);
        if (!res.ok) throw new Error("API request failed");
        return await res.json();
    } catch (err) {
        console.warn("apiFetchTickets failed, using fallback:", err);
        return null;
    }
}

async function apiCreateTicket(ticketPayload) {
    const res = await fetch(`${API_BASE_URL}/tickets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ticketPayload)
    });

    if (!res.ok) {
        let detail = `Ticket creation failed (HTTP ${res.status})`;
        try {
            const body = await res.json();
            if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
        } catch (e) {}
        throw new Error(detail);
    }

    return await res.json();
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
        console.error("apiUpdateTicket failed:", err);
    }
    return null;
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
        console.error("apiPostComment failed:", err);
        return null;
    }
}

async function apiFetchAnnouncements() {
    try {
        const res = await fetch(`${API_BASE_URL}/announcements`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("apiFetchAnnouncements failed:", err);
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
        console.error("apiCreateAnnouncement failed:", err);
    }
    return null;
}

async function apiDeleteAnnouncement(ancId) {
    try {
        const res = await fetch(`${API_BASE_URL}/announcements/${ancId}`, { method: "DELETE" });
        return res.ok;
    } catch (err) {
        console.error("apiDeleteAnnouncement failed:", err);
    }
    return false;
}

async function apiFetchNotifications() {
    try {
        const res = await fetch(`${API_BASE_URL}/notifications`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("apiFetchNotifications failed:", err);
    }
    return [];
}

async function apiMarkNotificationRead(notifId) {
    try {
        const res = await fetch(`${API_BASE_URL}/notifications/${notifId}/read`, { method: "PUT" });
        return res.ok;
    } catch (err) {
        console.error("apiMarkNotificationRead failed:", err);
    }
    return false;
}

async function apiFetchOnboarding() {
    try {
        const res = await fetch(`${API_BASE_URL}/onboarding`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("apiFetchOnboarding failed:", err);
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
        console.error("apiCreateOnboarding failed:", err);
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
        console.error("apiUpdateOnboardingStatus failed:", err);
    }
    return null;
}

async function apiFetchUserProfile() {
    try {
        const res = await fetch(`${API_BASE_URL}/users/profile`);
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("apiFetchUserProfile failed:", err);
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
        console.error("apiUpdateUserProfile failed:", err);
    }
    return null;
}

async function apiGenieChat(message) {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        if (res.ok) return await res.json();
    } catch (err) {
        console.error("apiGenieChat failed:", err);
    }
    return { reply: "I'm having trouble connecting to the backend right now. Please try again shortly.", suggestions: ["Check my tickets"] };
}

async function apiRunReAct(message, role = "Super Admin") {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/react`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, role }),
        });
        return await res.json();
    } catch (err) {
        console.error("apiRunReAct failed:", err);
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
        console.error("apiRunExecAction failed:", err);
        return { executive_response: "Executive command execution failed." };
    }
}

function getExportUrl(ticketId, format = "pdf") {
    return `${API_BASE_URL}/tickets/${ticketId}/export?format=${format}`;
}

// Bind API client functions globally to window
Object.assign(window, {
    API_BASE_URL,
    apiFetchTickets,
    apiCreateTicket,
    apiUpdateTicket,
    apiGetComments,
    apiPostComment,
    apiFetchAnnouncements,
    apiCreateAnnouncement,
    apiDeleteAnnouncement,
    apiFetchNotifications,
    apiMarkNotificationRead,
    apiFetchOnboarding,
    apiCreateOnboarding,
    apiUpdateOnboardingStatus,
    apiFetchUserProfile,
    apiUpdateUserProfile,
    apiGenieChat,
    apiRunReAct,
    apiRunExecAction,
    getExportUrl
});
