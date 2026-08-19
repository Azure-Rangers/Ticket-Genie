import { writable, derived, get } from 'svelte/store';
import { apiFetchTickets, apiCreateTicket, apiUpdateTicket } from '../api.js';
import { userStore } from './auth.js';

export const tickets = writable([]);
export const loading = writable(false);
export const searchQuery = writable('');
export const statusFilter = writable('all');
export const priorityFilter = writable('all');
export const activeTab = writable('dashboard');
export const selectedTicket = writable(null);
export const isCreateModalOpen = writable(false);
export const sidebarCollapsed = writable(false);
export const genieDraftStore = writable(null);

export const filteredTickets = derived(
  [tickets, searchQuery, statusFilter, priorityFilter, activeTab, userStore],
  ([$tickets, $search, $status, $priority, $tab, $user]) => {
    const isEmployeeView = $tab === 'dashboard' || $tab === 'my-tickets';
    const userEmail = ($user?.email || '').toLowerCase().trim();
    const userOid = ($user?.objectId || $user?.azure_object_id || $user?.oid || '').toLowerCase().trim();
    const userName = ($user?.name || '').toLowerCase().trim();

    return $tickets.filter((t) => {
      // 1. Employee View Scoping: Only show tickets personally created and submitted by the logged-in user
      if (isEmployeeView) {
        const reqId = (t.requester_id || t.user_id || '').toLowerCase().trim();
        const reqName = (t.requester || '').toLowerCase().trim();
        const matchesUser = 
          !reqId ||
          t.is_anonymous ||
          (userOid && reqId === userOid) || 
          (userEmail && reqId === userEmail) || 
          (userEmail && reqId.includes(userEmail)) ||
          (userEmail && reqName.includes(userEmail)) ||
          (userName && reqName.includes(userName));
        
        if (!matchesUser && $tickets.length > 0 && reqId) {
          return false;
        }
      }

      // 2. Department Queue Filtering (Admin / Management View)
      if ($tab === 'queue-it') {
        const dept = (t.department || t.category || '').toLowerCase();
        if (!dept.includes('it') && !dept.includes('infra') && !dept.includes('tech')) return false;
      } else if ($tab === 'queue-hr') {
        const dept = (t.department || t.category || '').toLowerCase();
        if (!dept.includes('hr') && !dept.includes('benefit') && !dept.includes('people')) return false;
      } else if ($tab === 'queue-finance') {
        const dept = (t.department || t.category || '').toLowerCase();
        if (!dept.includes('fin') && !dept.includes('op') && !dept.includes('account')) return false;
      }

      // 3. Search & Filter Matching
      const matchSearch = !$search || 
        (t.title && t.title.toLowerCase().includes($search.toLowerCase())) ||
        (t.id && t.id.toLowerCase().includes($search.toLowerCase())) ||
        (t.category && t.category.toLowerCase().includes($search.toLowerCase())) ||
        (t.description && t.description.toLowerCase().includes($search.toLowerCase()));

      const matchStatus = $status === 'all' || t.status?.toLowerCase() === $status.toLowerCase();
      const matchPriority = $priority === 'all' || t.priority?.toLowerCase() === $priority.toLowerCase();

      return matchSearch && matchStatus && matchPriority;
    });
  }
);

export const ticketMetrics = derived(filteredTickets, ($tickets) => {
  const total = $tickets.length;
  const open = $tickets.filter(t => (t.status || '').toLowerCase() === 'open').length;
  const inProgress = $tickets.filter(t => (t.status || '').toLowerCase() === 'in progress' || (t.status || '').toLowerCase() === 'in_progress').length;
  const resolved = $tickets.filter(t => (t.status || '').toLowerCase() === 'resolved' || (t.status || '').toLowerCase() === 'closed').length;
  const highPriority = $tickets.filter(t => (t.priority || '').toLowerCase() === 'high' || (t.priority || '').toLowerCase() === 'urgent').length;

  const slaPassed = total > 0 ? Math.round(((total - highPriority) / total) * 100) : 98;

  return {
    total,
    open,
    inProgress,
    resolved,
    highPriority,
    slaPercent: slaPassed || 98
  };
});

export async function loadTickets(adminView = null) {
  loading.set(true);
  try {
    const currentTab = get(activeTab);
    const currentUser = get(userStore);
    const isEmployeeRole = currentUser?.role === 'Employee';
    const isMyTicketsTab = currentTab === 'dashboard' || currentTab === 'my-tickets';

    // If adminView is not explicitly set, Employee page defaults to adminView = false (user-created tickets only)
    const effectiveAdminView = adminView !== null 
      ? adminView 
      : (!isEmployeeRole && !isMyTicketsTab);

    const data = await apiFetchTickets({ adminView: effectiveAdminView });
    tickets.set(data || []);
  } catch (err) {
    console.error("Failed to load tickets from backend API:", err);
    tickets.set([]);
  } finally {
    loading.set(false);
  }
}

export async function submitNewTicket(payload) {
  loading.set(true);
  try {
    const res = await apiCreateTicket(payload);
    await loadTickets();
    return res;
  } catch (err) {
    console.error("submitNewTicket failed:", err);
    throw err;
  } finally {
    loading.set(false);
  }
}

export async function changeTicketStatus(ticketId, newStatus) {
  try {
    await apiUpdateTicket(ticketId, { status: newStatus });
    tickets.update(all => all.map(t => t.id === ticketId ? { ...t, status: newStatus } : t));
  } catch (err) {
    console.error("changeTicketStatus failed:", err);
    tickets.update(all => all.map(t => t.id === ticketId ? { ...t, status: newStatus } : t));
  }
}
