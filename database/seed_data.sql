-- ==========================================================
-- TicketGenie Initial Seed Data (SQL)
-- ==========================================================

-- Seed Initial Admin in Department Users
INSERT OR REPLACE INTO department_users (id, department_name, azure_object_id, role, user_email, createdAt)
VALUES (
    'uobj-admin-dc3b56e9',
    'IT',
    'dc3b56e9-9280-40dc-8d73-98bfd81fdd6a',
    'Super Admin',
    'Admin1@vigneshquadrantoutlook.onmicrosoft.com',
    '2026-08-16T12:00:00'
);

-- Seed Initial Admin in User Profiles
INSERT OR REPLACE INTO user_profiles (id, name, email, role, department, phone, avatar)
VALUES (
    'usr-admin-dc3b56e9',
    'Greg Davis',
    'Admin1@vigneshquadrantoutlook.onmicrosoft.com',
    'Super Admin',
    'IT',
    '+1 (555) 019-9999',
    'GD'
);

-- Seed Initial Ticket Created by User (usr-admin-dc3b56e9 / dc3b56e9-9280-40dc-8d73-98bfd81fdd6a)
INSERT OR REPLACE INTO tickets (id, title, department, category, priority, status, description, date, createdAt, is_anonymous, auto_resolved, requester_id, classification_status, classification_confidence, classification_reason, needs_human_review, model_deployment)
VALUES (
    'HD-2001',
    'VPN Connection Issue for Admin User',
    'IT Team',
    'IT Support',
    'High',
    'Open',
    'Unable to connect to internal VPN network from remote office.',
    '2026-08-16',
    '2026-08-16T23:06:00',
    0,
    0,
    'usr-admin-dc3b56e9',
    'Classified',
    '0.95',
    'IT Support request regarding VPN',
    0,
    'gpt-5.2'
);

-- Seed Initial Ticket Created by Another User (other-employee-7890)
INSERT OR REPLACE INTO tickets (id, title, department, category, priority, status, description, date, createdAt, is_anonymous, auto_resolved, requester_id, classification_status, classification_confidence, classification_reason, needs_human_review, model_deployment)
VALUES (
    'HD-2002',
    'Payroll Discrepancy Inquiry',
    'HR Team',
    'Payroll',
    'Medium',
    'Open',
    'Overtime pay was not reflected on recent paystub.',
    '2026-08-16',
    '2026-08-16T23:06:30',
    0,
    0,
    'other-employee-7890',
    'Classified',
    '0.90',
    'HR Payroll request',
    0,
    'gpt-5.2'
);
