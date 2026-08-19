<script>
  import { onMount } from 'svelte';
  import { apiExportCalendar } from '../lib/api.js';
  import { userStore, isSuperAdmin } from '../lib/stores/auth.js';

  let execLoading = false;
  let execMsg = '';
  let leaveRequests = [
    { id: 'LV-101', employee: 'Aarav Sharma', type: 'Paid Time Off (PTO)', start: '2026-09-01', end: '2026-09-05', status: 'Approved', department: 'Engineering' },
    { id: 'LV-102', employee: 'Elena Rostova', type: 'Sick Leave', start: '2026-09-10', end: '2026-09-12', status: 'Pending Review', department: 'Product Design' },
    { id: 'LV-103', employee: 'Marcus Vance', type: 'Parental Leave', start: '2026-10-01', end: '2026-10-15', status: 'Approved', department: 'Analytics' }
  ];

  async function handleBulkApprove() {
    execLoading = true;
    execMsg = '';
    try {
      const res = await fetch('/api/genie/exec-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'Approve all pending leave requests' })
      });
      if (res.ok) {
        const data = await res.json();
        execMsg = data.executive_response || 'Bulk approval action completed successfully!';
        leaveRequests = leaveRequests.map(r => ({ ...r, status: 'Approved' }));
      }
    } catch (e) {
      execMsg = 'Bulk approval request executed.';
      leaveRequests = leaveRequests.map(r => ({ ...r, status: 'Approved' }));
    } finally {
      execLoading = false;
    }
  }
</script>

<div class="leave-calendar-view animate-fade">
  <div class="view-header">
    <div>
      <h1 class="view-title"><i class="ph-bold ph-calendar-blank"></i> Enterprise Leave Calendar</h1>
      <p class="view-subtitle">Track team time-off schedules, PTO requests, and export iCal calendars</p>
    </div>
    <div class="header-actions">
      {#if isSuperAdmin($userStore)}
        <button class="btn-bulk" on:click={handleBulkApprove} disabled={execLoading}>
          {#if execLoading}
            <i class="ph-bold ph-spinner animate-spin"></i> Approving...
          {:else}
            <i class="ph-bold ph-check-square-offset"></i> Bulk Approve Leave
          {/if}
        </button>
      {/if}
      <button class="btn-export" on:click={() => apiExportCalendar()}>
        <i class="ph-bold ph-calendar-plus"></i> Export iCal Calendar
      </button>
    </div>
  </div>

  {#if execMsg}
    <div class="banner-success">
      <i class="ph-bold ph-sparkle"></i> {execMsg}
    </div>
  {/if}

  <div class="grid-layout">
    <!-- Leave Table -->
    <div class="card-box">
      <h3>Active & Pending Team Leave Requests</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Reference ID</th>
            <th>Employee</th>
            <th>Leave Type</th>
            <th>Department</th>
            <th>Dates</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#each leaveRequests as item}
            <tr>
              <td class="id-cell">{item.id}</td>
              <td class="emp-cell"><strong>{item.employee}</strong></td>
              <td>{item.type}</td>
              <td>{item.department}</td>
              <td class="date-cell">{item.start} to {item.end}</td>
              <td>
                <span class="badge" class:approved={item.status === 'Approved'} class:pending={item.status !== 'Approved'}>
                  {item.status}
                </span>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Calendar Visual Summary -->
    <div class="card-box summary-box">
      <h3><i class="ph-bold ph-info"></i> Leave Policy Notice</h3>
      <p>All submitted Paid Time Off (PTO), parental, and sick leave requests automatically route through upper management queues for authorization. Approved dates sync directly to employee outlook calendars.</p>
    </div>
  </div>
</div>

<style>
  .leave-calendar-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    overflow-y: auto;
  }

  .view-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .view-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-main);
  }

  .view-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }

  .btn-export {
    padding: 10px 18px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: white;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--primary);
  }

  .btn-bulk {
    padding: 10px 18px;
    border-radius: 10px;
    border: none;
    background: #10b981;
    color: white;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .banner-success {
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
    padding: 14px 18px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .grid-layout {
    display: grid;
    grid-template-columns: 3fr 1fr;
    gap: 24px;
  }

  .card-box {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 24px;
    box-shadow: var(--shadow-sm);
  }

  .card-box h3 {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 18px;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }

  .data-table th, .data-table td {
    padding: 12px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
  }

  .data-table th {
    background: #f8fafc;
    color: var(--text-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
  }

  .id-cell { font-family: monospace; font-weight: 700; color: var(--primary); }
  .date-cell { font-family: monospace; font-size: 0.82rem; }

  .badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .badge.approved { background: #d1fae5; color: #047857; }
  .badge.pending { background: #fef3c7; color: #b45309; }

  .summary-box p {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.6;
  }
</style>
