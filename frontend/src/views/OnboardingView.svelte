<script>
  let candidates = [
    { id: 'ONB-101', name: 'Aarav Sharma', role: 'Senior Software Engineer', dept: 'IT Engineering', status: 'Completed', startDate: '2026-09-01', visa: 'H-1B Active' },
    { id: 'ONB-102', name: 'Elena Rostova', role: 'Product Designer', dept: 'UX Design', status: 'In Progress', startDate: '2026-09-15', visa: 'OPT STEM' },
    { id: 'ONB-103', name: 'Marcus Vance', role: 'Data Analyst', dept: 'HR Analytics', status: 'Pending Documents', startDate: '2026-10-01', visa: 'TN Visa' }
  ];
</script>

<div class="onboarding-view animate-fade">
  <div class="view-header">
    <div>
      <h1 class="view-title"><i class="ph-bold ph-user-plus"></i> Executive Onboarding Pipeline</h1>
      <p class="view-subtitle">Track new hires, visa authorizations, IT hardware provisioning, and HR credentials</p>
    </div>
  </div>

  <div class="card-box">
    <table class="data-table">
      <thead>
        <tr>
          <th>Pipeline ID</th>
          <th>Candidate Name</th>
          <th>Target Role</th>
          <th>Department</th>
          <th>Visa / Work Auth</th>
          <th>Start Date</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {#each candidates as item}
          <tr>
            <td class="id-cell">{item.id}</td>
            <td><strong>{item.name}</strong></td>
            <td>{item.role}</td>
            <td>{item.dept}</td>
            <td><span class="visa-badge">{item.visa}</span></td>
            <td class="date-cell">{item.startDate}</td>
            <td>
              <span class="badge" class:completed={item.status === 'Completed'} class:progress={item.status === 'In Progress'} class:pending={item.status === 'Pending Documents'}>
                {item.status}
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .onboarding-view {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    overflow-y: auto;
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

  .card-box {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 24px;
    box-shadow: var(--shadow-sm);
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }

  .data-table th, .data-table td {
    padding: 14px;
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

  .visa-badge {
    background: #f1f5f9;
    color: #475569;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
  }

  .badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .badge.completed { background: #d1fae5; color: #047857; }
  .badge.progress { background: #dbeafe; color: #1e40af; }
  .badge.pending { background: #fef3c7; color: #b45309; }
</style>
